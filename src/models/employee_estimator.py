"""
Employee estimation using multiple signals.
"""

from typing import Dict, Optional
from src.config import EMPLOYEE_AREA_COEFFICIENTS


class EmployeeEstimator:
    def __init__(self, category: str):
        self.category = category
        self.area_coeff = EMPLOYEE_AREA_COEFFICIENTS.get(category, 1 / 30.0)

    def estimate_from_linkedin(self, linkedin_employee_count: Optional[float]) -> Optional[int]:
        if linkedin_employee_count is None:
            return None
        return max(int(linkedin_employee_count), 0)

    def estimate_from_job_postings(self, job_postings_12m: Optional[float]) -> Optional[int]:
        if job_postings_12m is None:
            return None
        # Conservative mapping: 1 active posting ~ 2-4 employees
        return max(int(round(job_postings_12m * 3)), 0)

    def estimate_from_building_area(self, building_area_m2: Optional[float]) -> Optional[int]:
        if building_area_m2 is None:
            return None
        return max(int(round(building_area_m2 * self.area_coeff)), 0)

    def estimate_from_review_velocity(self, reviews_per_month: Optional[float]) -> Optional[int]:
        if reviews_per_month is None:
            return None
        # Category-agnostic proxy: 5 reviews/month ~ 1-2 employees baseline
        return max(int(round(reviews_per_month * 0.3)), 0)

    def estimate_from_popular_times(self, popular_times_peak: Optional[float]) -> Optional[int]:
        if popular_times_peak is None:
            return None
        # Heuristic: peak visitor index / 15
        return max(int(round(popular_times_peak / 15.0)), 0)

    def estimate_from_sos_partners(self, sos_partner_count: Optional[float]) -> Optional[int]:
        if sos_partner_count is None:
            return None
        # Partner count is a lower bound; scale by 2 to approximate staff
        return max(int(round(sos_partner_count * 2)), 0)

    def combine_estimates(self, signals: Dict) -> Dict:
        estimates = {}
        estimates['linkedin'] = self.estimate_from_linkedin(signals.get('linkedin_employee_count'))
        estimates['job_postings'] = self.estimate_from_job_postings(signals.get('job_postings_12m'))
        estimates['building_area'] = self.estimate_from_building_area(signals.get('building_area_m2'))
        estimates['review_velocity'] = self.estimate_from_review_velocity(signals.get('reviews_per_month'))
        estimates['popular_times'] = self.estimate_from_popular_times(signals.get('popular_times_peak'))
        estimates['sos_partners'] = self.estimate_from_sos_partners(signals.get('sos_partner_count'))

        valid = [v for v in estimates.values() if v is not None]
        if not valid:
            return {
                'employee_estimate': None,
                'employee_estimate_min': None,
                'employee_estimate_max': None,
                'employee_estimate_methods': []
            }

        return {
            'employee_estimate': int(round(sum(valid) / len(valid))),
            'employee_estimate_min': int(min(valid)),
            'employee_estimate_max': int(max(valid)),
            'employee_estimate_methods': [k for k, v in estimates.items() if v is not None]
        }
