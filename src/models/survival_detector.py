"""
Business Survival Detection Module
Predict operational status and closure probability using multi-signal analysis
Signals: Google review decay + review recency + job posting activity + street view
Output: is_active probability (0-1) + confidence level
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available")


@dataclass
class SurvivalEstimate:
    """Container for business survival/operational status estimate"""
    duns_id: str
    company_name: str
    is_active_prob: float  # 0.0-1.0 probability of being active
    confidence_level: str  # 'high', 'medium', 'low'
    last_review_date: Optional[str]
    days_since_last_review: Optional[int]
    review_decay_rate: Optional[float]
    risk_factors: List[str]
    protective_factors: List[str]
    primary_indicator: str  # Which signal was most influential
    signals_used: List[str]


class SurvivalDetector:
    """
    Detect business operational status using multi-signal analysis
    Implements Random Forest classification + decay curve analysis
    """
    
    def __init__(self):
        """Initialize survival detector"""
        self.rf_model = None if SKLEARN_AVAILABLE else None
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.logger = logger
        self.feature_names = [
            'days_since_last_review',
            'review_count_recent',
            'review_decay_rate',
            'job_posting_activity',
            'street_view_visible',
            'latest_review_sentiment_positive'
        ]
    
    def calculate_review_decay_rate(
        self,
        review_count_3m: Optional[int],
        review_count_6_12m: Optional[int]
    ) -> Optional[float]:
        """
        Calculate review decay rate (trend indicator)
        
        Formula: decay_rate = (reviews_recent_3m / 3) / (reviews_6_12m / 6)
        
        Interpretation:
            - decay_rate > 1.0: Increasing reviews (business growing/healthy)
            - decay_rate = 1.0: Stable reviews (stable business)
            - decay_rate < 1.0: Declining reviews (concerning indicator)
            - decay_rate < 0.3: Steep decline (likely closure within 6 months)
        
        Args:
            review_count_3m: Reviews in recent 3 months
            review_count_6_12m: Reviews in 6-12 months prior
            
        Returns:
            Decay rate (float) or None if insufficient data
        """
        if not review_count_3m or not review_count_6_12m:
            return None
        
        if review_count_6_12m < 2:  # Insufficient historical baseline
            return None
        
        recent_monthly = review_count_3m / 3
        historical_monthly = review_count_6_12m / 6
        
        # Avoid division by zero
        if historical_monthly < 0.1:
            return None
        
        decay_rate = recent_monthly / historical_monthly
        return float(decay_rate)
    
    def evaluate_review_recency(
        self,
        last_review_date: Optional[str]
    ) -> Tuple[Optional[int], bool]:
        """
        Evaluate recency of latest customer review
        
        Interpretation:
            - < 30 days: Strong positive signal (actively serving customers)
            - 30-90 days: Neutral signal
            - 90-180 days: Caution (reduced activity)
            - 180+ days: Strong negative signal (likely inactive/closed)
        
        Args:
            last_review_date: ISO format date string (YYYY-MM-DD)
            
        Returns:
            Tuple of (days_since_review, is_recent_bool)
        """
        # Handle None and NaN cases
        if last_review_date is None or (isinstance(last_review_date, float) and np.isnan(last_review_date)):
            return None, False
        
        if isinstance(last_review_date, str) and last_review_date.lower() in ['nan', 'none', '']:
            return None, False
        
        try:
            review_date = pd.to_datetime(last_review_date)
            if pd.isna(review_date):
                return None, False
            
            review_date = review_date.date()
            today = datetime.now().date()
            days_since = (today - review_date).days
            
            is_recent = days_since <= 90  # Within 3 months
            
            return days_since, is_recent
        except Exception as e:
            self.logger.debug(f"Error parsing review date {last_review_date}: {e}")
            return None, False
    
    def evaluate_job_posting_activity(
        self,
        postings_recent_6m: Optional[int],
        postings_peak_historical: Optional[int]
    ) -> Tuple[float, bool]:
        """
        Evaluate job posting activity as survival indicator
        
        Theory: Active hiring = operational business
        Declining hiring = downsizing or closure preparation
        
        Args:
            postings_recent_6m: Job postings in last 6 months
            postings_peak_historical: Peak postings in any 6-month period
            
        Returns:
            Tuple of (activity_ratio, has_recent_activity_bool)
        """
        if postings_recent_6m is None or postings_peak_historical is None:
            return 0.5, False  # Neutral if data unavailable
        
        peak = max(1, postings_peak_historical)  # Avoid division by zero
        ratio = float(postings_recent_6m) / peak
        
        # Activity threshold: at least 20% of peak activity
        has_activity = postings_recent_6m >= 1 and ratio >= 0.2
        
        return ratio, has_activity
    
    def evaluate_street_view(
        self,
        facade_visible: Optional[bool],
        signage_visible: Optional[bool],
        lighting_indicators: Optional[bool]
    ) -> bool:
        """
        Evaluate street-view visual indicators of operational status
        
        Positive indicators:
            - Visible storefront facade
            - Legible business signage
            - Window lighting (evening hours)
            - Recent merchandise displays
        
        Args:
            facade_visible: Boolean from OpenCV edge detection
            signage_visible: Boolean from OCR/detection
            lighting_indicators: Boolean from pixel analysis
            
        Returns:
            Boolean: True if business appears operational from street view
        """
        if facade_visible is None and signage_visible is None and lighting_indicators is None:
            return None  # No street view data available
        
        indicators = [facade_visible, signage_visible, lighting_indicators]
        non_null = [i for i in indicators if i is not None]
        
        if not non_null:
            return None
        
        # Majority voting: at least 2 of 3 indicators positive
        return sum(non_null) >= 2
    
    def score_survival(
        self,
        last_review_date: Optional[str] = None,
        review_count_3m: Optional[int] = None,
        review_count_6_12m: Optional[int] = None,
        job_postings_6m: Optional[int] = None,
        job_postings_peak: Optional[int] = None,
        facade_visible: Optional[bool] = None,
        signage_visible: Optional[bool] = None,
        lighting_visible: Optional[bool] = None,
        latest_review_sentiment: Optional[str] = None
    ) -> Dict:
        """
        Score business survival probability using multi-signal fusion
        
        Args:
            last_review_date: Latest customer review date
            review_count_3m: Reviews in last 3 months
            review_count_6_12m: Reviews in months 6-12
            job_postings_6m: Job postings in last 6 months
            job_postings_peak: Historical peak job postings
            facade_visible: Street view facade detection
            signage_visible: Street view signage detection
            lighting_visible: Street view lighting detection
            latest_review_sentiment: Sentiment of latest review
            
        Returns:
            Dictionary with survival probability and supporting metrics
        """
        signals_used = []
        risk_factors = []
        protective_factors = []
        signal_scores = []
        signal_weights = []
        
        # Signal 1: Review recency (weight: 0.35)
        days_since, is_recent = self.evaluate_review_recency(last_review_date)
        if days_since is not None:
            signals_used.append('review_recency')
            if days_since <= 30:
                score = 1.0
                protective_factors.append(f"Recent review ({days_since} days ago)")
            elif days_since <= 90:
                score = 0.75
                protective_factors.append(f"Moderate recency ({days_since} days)")
            elif days_since <= 180:
                score = 0.4
                risk_factors.append(f"Declining activity ({days_since} days since review)")
            else:
                score = 0.1
                risk_factors.append(f"No recent activity ({days_since} days without review)")
            
            signal_scores.append(score)
            signal_weights.append(0.35)
        
        # Signal 2: Review decay rate (weight: 0.30)
        decay_rate = self.calculate_review_decay_rate(review_count_3m, review_count_6_12m)
        if decay_rate is not None:
            signals_used.append('review_decay')
            if decay_rate > 1.2:
                score = 0.9
                protective_factors.append(f"Growing reviews (decay={decay_rate:.2f})")
            elif decay_rate > 0.8:
                score = 0.8
                protective_factors.append("Stable review activity")
            elif decay_rate > 0.5:
                score = 0.5
                risk_factors.append(f"Declining reviews (decay={decay_rate:.2f})")
            else:
                score = 0.2
                risk_factors.append(f"Sharp review decline (decay={decay_rate:.2f})")
            
            signal_scores.append(score)
            signal_weights.append(0.30)
        
        # Signal 3: Job posting activity (weight: 0.20)
        activity_ratio, has_activity = self.evaluate_job_posting_activity(
            job_postings_6m, job_postings_peak
        )
        if job_postings_6m is not None:
            signals_used.append('job_postings')
            if has_activity and activity_ratio > 0.6:
                score = 0.85
                protective_factors.append("Active hiring")
            elif has_activity:
                score = 0.65
                protective_factors.append("Recent job postings")
            elif job_postings_peak and job_postings_peak > 0:
                score = 0.35
                risk_factors.append("Reduced hiring activity")
            else:
                score = 0.5
            
            signal_scores.append(score)
            signal_weights.append(0.20)
        
        # Signal 4: Street view visual indicators (weight: 0.15)
        street_view_score = self.evaluate_street_view(facade_visible, signage_visible, lighting_visible)
        if street_view_score is not None:
            signals_used.append('street_view')
            if street_view_score:
                score = 0.8
                protective_factors.append("Visible operational indicators")
            else:
                score = 0.2
                risk_factors.append("No visible operational indicators")
            
            signal_scores.append(score)
            signal_weights.append(0.15)
        
        # Calculate weighted probability
        if signal_scores:
            total_weight = sum(signal_weights)
            normalized_weights = [w / total_weight for w in signal_weights]
            survival_prob = np.average(signal_scores, weights=normalized_weights)
        else:
            # Fallback if no signals available
            survival_prob = 0.5  # Neutral default
            protective_factors.append("Insufficient data - neutral assessment")
        
        # Determine confidence level
        confidence = self._determine_confidence(len(signals_used), signal_scores)
        
        # Identify primary indicator
        primary = self._identify_primary_indicator(signals_used, signal_scores, signal_weights)
        
        return {
            'is_active_prob': float(survival_prob),
            'confidence_level': confidence,
            'days_since_last_review': days_since,
            'review_decay_rate': decay_rate,
            'risk_factors': risk_factors,
            'protective_factors': protective_factors,
            'primary_indicator': primary,
            'signals_used': signals_used,
            'signal_count': len(signals_used)
        }
    
    def _determine_confidence(self, signal_count: int, signal_scores: List[float]) -> str:
        """
        Determine confidence level based on signal quality and count
        
        Args:
            signal_count: Number of signals available
            signal_scores: Scores from individual signals
            
        Returns:
            'high', 'medium', or 'low'
        """
        if signal_count >= 3:
            # Multiple signals = higher confidence
            score_variance = np.var(signal_scores) if len(signal_scores) > 1 else 0
            if score_variance < 0.1:  # Signals agree
                return 'high'
            return 'high'
        elif signal_count == 2:
            return 'medium'
        else:
            return 'low'
    
    def _identify_primary_indicator(
        self,
        signals: List[str],
        scores: List[float],
        weights: List[float]
    ) -> str:
        """
        Identify which signal most strongly influenced the survival prediction
        
        Args:
            signals: List of signal names
            scores: Corresponding scores
            weights: Corresponding weights
            
        Returns:
            Name of primary signal
        """
        if not signals:
            return 'none'
        
        # Weighted influence = score * weight
        influences = [s * w for s, w in zip(scores, weights)]
        max_idx = np.argmax(influences)
        
        return signals[max_idx]
    
    def estimate(
        self,
        record: Dict,
        **signal_kwargs
    ) -> SurvivalEstimate:
        """
        Generate comprehensive survival estimate
        
        Args:
            record: Dictionary with at minimum 'duns_id', 'company_name'
            **signal_kwargs: All signal parameters (see score_survival)
            
        Returns:
            SurvivalEstimate object
        """
        scores = self.score_survival(**signal_kwargs)
        
        return SurvivalEstimate(
            duns_id=record.get('duns_id', 'unknown'),
            company_name=record.get('company_name', 'unknown'),
            is_active_prob=scores['is_active_prob'],
            confidence_level=scores['confidence_level'],
            last_review_date=signal_kwargs.get('last_review_date'),
            days_since_last_review=scores['days_since_last_review'],
            review_decay_rate=scores['review_decay_rate'],
            risk_factors=scores['risk_factors'],
            protective_factors=scores['protective_factors'],
            primary_indicator=scores['primary_indicator'],
            signals_used=scores['signals_used']
        )
    
    def process_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process batch of establishments for survival detection
        
        Args:
            df: DataFrame with business records and signals
            
        Returns:
            DataFrame with added survival probability columns
        """
        survival_list = []
        
        for _, row in df.iterrows():
            estimate = self.estimate(
                record=row.to_dict(),
                last_review_date=row.get('last_review_date'),
                review_count_3m=row.get('review_count_3m'),
                review_count_6_12m=row.get('review_count_6_12m'),
                job_postings_6m=row.get('job_postings_6m'),
                job_postings_peak=row.get('job_postings_peak'),
                facade_visible=row.get('facade_visible'),
                signage_visible=row.get('signage_visible'),
                lighting_visible=row.get('lighting_visible'),
                latest_review_sentiment=row.get('latest_review_sentiment')
            )
            survival_list.append(estimate)
        
        # Convert to DataFrame
        results = pd.DataFrame([
            {
                'is_active_prob': e.is_active_prob,
                'is_active_confidence': e.confidence_level,
                'days_since_last_review': e.days_since_last_review,
                'review_decay_rate': round(e.review_decay_rate, 2) if e.review_decay_rate else None,
                'survival_primary_indicator': e.primary_indicator,
                'survival_signals_count': len(e.signals_used),
                'survival_risk_factors': ', '.join(e.risk_factors) if e.risk_factors else None,
                'survival_protective_factors': ', '.join(e.protective_factors) if e.protective_factors else None
            }
            for e in survival_list
        ])
        
        return pd.concat([df.reset_index(drop=True), results], axis=1)
