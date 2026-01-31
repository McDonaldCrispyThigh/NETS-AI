"""
City context manager for runtime configuration access.
Provides city-agnostic interface for all pipeline components.
All geographic data fetched dynamically - no hardcoded values.
"""

from typing import Dict, List, Tuple, Optional
from .dynamic_config import CityConfig, get_city_config


class CityContext:
    """
    Runtime context manager for city-specific configuration.
    Use this instead of hardcoded values throughout the codebase.
    All geographic boundaries and ZIP codes are fetched from external APIs.
    """
    
    _current_city_key: str = "minneapolis_mn"
    _config: Optional[CityConfig] = None
    
    @classmethod
    def set_city(cls, city_key: str) -> None:
        """
        Set the current city context.
        
        Args:
            city_key: City key in format 'city_state' (e.g., 'minneapolis_mn')
        """
        cls._current_city_key = city_key.lower()
        cls._config = get_city_config(city_key)
    
    @classmethod
    def get_config(cls) -> CityConfig:
        """Get current city configuration."""
        if cls._config is None:
            cls._config = get_city_config(cls._current_city_key)
        return cls._config
    
    @classmethod
    def get_city_name(cls) -> str:
        """Get current city name."""
        return cls.get_config().city_name
    
    @classmethod
    def get_state_code(cls) -> str:
        """Get current state code."""
        return cls.get_config().state
    
    @classmethod
    def get_geographic_bounds(cls) -> Optional[Tuple[float, float, float, float]]:
        """
        Get bounding box (min_lon, min_lat, max_lon, max_lat).
        Fetched dynamically from OpenStreetMap/Census.
        """
        return cls.get_config().get_bounds()
    
    @classmethod
    def get_target_zip_codes(cls) -> List[str]:
        """
        Get list of target ZIP codes.
        Fetched dynamically from Census ZCTA data.
        """
        return cls.get_config().get_zip_codes()
    
    @classmethod
    def get_naics_targets(cls) -> List[str]:
        """Get list of target NAICS codes."""
        return list(cls.get_config().naics_codes.keys())
    
    @classmethod
    def get_industry_baseline(cls, naics_code: str) -> Dict:
        """Get industry baseline for a specific NAICS code."""
        return cls.get_config().get_employee_baseline(naics_code)
    
    @classmethod
    def is_within_bounds(cls, lat: float, lon: float) -> bool:
        """Check if coordinates are within city bounds."""
        return cls.get_config().is_within_bounds(lat, lon)
    
    @classmethod
    def is_valid_zip(cls, zip_code: str) -> bool:
        """Check if ZIP code is in target list."""
        return cls.get_config().is_valid_zip(str(zip_code)[:5])
