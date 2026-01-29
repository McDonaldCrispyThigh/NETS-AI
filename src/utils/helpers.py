"""
Helper utilities for AI-BDD
"""

import re
import requests
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path


def clean_url(url: str) -> str:
    """Clean and normalize URL"""
    if not url:
        return ""
    
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Remove trailing slashes
    url = url.rstrip('/')
    
    return url


def check_website_status(url: str, timeout: int = 5) -> Dict:
    """
    Check if a website is accessible
    
    Returns:
        Dict with status_code, accessible, response_time
    """
    url = clean_url(url)
    
    try:
        start = datetime.now()
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        elapsed = (datetime.now() - start).total_seconds()
        
        return {
            'status_code': response.status_code,
            'accessible': response.status_code == 200,
            'response_time': elapsed,
            'final_url': response.url
        }
    except requests.exceptions.Timeout:
        return {'status_code': None, 'accessible': False, 'error': 'Timeout'}
    except requests.exceptions.RequestException as e:
        return {'status_code': None, 'accessible': False, 'error': str(e)[:100]}


def parse_review_date(date_str: str) -> Optional[datetime]:
    """Parse various date formats from reviews"""
    if not date_str:
        return None
    
    # Try common formats
    formats = [
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%m/%d/%Y',
        '%d-%m-%Y',
        '%B %d, %Y',
        '%b %d, %Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def days_since_last_review(last_review_date: str) -> Optional[int]:
    """Calculate days since last review"""
    date = parse_review_date(last_review_date)
    if not date:
        return None
    
    return (datetime.now() - date).days


def is_recent_activity(last_review_date: str, threshold_days: int = 180) -> bool:
    """Check if business has recent activity"""
    days = days_since_last_review(last_review_date)
    if days is None:
        return False
    
    return days <= threshold_days


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """Extract keywords from text (simple version)"""
    if not text:
        return []
    
    # Remove punctuation, lowercase, split
    words = re.findall(r'\b[a-zA-Z]{' + str(min_length) + r',}\b', text.lower())
    
    # Remove common stop words
    stop_words = {'the', 'and', 'this', 'that', 'with', 'for', 'are', 'was', 'were', 'been'}
    keywords = [w for w in words if w not in stop_words]
    
    # Return unique keywords
    return list(set(keywords))


def normalize_name(text: str) -> str:
    """Normalize business names for matching"""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def calculate_review_velocity(review_count: int, oldest_review_date: str, last_review_date: str) -> Optional[float]:
    """
    Estimate reviews per month based on oldest and latest review dates.

    Args:
        review_count: Total review count
        oldest_review_date: Oldest review date string (YYYY-MM-DD)
        last_review_date: Latest review date string (YYYY-MM-DD)

    Returns:
        Reviews per month (float) or None if dates unavailable
    """
    if review_count is None or review_count <= 0:
        return None

    start = parse_review_date(oldest_review_date)
    end = parse_review_date(last_review_date)
    if not start or not end or end <= start:
        return None

    months = max((end - start).days / 30.0, 1.0)
    return review_count / months


def calculate_confidence_score(indicators: Dict) -> str:
    """
    Calculate confidence level based on data quality indicators
    
    Args:
        indicators: Dict with various data quality flags
        
    Returns:
        'High', 'Medium', or 'Low'
    """
    score = 0
    max_score = 0
    
    # Review recency
    if indicators.get('has_recent_reviews'):
        score += 3
    max_score += 3
    
    # Review count
    review_count = indicators.get('review_count', 0)
    if review_count > 50:
        score += 2
    elif review_count > 10:
        score += 1
    max_score += 2
    
    # Website accessible
    if indicators.get('website_accessible'):
        score += 2
    max_score += 2
    
    # Operating hours
    if indicators.get('has_hours'):
        score += 1
    max_score += 1
    
    # Wayback validation
    if indicators.get('wayback_verified'):
        score += 2
    max_score += 2
    
    # Calculate percentage
    confidence_pct = (score / max_score) * 100 if max_score > 0 else 0
    
    if confidence_pct >= 70:
        return 'High'
    elif confidence_pct >= 40:
        return 'Medium'
    else:
        return 'Low'


def generate_cache_key(*args) -> str:
    """Generate cache key from arguments"""
    key_string = "_".join(str(arg) for arg in args)
    return hashlib.md5(key_string.encode()).hexdigest()


def save_json(data: Dict, filepath: Path):
    """Save dict to JSON file"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(filepath: Path) -> Optional[Dict]:
    """Load JSON file"""
    if not filepath.exists():
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_currency(amount: float) -> str:
    """Format number as currency"""
    return f"${amount:,.2f}"


def calculate_api_cost(num_places: int, gpt_calls_per_place: int = 1) -> Dict:
    """
    Estimate API costs for a data collection run
    
    Args:
        num_places: Number of businesses to analyze
        gpt_calls_per_place: GPT API calls per business
        
    Returns:
        Cost breakdown
    """
    # Pricing (as of 2026)
    GOOGLE_MAPS_COST_PER_CALL = 0.017  # Places Details
    GPT_4O_MINI_COST_PER_CALL = 0.0001  # Rough estimate
    
    google_cost = num_places * GOOGLE_MAPS_COST_PER_CALL
    gpt_cost = num_places * gpt_calls_per_place * GPT_4O_MINI_COST_PER_CALL
    
    return {
        'google_maps_cost': google_cost,
        'gpt_cost': gpt_cost,
        'total_cost': google_cost + gpt_cost,
        'formatted_total': format_currency(google_cost + gpt_cost)
    }


# Example usage
if __name__ == "__main__":
    # Test website check
    status = check_website_status("google.com")
    print(f"Website status: {status}")
    
    # Test confidence calculation
    indicators = {
        'has_recent_reviews': True,
        'review_count': 100,
        'website_accessible': True,
        'has_hours': True,
        'wayback_verified': False
    }
    confidence = calculate_confidence_score(indicators)
    print(f"Confidence: {confidence}")
    
    # Test cost calculation
    costs = calculate_api_cost(num_places=500)
    print(f"Estimated cost: {costs}")
