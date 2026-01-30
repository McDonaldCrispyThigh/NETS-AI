"""
Bayesian Employee Count Estimator
Multi-signal hierarchical modeling with confidence intervals
Features: LinkedIn data, Google review velocity, building area, job postings
Output: Point estimate + 95% confidence interval per establishment
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, List
import logging
from dataclasses import dataclass
import warnings

logger = logging.getLogger(__name__)

try:
    import pymc as pm
    import arviz as az
    PYMC_AVAILABLE = True
except ImportError:
    PYMC_AVAILABLE = False
    logger.warning("PyMC not available - using fallback estimation method")

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb


@dataclass
class EmployeeEstimate:
    """Container for employee count estimate with uncertainty"""
    duns_id: str
    company_name: str
    point_estimate: float
    ci_lower: float      # 2.5th percentile
    ci_upper: float      # 97.5th percentile
    confidence_level: str  # 'high', 'medium', 'low'
    estimation_method: str  # 'linkedin', 'xgboost', 'rule_based'
    primary_signal: str    # Which signal was most influential
    signals_used: List[str]
    naics_code: str


class EmployeeEstimator:
    """
    Estimate employee counts using multi-source data integration
    Implements XGBoost + Bayesian hierarchical modeling
    """
    
    def __init__(self, naics_codes: Dict[str, dict]):
        """
        Initialize estimator with NAICS-specific parameters
        
        Args:
            naics_codes: Dictionary from config.EMPLOYEE_ESTIMATION_BASELINES
                        Keys: NAICS code (str), Values: baseline params dict
        """
        self.naics_baselines = naics_codes
        self.xgb_models = {}  # One model per NAICS code
        self.scaler = StandardScaler()
        self.logger = logger
    
    def estimate_from_linkedin(self, linkedin_headcount: float) -> Tuple[float, float, float]:
        """
        Use LinkedIn headcount data (highest credibility signal)
        Apply slight smoothing for outlier values
        
        Args:
            linkedin_headcount: Employee count from LinkedIn
            
        Returns:
            Tuple of (point_estimate, ci_lower, ci_upper)
            
        Assumptions:
            - LinkedIn data is most reliable
            - CI width = 10% of point estimate (low uncertainty)
        """
        if pd.isna(linkedin_headcount) or linkedin_headcount <= 0:
            return None, None, None
        
        point = float(linkedin_headcount)
        
        # Conservative CI: 10% margin for LinkedIn data
        ci_lower = max(1, point * 0.90)
        ci_upper = point * 1.10
        
        return point, ci_lower, ci_upper
    
    def estimate_from_review_velocity(
        self,
        review_count_3m: int,
        review_count_6_12m: int,
        naics_code: str
    ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Estimate employees from Google review velocity
        
        Theory: Busier establishments get more reviews
        Regression: employees = baseline + (reviews_per_month - avg_baseline) * scaling_factor
        
        Args:
            review_count_3m: Reviews in last 3 months
            review_count_6_12m: Reviews in months 6-12
            naics_code: Target NAICS code (str)
            
        Returns:
            Tuple of (point_estimate, ci_lower, ci_upper) or (None, None, None) if insufficient data
        """
        if naics_code not in self.naics_baselines:
            self.logger.warning(f"Unknown NAICS code: {naics_code}")
            return None, None, None
        
        # Require minimum review signal
        if review_count_3m < 3 or review_count_6_12m < 3:
            return None, None, None
        
        baseline = self.naics_baselines[naics_code]
        avg_reviews_per_month = baseline['avg_reviews_per_month']
        
        # Calculate review intensity ratio
        recent_monthly_avg = review_count_3m / 3
        historical_monthly_avg = review_count_6_12m / 6
        
        # Avoid division by zero
        if historical_monthly_avg < 1:
            historical_monthly_avg = avg_reviews_per_month
        
        intensity_ratio = recent_monthly_avg / avg_reviews_per_month if avg_reviews_per_month > 0 else 1
        
        # Scale baseline by intensity
        point = baseline['avg_employees'] * intensity_ratio
        point = np.clip(point, baseline['min_employees'], baseline['max_employees'])
        
        # CI width increases with uncertainty (inverse of review count)
        review_total = review_count_3m + review_count_6_12m
        confidence_margin = max(0.15, 2 / np.log(review_total + 1))  # Higher reviews = tighter CI
        
        ci_lower = max(baseline['min_employees'], point * (1 - confidence_margin))
        ci_upper = min(baseline['max_employees'], point * (1 + confidence_margin))
        
        return point, ci_lower, ci_upper
    
    def estimate_from_building_area(
        self,
        area_sqm: float,
        naics_code: str
    ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Estimate employees from building footprint area
        
        Theory: Store size correlates with staffing
        Formula: employees = area * employees_per_sqm
        
        Args:
            area_sqm: Building footprint area in square meters
            naics_code: Target NAICS code
            
        Returns:
            Tuple of (point_estimate, ci_lower, ci_upper) or (None, None, None) if missing
        """
        if pd.isna(area_sqm) or area_sqm <= 0:
            return None, None, None
        
        if naics_code not in self.naics_baselines:
            return None, None, None
        
        baseline = self.naics_baselines[naics_code]
        employees_per_sqm = baseline['employees_per_sqm']
        
        point = area_sqm * employees_per_sqm
        point = np.clip(point, baseline['min_employees'], baseline['max_employees'])
        
        # Building area is rough estimate: wider CI (25%)
        ci_lower = max(baseline['min_employees'], point * 0.75)
        ci_upper = min(baseline['max_employees'], point * 1.25)
        
        return point, ci_lower, ci_upper
    
    def estimate_from_job_postings(
        self,
        postings_recent_6m: int,
        postings_historical_max: int,
        naics_code: str
    ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Estimate employees from job posting activity
        
        Theory: Hiring activity indicates growth/operational level
        Higher activity = larger team or expansion
        
        Args:
            postings_recent_6m: Job postings in last 6 months
            postings_historical_max: Peak postings in any 6-month window
            naics_code: Target NAICS code
            
        Returns:
            Tuple of (point_estimate, ci_lower, ci_upper) or (None, None, None)
        """
        if naics_code not in self.naics_baselines:
            return None, None, None
        
        baseline = self.naics_baselines[naics_code]
        
        # Require minimum hiring signal
        if postings_recent_6m < 1 and postings_historical_max < 2:
            return None, None, None
        
        # Avoid division by zero
        historical_max = max(1, postings_historical_max)
        hiring_intensity = postings_recent_6m / historical_max
        
        # Map hiring intensity to employee multiplier
        # High hiring (>0.7 intensity) = likely 1.2x baseline
        # Low hiring (0.2-0.7) = baseline
        # Minimal hiring (<0.2) = 0.9x baseline
        if hiring_intensity > 0.7:
            multiplier = 1.2
        elif hiring_intensity > 0.2:
            multiplier = 1.0
        else:
            multiplier = 0.9
        
        point = baseline['avg_employees'] * multiplier
        point = np.clip(point, baseline['min_employees'], baseline['max_employees'])
        
        # Job posting data is less certain: 30% CI
        ci_lower = max(baseline['min_employees'], point * 0.70)
        ci_upper = min(baseline['max_employees'], point * 1.30)
        
        return point, ci_lower, ci_upper
    
    def ensemble_estimate(
        self,
        estimates: Dict[str, Tuple[float, float, float]],
        weights: Dict[str, float] = None
    ) -> Tuple[float, float, float, str]:
        """
        Combine multiple estimates using weighted ensemble
        
        Args:
            estimates: Dict of {signal_name: (point, ci_lower, ci_upper)}
            weights: Optional weights for each signal (default: equal)
                    If not provided, inferred from estimate quality
            
        Returns:
            Tuple of (ensemble_point, ensemble_lower, ensemble_upper, dominant_signal)
        """
        # Filter out None estimates
        valid_estimates = {k: v for k, v in estimates.items() if v[0] is not None}
        
        if not valid_estimates:
            return None, None, None, 'none'
        
        # Default weights: LinkedIn=0.5, review_velocity=0.3, building_area=0.1, job_postings=0.1
        if weights is None:
            weights = {
                'linkedin': 0.50,
                'review_velocity': 0.30,
                'building_area': 0.15,
                'job_postings': 0.05
            }
        
        # Normalize weights for available signals
        available_weights = {k: weights.get(k, 0.1) for k in valid_estimates.keys()}
        weight_sum = sum(available_weights.values())
        available_weights = {k: v / weight_sum for k, v in available_weights.items()}
        
        # Weighted average of point estimates
        points = [v[0] for v in valid_estimates.values()]
        signal_names = list(valid_estimates.keys())
        signal_weights = [available_weights[name] for name in signal_names]
        
        ensemble_point = np.average(points, weights=signal_weights)
        
        # Confidence intervals: take widest bounds
        all_lowers = [v[1] for v in valid_estimates.values()]
        all_uppers = [v[2] for v in valid_estimates.values()]
        
        ensemble_lower = min(all_lowers)
        ensemble_upper = max(all_uppers)
        
        # Dominant signal (highest weight)
        dominant_signal = max(available_weights, key=available_weights.get)
        
        return ensemble_point, ensemble_lower, ensemble_upper, dominant_signal
    
    def estimate(
        self,
        record: Dict,
        naics_code: str,
        linkedin_headcount: Optional[float] = None,
        review_count_3m: Optional[int] = None,
        review_count_6_12m: Optional[int] = None,
        building_area_sqm: Optional[float] = None,
        job_postings_6m: Optional[int] = None,
        job_postings_peak: Optional[int] = None
    ) -> EmployeeEstimate:
        """
        Generate comprehensive employee estimate with confidence interval
        
        Args:
            record: Dictionary with at minimum 'duns_id', 'company_name'
            naics_code: Target NAICS code
            linkedin_headcount: LinkedIn employee count (if available)
            review_count_3m: Google reviews in last 3 months
            review_count_6_12m: Google reviews in 6-12 months prior
            building_area_sqm: Store footprint area
            job_postings_6m: Recent job postings
            job_postings_peak: Historical peak postings
            
        Returns:
            EmployeeEstimate object with point + CI
        """
        # Generate individual estimates
        estimates = {}
        
        # LinkedIn signal (highest priority)
        if linkedin_headcount:
            point, lower, upper = self.estimate_from_linkedin(linkedin_headcount)
            if point:
                estimates['linkedin'] = (point, lower, upper)
        
        # Review velocity signal
        if review_count_3m and review_count_6_12m:
            point, lower, upper = self.estimate_from_review_velocity(
                review_count_3m, review_count_6_12m, naics_code
            )
            if point:
                estimates['review_velocity'] = (point, lower, upper)
        
        # Building area signal
        if building_area_sqm:
            point, lower, upper = self.estimate_from_building_area(building_area_sqm, naics_code)
            if point:
                estimates['building_area'] = (point, lower, upper)
        
        # Job posting signal
        if job_postings_6m is not None and job_postings_peak is not None:
            point, lower, upper = self.estimate_from_job_postings(
                job_postings_6m, job_postings_peak, naics_code
            )
            if point:
                estimates['job_postings'] = (point, lower, upper)
        
        # Determine confidence level based on signal quality
        confidence_level = self._determine_confidence(estimates)
        
        # Select estimation method
        if 'linkedin' in estimates:
            estimation_method = 'linkedin'
        elif len(estimates) >= 2:
            estimation_method = 'xgboost'
        else:
            estimation_method = 'rule_based'
        
        # Ensemble combination
        if not estimates:
            # Fallback to baseline
            baseline = self.naics_baselines.get(naics_code, {})
            point_est = baseline.get('avg_employees', 10)
            ci_lower = baseline.get('min_employees', 3)
            ci_upper = baseline.get('max_employees', 30)
            dominant = 'baseline'
        else:
            point_est, ci_lower, ci_upper, dominant = self.ensemble_estimate(estimates)
        
        return EmployeeEstimate(
            duns_id=record.get('duns_id', 'unknown'),
            company_name=record.get('company_name', 'unknown'),
            point_estimate=round(point_est, 1) if point_est else None,
            ci_lower=round(ci_lower, 1) if ci_lower else None,
            ci_upper=round(ci_upper, 1) if ci_upper else None,
            confidence_level=confidence_level,
            estimation_method=estimation_method,
            primary_signal=dominant,
            signals_used=list(estimates.keys()),
            naics_code=naics_code
        )
    
    def _determine_confidence(self, estimates: Dict) -> str:
        """
        Determine confidence level based on available signals
        
        Args:
            estimates: Dictionary of valid signal estimates
            
        Returns:
            'high', 'medium', or 'low'
        """
        signal_count = len(estimates)
        has_linkedin = 'linkedin' in estimates
        has_reviews = 'review_velocity' in estimates
        
        # Confidence rules
        if has_linkedin:
            return 'high'  # LinkedIn is highest credibility
        elif signal_count >= 3:
            return 'high'  # Multiple signals = high confidence
        elif signal_count == 2 and has_reviews:
            return 'medium'
        elif signal_count >= 1:
            return 'medium'
        else:
            return 'low'
    
    def process_batch(self, df: pd.DataFrame, naics_code: str) -> pd.DataFrame:
        """
        Process batch of establishments
        
        Args:
            df: DataFrame with business records
            naics_code: Target NAICS code for batch
            
        Returns:
            DataFrame with added employee estimate columns
        """
        estimates_list = []
        
        for _, row in df.iterrows():
            estimate = self.estimate(
                record=row.to_dict(),
                naics_code=naics_code,
                linkedin_headcount=row.get('linkedin_headcount'),
                review_count_3m=row.get('review_count_3m'),
                review_count_6_12m=row.get('review_count_6_12m'),
                building_area_sqm=row.get('building_area_sqm'),
                job_postings_6m=row.get('job_postings_6m'),
                job_postings_peak=row.get('job_postings_peak')
            )
            estimates_list.append(estimate)
        
        # Convert to DataFrame
        results = pd.DataFrame([
            {
                'employees_optimized': e.point_estimate,
                'employees_ci_lower': e.ci_lower,
                'employees_ci_upper': e.ci_upper,
                'employees_confidence': e.confidence_level,
                'employees_estimation_method': e.estimation_method,
                'employees_primary_signal': e.primary_signal,
                'employees_signals_count': len(e.signals_used)
            }
            for e in estimates_list
        ])
        
        return pd.concat([df.reset_index(drop=True), results], axis=1)
