"""
Secretary of State (SOS) registry loader and matcher.

Expected CSV columns (minimum):
- legal_name
- address
- status
- registration_date
- entity_id
- partner_count (optional)
"""

from pathlib import Path
import pandas as pd
from typing import Optional, Dict
from src.utils.helpers import normalize_name


class SOSLoader:
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path) if csv_path else None
        self.df = None
        if self.csv_path and self.csv_path.exists():
            self.df = pd.read_csv(self.csv_path)
            self.df['name_norm'] = self.df['legal_name'].astype(str).apply(normalize_name)
            self.df['address_norm'] = self.df['address'].astype(str).apply(normalize_name)

    def match(self, name: str, address: str) -> Optional[Dict]:
        if self.df is None:
            return None
        name_norm = normalize_name(name)
        addr_norm = normalize_name(address)
        matches = self.df[
            (self.df['name_norm'] == name_norm) & 
            (self.df['address_norm'] == addr_norm)
        ]
        if matches.empty:
            return None
        row = matches.iloc[0].to_dict()
        return {
            'sos_entity_id': row.get('entity_id'),
            'sos_legal_name': row.get('legal_name'),
            'sos_status': row.get('status'),
            'sos_registration_date': row.get('registration_date'),
            'sos_partner_count': row.get('partner_count')
        }
