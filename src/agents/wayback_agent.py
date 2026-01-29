"""
Wayback Machine Agent for historical business validation
Uses waybackpy to check website snapshots and validate business establishment dates
"""

import os
import time
from datetime import datetime
from waybackpy import WaybackMachineCDXServerAPI
import requests
from typing import Optional, Dict, List


class WaybackAgent:
    """
    Agent for querying Wayback Machine to validate:
    1. Business establishment dates (first website snapshot)
    2. Business closure dates (last website snapshot)
    3. Historical presence validation
    """
    
    def __init__(self, user_agent: str = "AI-BDD/1.0"):
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})
    
    def get_first_snapshot(self, url: str) -> Optional[Dict]:
        """
        Get the earliest snapshot of a URL from Wayback Machine
        
        Args:
            url: Website URL to query
            
        Returns:
            Dict with {date, url, timestamp} or None if not found
        """
        if not url:
            return None
        
        try:
            # Clean URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Query CDX API for oldest snapshot
            cdx = WaybackMachineCDXServerAPI(
                url=url,
                user_agent=self.user_agent,
                filters=['statuscode:200', 'mimetype:text/html']
            )
            
            # Get oldest snapshot
            oldest = cdx.oldest()
            
            if oldest:
                return {
                    'date': datetime.strptime(oldest.timestamp, '%Y%m%d%H%M%S'),
                    'url': oldest.archive_url,
                    'timestamp': oldest.timestamp,
                    'year': int(oldest.timestamp[:4])
                }
            
            return None
            
        except Exception as e:
            print(f"[Wayback] Error querying {url}: {str(e)[:50]}")
            return None
    
    def get_last_snapshot(self, url: str) -> Optional[Dict]:
        """
        Get the most recent snapshot of a URL
        
        Args:
            url: Website URL to query
            
        Returns:
            Dict with {date, url, timestamp} or None if not found
        """
        if not url:
            return None
        
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            cdx = WaybackMachineCDXServerAPI(
                url=url,
                user_agent=self.user_agent,
                filters=['statuscode:200', 'mimetype:text/html']
            )
            
            newest = cdx.newest()
            
            if newest:
                return {
                    'date': datetime.strptime(newest.timestamp, '%Y%m%d%H%M%S'),
                    'url': newest.archive_url,
                    'timestamp': newest.timestamp,
                    'year': int(newest.timestamp[:4])
                }
            
            return None
            
        except Exception as e:
            print(f"[Wayback] Error querying {url}: {str(e)[:50]}")
            return None
    
    def validate_establishment_year(self, url: str, claimed_year: int, tolerance: int = 2) -> Dict:
        """
        Validate if a business's claimed establishment year matches web history
        
        Args:
            url: Business website
            claimed_year: Year business claims to be established (e.g., from NETS)
            tolerance: Acceptable year difference
            
        Returns:
            Dict with validation results
        """
        first_snapshot = self.get_first_snapshot(url)
        
        if not first_snapshot:
            return {
                'validated': False,
                'reason': 'No web history found',
                'first_snapshot_year': None,
                'claimed_year': claimed_year
            }
        
        snapshot_year = first_snapshot['year']
        year_diff = abs(snapshot_year - claimed_year)
        
        is_valid = year_diff <= tolerance
        
        return {
            'validated': is_valid,
            'first_snapshot_year': snapshot_year,
            'claimed_year': claimed_year,
            'year_difference': year_diff,
            'reason': 'Match' if is_valid else f'{year_diff} year discrepancy',
            'snapshot_url': first_snapshot['url']
        }
    
    def check_business_active(self, url: str, cutoff_date: datetime) -> bool:
        """
        Check if business was active after a certain date
        
        Args:
            url: Business website
            cutoff_date: Date to check against
            
        Returns:
            True if last snapshot is after cutoff_date
        """
        last_snapshot = self.get_last_snapshot(url)
        
        if not last_snapshot:
            return False
        
        return last_snapshot['date'] > cutoff_date
    
    def get_snapshot_count(self, url: str, start_year: int = None, end_year: int = None) -> int:
        """
        Count number of snapshots for a URL in a time range
        Useful for detecting business activity level
        
        Args:
            url: Website URL
            start_year: Start year (optional)
            end_year: End year (optional)
            
        Returns:
            Number of snapshots
        """
        if not url:
            return 0
        
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            params = {
                'url': url,
                'filter': 'statuscode:200',
                'output': 'json'
            }
            
            if start_year:
                params['from'] = f"{start_year}0101"
            if end_year:
                params['to'] = f"{end_year}1231"
            
            response = self.session.get(
                'http://web.archive.org/cdx/search/cdx',
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                return len(lines) - 1  # Subtract header
            
            return 0
            
        except Exception as e:
            print(f"[Wayback] Error counting snapshots: {str(e)[:50]}")
            return 0


# Example usage
if __name__ == "__main__":
    agent = WaybackAgent()
    
    # Test with Starbucks
    result = agent.get_first_snapshot("starbucks.com")
    print(f"Starbucks first snapshot: {result}")
    
    # Validate establishment year
    validation = agent.validate_establishment_year("starbucks.com", 1971, tolerance=30)
    print(f"Validation: {validation}")
