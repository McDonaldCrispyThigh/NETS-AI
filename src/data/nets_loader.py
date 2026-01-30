"""
NETS Database Loader and Integration Module
Handles reading, parsing, and filtering NETS establishment records
Geographic filtering by Census Tract boundaries
Industry filtering by NAICS codes
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)


class NETSLoader:
    """Load and process NETS business establishment data"""
    
    def __init__(self, nets_csv_path: str, target_state: str = "MN"):
        """
        Initialize NETS data loader
        
        Args:
            nets_csv_path: Path to NETS establishments CSV file
            target_state: State abbreviation filter (default: MN)
        """
        self.nets_csv_path = nets_csv_path
        self.target_state = target_state
        self.df = None
        self.logger = logging.getLogger(__name__)
        
    def load_raw(self) -> pd.DataFrame:
        """
        Load raw NETS CSV file
        
        Returns:
            DataFrame with all NETS records
            
        Expected columns:
            - duns_id (unique identifier)
            - company_name
            - street_address, city, state, zip_code
            - latitude, longitude
            - naics_code (6-digit)
            - year_established, year_closed (if applicable)
            - employee_count (may be imputed)
        """
        try:
            self.df = pd.read_csv(self.nets_csv_path, dtype={
                'duns_id': str,
                'naics_code': str,
                'zip_code': str,
                'latitude': float,
                'longitude': float
            })
            self.logger.info(f"Loaded {len(self.df)} NETS records from {self.nets_csv_path}")
            return self.df
        except FileNotFoundError:
            self.logger.error(f"NETS file not found: {self.nets_csv_path}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading NETS data: {e}")
            raise
    
    def filter_by_state(self, state_code: str = None) -> pd.DataFrame:
        """
        Filter NETS records by state
        
        Args:
            state_code: State abbreviation (default: use initialized target_state)
            
        Returns:
            Filtered DataFrame
        """
        if self.df is None:
            self.load_raw()
        
        state = state_code or self.target_state
        initial_count = len(self.df)
        self.df = self.df[self.df['state'].str.upper() == state]
        self.logger.info(f"State filter ({state}): {initial_count} -> {len(self.df)} records")
        return self.df
    
    def filter_by_naics_codes(self, naics_codes: List[str]) -> pd.DataFrame:
        """
        Filter NETS records by NAICS codes
        
        Args:
            naics_codes: List of NAICS codes to include (e.g., ['722513', '446110'])
            
        Returns:
            Filtered DataFrame
        """
        if self.df is None:
            self.load_raw()
        
        # Ensure NAICS codes are strings
        naics_codes = [str(code) for code in naics_codes]
        
        initial_count = len(self.df)
        
        # Handle both exact match and prefix match (6-digit codes)
        self.df['naics_6digit'] = self.df['naics_code'].astype(str).str[:6]
        self.df = self.df[self.df['naics_6digit'].isin(naics_codes)]
        
        self.logger.info(
            f"NAICS filter ({', '.join(naics_codes)}): {initial_count} -> {len(self.df)} records"
        )
        return self.df
    
    def filter_by_census_tracts(self, tract_list: List[str]) -> pd.DataFrame:
        """
        Filter NETS records by Census Tract identifiers
        Requires tract assignment (e.g., from geocoding or external dataset)
        
        Args:
            tract_list: List of Census Tract FIPS codes
            
        Returns:
            Filtered DataFrame with tract assignments
        """
        if self.df is None:
            self.load_raw()
        
        if 'census_tract' not in self.df.columns:
            self.logger.warning("census_tract column not found - adding placeholder")
            self.df['census_tract'] = None
        
        initial_count = len(self.df)
        self.df = self.df[self.df['census_tract'].isin(tract_list)]
        self.logger.info(f"Census Tract filter: {initial_count} -> {len(self.df)} records")
        return self.df
    
    def filter_by_zip_codes(self, zip_codes: List[str]) -> pd.DataFrame:
        """
        Filter NETS records by ZIP codes
        
        Args:
            zip_codes: List of ZIP codes to include
            
        Returns:
            Filtered DataFrame
        """
        if self.df is None:
            self.load_raw()
        
        zip_codes = [str(z) for z in zip_codes]
        initial_count = len(self.df)
        self.df = self.df[self.df['zip_code'].astype(str).isin(zip_codes)]
        self.logger.info(f"ZIP code filter: {initial_count} -> {len(self.df)} records")
        return self.df
    
    def filter_active_only(self, year_threshold: int = 2015) -> pd.DataFrame:
        """
        Filter to establishments likely still active
        
        Args:
            year_threshold: Include only establishments opened after this year
            
        Returns:
            Filtered DataFrame
        """
        if self.df is None:
            self.load_raw()
        
        initial_count = len(self.df)
        
        # Remove records with year_closed in recent period (within 3 years)
        if 'year_closed' in self.df.columns:
            self.df = self.df[
                (self.df['year_closed'].isna()) | 
                (self.df['year_closed'] < 2023)
            ]
        
        # Optional: Filter by establishment year
        if 'year_established' in self.df.columns:
            self.df = self.df[
                (self.df['year_established'].isna()) |
                (self.df['year_established'] >= year_threshold)
            ]
        
        self.logger.info(f"Active filter: {initial_count} -> {len(self.df)} records")
        return self.df
    
    def get_geopandas_gdf(self, crs: str = "EPSG:4326") -> gpd.GeoDataFrame:
        """
        Convert DataFrame to GeoDataFrame with Point geometries
        
        Args:
            crs: Coordinate Reference System (default: EPSG:4326 WGS84)
            
        Returns:
            GeoDataFrame with geometry column
        """
        if self.df is None:
            self.load_raw()
        
        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(
            self.df,
            geometry=gpd.points_from_xy(self.df['longitude'], self.df['latitude']),
            crs=crs
        )
        
        self.logger.info(f"Created GeoDataFrame with {len(gdf)} records, CRS={crs}")
        return gdf
    
    def get_pipeline_ready(
        self,
        naics_codes: List[str],
        zip_codes: Optional[List[str]] = None,
        state_code: str = "MN",
        filter_active: bool = True
    ) -> pd.DataFrame:
        """
        Load and apply all standard filters in sequence
        
        Args:
            naics_codes: Target NAICS codes
            zip_codes: Geographic filter (optional)
            state_code: State abbreviation
            filter_active: Whether to filter to likely active establishments
            
        Returns:
            Filtered DataFrame ready for pipeline
        """
        self.load_raw()
        self.filter_by_state(state_code)
        self.filter_by_naics_codes(naics_codes)
        
        if zip_codes:
            self.filter_by_zip_codes(zip_codes)
        
        if filter_active:
            self.filter_active_only()
        
        self.logger.info(
            f"Pipeline-ready dataset: {len(self.df)} establishments "
            f"({', '.join(naics_codes)}) in {state_code}"
        )
        
        return self.df
    
    def get_summary_stats(self) -> dict:
        """
        Generate summary statistics of loaded data
        
        Returns:
            Dictionary with counts and distributions
        """
        if self.df is None:
            return {}
        
        stats = {
            "total_records": len(self.df),
            "by_naics": self.df['naics_code'].value_counts().to_dict(),
            "by_zip": self.df['zip_code'].value_counts().head(10).to_dict(),
            "has_coordinates": self.df[['latitude', 'longitude']].notna().all(axis=1).sum(),
            "has_phone": self.df['phone'].notna().sum() if 'phone' in self.df else 0,
            "has_website": self.df['website'].notna().sum() if 'website' in self.df else 0,
        }
        
        return stats


class NETSValidator:
    """Validate NETS data quality and consistency"""
    
    @staticmethod
    def check_required_columns(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Verify required columns exist
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, missing_columns)
        """
        required = [
            'duns_id', 'company_name', 'latitude', 'longitude',
            'naics_code', 'zip_code', 'state'
        ]
        missing = [col for col in required if col not in df.columns]
        return len(missing) == 0, missing
    
    @staticmethod
    def check_coordinates(df: pd.DataFrame) -> dict:
        """
        Validate coordinate fields
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        valid = (
            (df['latitude'].notna()) &
            (df['longitude'].notna()) &
            (df['latitude'].between(-90, 90)) &
            (df['longitude'].between(-180, 180))
        )
        
        return {
            "total": len(df),
            "valid_coordinates": valid.sum(),
            "missing_or_invalid": (~valid).sum(),
            "percent_valid": (valid.sum() / len(df) * 100) if len(df) > 0 else 0
        }
    
    @staticmethod
    def check_duplicates(df: pd.DataFrame, key_cols: List[str] = None) -> dict:
        """
        Check for duplicate records
        
        Args:
            df: DataFrame to validate
            key_cols: Columns to check for duplicates (default: duns_id)
            
        Returns:
            Dictionary with duplication statistics
        """
        if key_cols is None:
            key_cols = ['duns_id']
        
        duplicates = df.duplicated(subset=key_cols, keep=False).sum()
        
        return {
            "total": len(df),
            "duplicate_rows": duplicates,
            "unique_key_values": df[key_cols].drop_duplicates().shape[0],
            "percent_duplicates": (duplicates / len(df) * 100) if len(df) > 0 else 0
        }
