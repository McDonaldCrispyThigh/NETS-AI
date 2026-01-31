"""
Distance calculations for NETS Enhancement System.
Haversine distance and matching threshold validation.
"""

import math
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Earth radius in meters
EARTH_RADIUS_M = 6371000

# Default matching threshold (50 meters)
DEFAULT_MATCHING_THRESHOLD_M = 50.0


def haversine_distance(
    lat1: float, 
    lon1: float, 
    lat2: float, 
    lon2: float
) -> float:
    """
    Calculate the great-circle distance between two points on Earth.
    
    Args:
        lat1, lon1: First point coordinates (degrees)
        lat2, lon2: Second point coordinates (degrees)
        
    Returns:
        Distance in meters
    """
    if any(x is None for x in [lat1, lon1, lat2, lon2]):
        return float('inf')
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return EARTH_RADIUS_M * c


def is_within_matching_threshold(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    threshold_m: float = DEFAULT_MATCHING_THRESHOLD_M
) -> bool:
    """
    Check if two points are within the matching distance threshold.
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
        threshold_m: Distance threshold in meters (default: 50m)
        
    Returns:
        True if distance <= threshold
    """
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    return distance <= threshold_m


class DistanceCalculator:
    """
    Distance calculator with configurable threshold.
    """
    
    def __init__(self, threshold_m: float = DEFAULT_MATCHING_THRESHOLD_M):
        """
        Initialize calculator with threshold.
        
        Args:
            threshold_m: Matching distance threshold in meters
        """
        self.threshold_m = threshold_m
    
    def calculate_distance(
        self, 
        lat1: float, 
        lon1: float, 
        lat2: float, 
        lon2: float
    ) -> float:
        """Calculate distance between two points in meters."""
        return haversine_distance(lat1, lon1, lat2, lon2)
    
    def is_match(
        self, 
        lat1: float, 
        lon1: float, 
        lat2: float, 
        lon2: float
    ) -> bool:
        """Check if two points are within matching threshold."""
        return is_within_matching_threshold(
            lat1, lon1, lat2, lon2, self.threshold_m
        )
    
    def find_nearest(
        self,
        target_lat: float,
        target_lon: float,
        candidates: list,
        lat_key: str = 'latitude',
        lon_key: str = 'longitude'
    ) -> Tuple[Optional[dict], float]:
        """
        Find the nearest candidate to target coordinates.
        
        Args:
            target_lat, target_lon: Target coordinates
            candidates: List of dicts with lat/lon keys
            lat_key, lon_key: Keys for latitude/longitude in dicts
            
        Returns:
            Tuple of (nearest_candidate, distance) or (None, inf)
        """
        if not candidates:
            return None, float('inf')
        
        nearest = None
        min_distance = float('inf')
        
        for candidate in candidates:
            cand_lat = candidate.get(lat_key)
            cand_lon = candidate.get(lon_key)
            
            if cand_lat is None or cand_lon is None:
                continue
            
            distance = self.calculate_distance(
                target_lat, target_lon, cand_lat, cand_lon
            )
            
            if distance < min_distance:
                min_distance = distance
                nearest = candidate
        
        return nearest, min_distance
