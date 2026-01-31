"""
Geographic boundary validation for NETS Enhancement System.
Validates coordinates against city-specific boundaries.
"""

from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class BoundaryValidator:
    """
    Validate geographic coordinates against city boundaries.
    Uses city configuration for bounds - no hardcoded values.
    """
    
    def __init__(self, bounds: Tuple[float, float, float, float]):
        """
        Initialize validator with bounding box.
        
        Args:
            bounds: (min_lon, min_lat, max_lon, max_lat) in EPSG:4326
        """
        self.min_lon, self.min_lat, self.max_lon, self.max_lat = bounds
    
    def is_within_bounds(self, lat: float, lon: float) -> bool:
        """
        Check if coordinates are within the bounding box.
        
        Args:
            lat: Latitude (EPSG:4326)
            lon: Longitude (EPSG:4326)
            
        Returns:
            True if within bounds, False otherwise
        """
        if lat is None or lon is None:
            return False
        return (self.min_lon <= lon <= self.max_lon and 
                self.min_lat <= lat <= self.max_lat)
    
    def validate_coordinate_format(self, lat: float, lon: float) -> bool:
        """
        Validate coordinate format (reasonable WGS84 values).
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            True if valid format
        """
        if lat is None or lon is None:
            return False
        # Valid WGS84 ranges
        return -90 <= lat <= 90 and -180 <= lon <= 180
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Return the bounding box."""
        return (self.min_lon, self.min_lat, self.max_lon, self.max_lat)


def validate_coordinates(
    lat: float, 
    lon: float, 
    bounds: Optional[Tuple[float, float, float, float]] = None
) -> Tuple[bool, str]:
    """
    Validate coordinates with optional boundary check.
    
    Args:
        lat: Latitude
        lon: Longitude
        bounds: Optional bounding box (min_lon, min_lat, max_lon, max_lat)
        
    Returns:
        Tuple of (is_valid, message)
    """
    # Check for None/NaN
    if lat is None or lon is None:
        return False, "Missing coordinates"
    
    try:
        lat = float(lat)
        lon = float(lon)
    except (ValueError, TypeError):
        return False, "Invalid coordinate format"
    
    # Check WGS84 range
    if not (-90 <= lat <= 90):
        return False, f"Latitude out of range: {lat}"
    if not (-180 <= lon <= 180):
        return False, f"Longitude out of range: {lon}"
    
    # Check bounds if provided
    if bounds:
        min_lon, min_lat, max_lon, max_lat = bounds
        if not (min_lon <= lon <= max_lon and min_lat <= lat <= max_lat):
            return False, "Coordinates outside city bounds"
    
    return True, "Valid"
