"""
Coordinate transformation utilities for NETS Enhancement System.
Ensures all coordinates are in EPSG:4326 (WGS84).
"""

from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Standard CRS for the project
STANDARD_CRS = "EPSG:4326"


class CoordinateTransformer:
    """
    Transform and validate coordinates.
    Ensures consistent EPSG:4326 (WGS84) coordinate system.
    """
    
    def __init__(self):
        """Initialize transformer."""
        self.crs = STANDARD_CRS
    
    def validate_crs(self, crs: str) -> bool:
        """
        Check if CRS is the standard EPSG:4326.
        
        Args:
            crs: Coordinate Reference System string
            
        Returns:
            True if CRS is EPSG:4326
        """
        if crs is None:
            return False
        crs_upper = crs.upper().replace(" ", "")
        return crs_upper in ["EPSG:4326", "WGS84", "WGS 84"]
    
    def to_wgs84(
        self, 
        lat: float, 
        lon: float, 
        source_crs: str = None
    ) -> Tuple[float, float]:
        """
        Ensure coordinates are in WGS84.
        Currently assumes input is already WGS84.
        
        Args:
            lat: Latitude
            lon: Longitude
            source_crs: Source CRS (for future expansion)
            
        Returns:
            Tuple of (lat, lon) in WGS84
        """
        # For now, assume coordinates are already WGS84
        # In future, could add pyproj transformation
        return (lat, lon)
    
    def normalize_coordinates(
        self, 
        lat: float, 
        lon: float
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Normalize coordinate precision and validate.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Tuple of normalized (lat, lon) or (None, None) if invalid
        """
        try:
            lat = float(lat)
            lon = float(lon)
        except (ValueError, TypeError):
            logger.warning(f"Invalid coordinates: lat={lat}, lon={lon}")
            return None, None
        
        # Validate ranges
        if not (-90 <= lat <= 90):
            logger.warning(f"Latitude out of range: {lat}")
            return None, None
        if not (-180 <= lon <= 180):
            logger.warning(f"Longitude out of range: {lon}")
            return None, None
        
        # Round to 6 decimal places (~0.1m precision)
        lat = round(lat, 6)
        lon = round(lon, 6)
        
        return lat, lon
    
    def get_crs(self) -> str:
        """Return the standard CRS string."""
        return self.crs
