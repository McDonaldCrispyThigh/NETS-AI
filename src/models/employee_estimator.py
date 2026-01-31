"""
Employee estimation using multiple signals.
"""

from typing import Dict, Optional
import math
from src.config import (
 EMPLOYEE_AREA_COEFFICIENTS,
 SERVICE_CATEGORIES,
 REVIEW_VELOCITY_BASELINES,
 POPULAR_TIMES_MAX_CUSTOMERS_PER_HOUR,
 POPULAR_TIMES_CUSTOMERS_PER_EMPLOYEE
)


class EmployeeEstimator:
 def __init__(self, category: str):
 self.category = category
 self.area_coeff = EMPLOYEE_AREA_COEFFICIENTS.get(category, 1 / 30.0)
 self.review_velocity_baseline = REVIEW_VELOCITY_BASELINES.get(category, 5.0)
 self.max_customers_per_hour = POPULAR_TIMES_MAX_CUSTOMERS_PER_HOUR.get(category, 100.0)

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

 def estimate_from_review_density(self, reviews_per_month: Optional[float],
 avg_reviews_per_month: Optional[float]) -> Optional[int]:
 if reviews_per_month is None:
 return None
 baseline = avg_reviews_per_month if avg_reviews_per_month else self.review_velocity_baseline
 if baseline <= 0:
 return None
 intensity = reviews_per_month / baseline
 baseline_staff = max(int(round(self.review_velocity_baseline * 0.3)), 1)
 return max(int(round(baseline_staff * intensity)), 1)

 def estimate_from_popular_times(self, popular_times_peak: Optional[float]) -> Optional[int]:
 if popular_times_peak is None:
 return None
 peak = float(popular_times_peak)
 if peak <= 0:
 return None

 # If peak is index (0-100), convert to customers/hour using category max
 if peak <= 100:
 customers_per_hour = (peak / 100.0) * self.max_customers_per_hour
 else:
 customers_per_hour = peak

 employees = math.ceil(customers_per_hour / POPULAR_TIMES_CUSTOMERS_PER_EMPLOYEE)
 return max(int(employees), 1)

 def estimate_from_sos_partners(self, sos_partner_count: Optional[float]) -> Optional[int]:
 if sos_partner_count is None:
 return None
 # Partner count is a lower bound; scale by 2 to approximate staff
 return max(int(round(sos_partner_count * 2)), 0)

 def combine_estimates(self, signals: Dict) -> Dict:
 estimates = {}
 if self.category in SERVICE_CATEGORIES:
 estimates['review_density'] = self.estimate_from_review_density(
 signals.get('reviews_per_month'),
 signals.get('reviews_per_month_avg')
 )
 estimates['popular_times'] = self.estimate_from_popular_times(signals.get('popular_times_peak'))
 else:
 estimates['linkedin'] = self.estimate_from_linkedin(signals.get('linkedin_employee_count'))
 estimates['job_postings'] = self.estimate_from_job_postings(signals.get('job_postings_12m'))
 estimates['building_area'] = self.estimate_from_building_area(signals.get('building_area_m2'))
 estimates['review_density'] = self.estimate_from_review_density(
 signals.get('reviews_per_month'),
 signals.get('reviews_per_month_avg')
 )
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
