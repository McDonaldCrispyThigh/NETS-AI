"""
City context manager for runtime configuration access.
Provides city-agnostic interface for all pipeline components.
"""

from typing import Dict, List, Tuple, Optional
from . import get_city_config


class CityContext:
    """
    Runtime context manager for city-specific configuration.
    Use this instead of hardcoded values throughout the codebase.
    """
    
    _current_city: str = "minneapolis"
    _config: dict = None
    
    @classmethod
    def set_city(cls, city_name: str) -> None:
        """Set the current city context."""
        cls._current_city = city_name.lower()
        cls._config = get_city_config(city_name)
    
    @classmethod
    def get_config(cls) -> dict:
        """Get current city configuration."""
        if cls._config is None:
            cls._config = get_city_config(cls._current_city)
        return cls._config
    
    @classmethod
    def get_city_name(cls) -> str:
        """Get current city name."""
        return cls.get_config()["CITY_NAME"]
    
    @classmethod
    def get_state_code(cls) -> str:
        """Get current state code."""
        return cls.get_config()["STATE_CODE"]
    
    @classmethod
    def get_geographic_bounds(cls) -> Tuple[float, float, float, float]:
        """Get bounding box (min_lon, min_lat, max_lon, max_lat)."""
        return tuple(cls.get_config()["GEOGRAPHIC_BOUNDS"])
    
    @classmethod
    def get_target_zip_codes(cls) -> List[str]:
        """Get list of target ZIP codes."""
        return cls.get_config()["TARGET_ZIP_CODES"]
    
    @classmethod
    def get_naics_targets(cls) -> List[str]:
        """Get list of target NAICS codes."""
        return cls.get_config()["NAICS_TARGETS"]
    
    @classmethod
    def get_industry_baseline(cls, naics_code: str) -> Dict:
        """Get industry baseline for a specific NAICS code."""
        baselines = cls.get_config()["INDUSTRY_BASELINES"]
        return baselines.get(naics_code, {})
    
    @classmethod
    def is_within_bounds(cls, lat: float, lon: float) -> bool:
        """Check if coordinates are within city bounds."""
        min_lon, min_lat, max_lon, max_lat = cls.get_geographic_bounds()
        return min_lon <= lon <= max_lon and min_lat <= lat <= max_lat
    
    @classmethod
    def is_valid_zip(cls, zip_code: str) -> bool:
        """Check if ZIP code is in target list."""
        return str(zip_code)[:5] in cls.get_target_zip_codes()
