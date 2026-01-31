"""
External signals loader for employee estimation and validation.

Expected CSV columns (optional):
- name
- address
- linkedin_employee_count
- job_postings_12m
- building_area_m2
- popular_times_peak
- sos_partner_count
"""

from pathlib import Path
import pandas as pd
from typing import Optional, Dict
from src.utils.helpers import normalize_name


class ExternalSignalsLoader:
 def __init__(self, csv_path: str):
 self.csv_path = Path(csv_path) if csv_path else None
 self.df = None
 if self.csv_path and self.csv_path.exists():
 self.df = pd.read_csv(self.csv_path)
 self.df['name_norm'] = self.df['name'].astype(str).apply(normalize_name)
 self.df['address_norm'] = self.df['address'].astype(str).apply(normalize_name)

 def match(self, name: str, address: str) -> Optional[Dict]:
 if self.df is None:
 return None
 name_norm = normalize_name(name)
 addr_norm = normalize_name(address)
 matches = self.df[(self.df['name_norm'] == name_norm) & (self.df['address_norm'] == addr_norm)]
 if matches.empty:
 return None
 row = matches.iloc[0].to_dict()
 return {
 'linkedin_employee_count': row.get('linkedin_employee_count'),
 'job_postings_12m': row.get('job_postings_12m'),
 'building_area_m2': row.get('building_area_m2'),
 'popular_times_peak': row.get('popular_times_peak'),
 'sos_partner_count': row.get('sos_partner_count')
 }
