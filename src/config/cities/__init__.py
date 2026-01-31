"""
Multi-city configuration module.
Each city has its own configuration file with geographic bounds, NAICS targets, and baselines.
"""

from .minneapolis_mn import MINNEAPOLIS_CONFIG
from .denver_co import DENVER_CONFIG

CITY_CONFIGS = {
    "minneapolis": MINNEAPOLIS_CONFIG,
    "denver": DENVER_CONFIG,
}

def get_city_config(city_name: str) -> dict:
    """Get configuration for a specific city."""
    city_key = city_name.lower().replace(" ", "_")
    if city_key not in CITY_CONFIGS:
        raise ValueError(f"Unknown city: {city_name}. Available: {list(CITY_CONFIGS.keys())}")
    return CITY_CONFIGS[city_key]
