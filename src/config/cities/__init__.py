"""
Multi-city configuration module.
All geographic data (bounds, ZIP codes) fetched dynamically from external APIs.
No hardcoded geographic constants.
"""

from .dynamic_config import (
    CityConfig,
    create_city_config,
    get_city_config,
    register_city_config,
    list_available_cities,
    DEFAULT_NAICS,
    DEFAULT_BASELINES,
)

__all__ = [
    "CityConfig",
    "create_city_config",
    "get_city_config",
    "register_city_config",
    "list_available_cities",
    "DEFAULT_NAICS",
    "DEFAULT_BASELINES",
]
