"""
NETS Business Data Enhancement Pipeline
End-to-end data processing: load NETS -> enrich with multi-source data -> output Parquet
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
from datetime import datetime
import logging
from typing import Optional, Dict, List
import json

logger = logging.getLogger(__name__)

# Import custom modules
from src.config import (
    INDUSTRY_CONFIG, PARQUET_OUTPUT_SCHEMA, DEFAULT_PARQUET_OUTPUT,
    DATA_SOURCE_PRIORITY, EMPLOYEE_ESTIMATION_BASELINES, TARGET_ZIP_CODES
)
from src.data.nets_loader import NETSLoader, NETSValidator
from src.models.bayesian_employee_estimator import EmployeeEstimator
from src.models.survival_detector import SurvivalDetector
from src.utils.logger import setup_logger


class NETSDataPipeline:
    """
    End-to-end pipeline for NETS data enrichment
    Workflow: Load NETS -> Filter -> Enrich -> Model -> Export Parquet
    """
    
    def __init__(
        self,
        nets_csv_path: str,
        output_parquet_path: str = DEFAULT_PARQUET_OUTPUT,
        target_naics_codes: List[str] = None
    ):
        """
        Initialize pipeline
        
        Args:
            nets_csv_path: Path to NETS CSV file
            output_parquet_path: Output Parquet file path
            target_naics_codes: NAICS codes to focus on (default: ['722513', '446110'])
        """
        self.nets_csv_path = nets_csv_path
        self.output_parquet = output_parquet_path
        self.target_naics = target_naics_codes or ['722513', '446110']
        self.logger = setup_logger("NETSPipeline")
        
        # Initialize components
        self.nets_loader = NETSLoader(nets_csv_path)
        self.employee_estimator = EmployeeEstimator(EMPLOYEE_ESTIMATION_BASELINES)
        self.survival_detector = SurvivalDetector()
        
        self.df = None  # Working DataFrame
        self.gdf = None  # GeoDataFrame for spatial operations
    
    def load_and_filter(
        self,
        filter_by_zip: bool = True,
        filter_active_only: bool = True
    ) -> pd.DataFrame:
        """
        Load NETS data and apply geographic + industry filters
        
        Args:
            filter_by_zip: Apply Minneapolis ZIP code filter
            filter_active_only: Filter to likely active establishments
            
        Returns:
            Filtered DataFrame
        """
        self.logger.info("Loading NETS data...")
        self.df = self.nets_loader.load_raw()
        
        self.logger.info(f"Initial records: {len(self.df)}")
        
        # Industry filter
        self.logger.info(f"Filtering to NAICS codes: {self.target_naics}")
        self.df = self.nets_loader.filter_by_naics_codes(self.target_naics)
        
        # Geographic filter
        if filter_by_zip:
            self.logger.info(f"Filtering to Minneapolis ZIP codes")
            self.df = self.nets_loader.filter_by_zip_codes(TARGET_ZIP_CODES)
        
        # Active filter
        if filter_active_only:
            self.logger.info("Filtering to likely active establishments")
            self.df = self.nets_loader.filter_active_only()
        
        self.logger.info(f"After filtering: {len(self.df)} records")
        return self.df
    
    def create_geodataframe(self, crs: str = "EPSG:4326") -> gpd.GeoDataFrame:
        """
        Convert to GeoDataFrame for spatial operations
        
        Args:
            crs: Coordinate Reference System
            
        Returns:
            GeoDataFrame with Point geometries
        """
        self.logger.info("Creating GeoDataFrame...")
        self.gdf = self.nets_loader.get_geopandas_gdf(crs=crs)
        self.logger.info(f"GeoDataFrame created: {len(self.gdf)} records with CRS {crs}")
        return self.gdf
    
    def deduplicate(self, key_columns: List[str] = None) -> pd.DataFrame:
        """
        Remove duplicate records based on key columns
        
        Args:
            key_columns: Columns to use for deduplication (default: ['duns_id'])
            
        Returns:
            Deduplicated DataFrame
        """
        if key_columns is None:
            key_columns = ['duns_id']
        
        initial_count = len(self.df)
        self.df = self.df.drop_duplicates(subset=key_columns, keep='first')
        
        self.logger.info(f"Deduplication: {initial_count} -> {len(self.df)} records")
        return self.df
    
    def validate_data_quality(self) -> Dict:
        """
        Validate data quality before modeling
        
        Returns:
            Dictionary with validation results
        """
        self.logger.info("Validating data quality...")
        
        is_valid, missing = NETSValidator.check_required_columns(self.df)
        if not is_valid:
            self.logger.warning(f"Missing required columns: {missing}")
        
        coords_check = NETSValidator.check_coordinates(self.df)
        self.logger.info(f"Coordinate validation: {coords_check['percent_valid']:.1f}% valid")
        
        dup_check = NETSValidator.check_duplicates(self.df)
        self.logger.info(f"Duplicates: {dup_check['duplicate_rows']} rows ({dup_check['percent_duplicates']:.2f}%)")
        
        return {
            'valid_columns': is_valid,
            'coordinates': coords_check,
            'duplicates': dup_check
        }
    
    def enrich_with_external_sources(
        self,
        linkedin_data_path: Optional[str] = None,
        outscraper_data_path: Optional[str] = None,
        job_postings_path: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Merge external data sources with NETS records
        
        Args:
            linkedin_data_path: Path to LinkedIn employee count data
            outscraper_data_path: Path to Outscraper Google reviews
            job_postings_path: Path to job posting data
            
        Returns:
            Enriched DataFrame
        """
        self.logger.info("Enriching with external data sources...")
        
        # LinkedIn enrichment
        if linkedin_data_path and Path(linkedin_data_path).exists():
            self.logger.info("Loading LinkedIn data...")
            linkedin_df = pd.read_csv(linkedin_data_path)
            self.df = self.df.merge(
                linkedin_df[['duns_id', 'linkedin_headcount', 'linkedin_url']],
                on='duns_id',
                how='left'
            )
            self.logger.info(f"LinkedIn match rate: {self.df['linkedin_headcount'].notna().sum() / len(self.df) * 100:.1f}%")
        
        # Outscraper reviews enrichment
        if outscraper_data_path and Path(outscraper_data_path).exists():
            self.logger.info("Loading Outscraper reviews...")
            reviews_df = pd.read_csv(outscraper_data_path)
            self.df = self.df.merge(
                reviews_df[[
                    'duns_id', 'review_count_3m', 'review_count_6_12m',
                    'last_review_date', 'avg_rating'
                ]],
                on='duns_id',
                how='left'
            )
        
        # Job postings enrichment
        if job_postings_path and Path(job_postings_path).exists():
            self.logger.info("Loading job posting data...")
            postings_df = pd.read_csv(job_postings_path)
            self.df = self.df.merge(
                postings_df[['duns_id', 'job_postings_6m', 'job_postings_peak']],
                on='duns_id',
                how='left'
            )
        
        self.logger.info(f"Enrichment complete: {len(self.df)} records")
        return self.df
    
    def estimate_employees(self) -> pd.DataFrame:
        """
        Run employee estimation for all records
        
        Returns:
            DataFrame with employee estimates
        """
        self.logger.info("Estimating employee counts...")
        
        # Process by NAICS code for category-specific baselines
        for naics_code in self.target_naics:
            mask = self.df['naics_code'].astype(str).str.startswith(naics_code)
            naics_count = mask.sum()
            
            if naics_count == 0:
                continue
            
            self.logger.info(f"Processing {naics_count} establishments with NAICS {naics_code}")
            
            # Process batch
            subset = self.df[mask].reset_index(drop=True)
            enriched = self.employee_estimator.process_batch(subset, naics_code)
            
            # Merge results back
            self.df.loc[mask, enriched.columns[len(subset.columns):]] = enriched.iloc[:, len(subset.columns):].values
        
        self.logger.info("Employee estimation complete")
        return self.df
    
    def detect_survival_status(self) -> pd.DataFrame:
        """
        Run business survival detection for all records
        
        Returns:
            DataFrame with survival probabilities
        """
        self.logger.info("Detecting business survival status...")
        
        enriched = self.survival_detector.process_batch(self.df)
        
        # Merge results
        survival_cols = [col for col in enriched.columns if 'survival' in col or 'is_active' in col]
        self.df[survival_cols] = enriched[survival_cols]
        
        self.logger.info(f"Survival detection complete: {(enriched['is_active_prob'] > 0.7).sum()} likely active")
        return self.df
    
    def calculate_composite_quality_score(self) -> pd.DataFrame:
        """
        Calculate overall data quality score (0-100)
        
        Factors:
            - Completeness of fields (20%)
            - Source diversity (20%)
            - Signal confidence (30%)
            - Estimate certainty (30%)
            
        Returns:
            DataFrame with quality_score column
        """
        self.logger.info("Calculating data quality scores...")
        
        scores = []
        
        for _, row in self.df.iterrows():
            # Completeness (20%): ratio of non-null fields
            total_fields = len(row)
            non_null = row.notna().sum()
            completeness = (non_null / total_fields) * 20
            
            # Source diversity (20%): count of different data sources
            sources_count = 0
            if pd.notna(row.get('linkedin_headcount')):
                sources_count += 1
            if pd.notna(row.get('review_count_3m')):
                sources_count += 1
            if pd.notna(row.get('job_postings_6m')):
                sources_count += 1
            diversity_score = min(sources_count * 5, 20)
            
            # Signal confidence (30%): average confidence from models
            confidence_map = {'high': 30, 'medium': 20, 'low': 10}
            emp_conf = confidence_map.get(row.get('employees_confidence'), 10)
            surv_conf = confidence_map.get(row.get('is_active_confidence'), 10)
            signal_conf = (emp_conf + surv_conf) / 2
            
            # Estimate certainty (30%): CI width inversely related
            ci_width_score = 30  # Default
            if pd.notna(row.get('employees_ci_upper')) and pd.notna(row.get('employees_ci_lower')):
                estimate = row.get('employees_optimized', 1)
                if estimate > 0:
                    ci_width = row['employees_ci_upper'] - row['employees_ci_lower']
                    width_ratio = ci_width / estimate
                    ci_width_score = max(10, 30 - (width_ratio * 15))  # Narrower CI = higher score
            
            total_score = completeness + diversity_score + signal_conf + ci_width_score
            scores.append(min(total_score, 100))
        
        self.df['data_quality_score'] = scores
        self.logger.info(f"Quality scores calculated: mean={np.mean(scores):.1f}")
        
        return self.df
    
    def prepare_parquet_output(self) -> pd.DataFrame:
        """
        Prepare DataFrame for Parquet export
        Select and order columns per schema specification
        
        Returns:
            DataFrame with columns in PARQUET_OUTPUT_SCHEMA order
        """
        self.logger.info("Preparing Parquet output schema...")
        
        # Start with available columns from schema
        available_cols = [col for col in PARQUET_OUTPUT_SCHEMA if col in self.df.columns]
        
        # Add any columns not in schema that are valuable
        existing_cols = set(self.df.columns)
        extra_cols = list(existing_cols - set(available_cols))
        
        output_cols = available_cols + extra_cols
        
        # Create final DataFrame
        output_df = self.df[output_cols].copy()
        
        # Add export metadata
        output_df['data_export_date'] = datetime.now().isoformat()
        output_df['data_export_source'] = 'NETS AI Enhancement Pipeline v1.0'
        
        self.logger.info(f"Parquet output prepared: {len(output_df)} records, {len(output_df.columns)} columns")
        return output_df
    
    def export_parquet(
        self,
        df: pd.DataFrame,
        compression: str = 'snappy',
        index: bool = False
    ) -> Path:
        """
        Export DataFrame to Parquet format
        
        Args:
            df: DataFrame to export
            compression: Compression algorithm ('snappy', 'gzip', None)
            index: Include index in output
            
        Returns:
            Path to exported file
        """
        output_path = Path(self.output_parquet)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Exporting to Parquet: {output_path}")
        
        try:
            df.to_parquet(
                output_path,
                compression=compression,
                index=index,
                engine='pyarrow'
            )
            
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            self.logger.info(f"Parquet export complete: {file_size_mb:.1f} MB")
            
            return output_path
        except Exception as e:
            self.logger.error(f"Error exporting Parquet: {e}")
            raise
    
    def run(
        self,
        linkedin_data: Optional[str] = None,
        outscraper_data: Optional[str] = None,
        job_postings_data: Optional[str] = None,
        validate: bool = True
    ) -> Path:
        """
        Execute complete pipeline
        
        Args:
            linkedin_data: Path to LinkedIn data file (optional)
            outscraper_data: Path to Outscraper reviews file (optional)
            job_postings_data: Path to job postings file (optional)
            validate: Run data validation checks
            
        Returns:
            Path to output Parquet file
        """
        self.logger.info("=" * 80)
        self.logger.info("NETS Business Data Enhancement Pipeline - Starting")
        self.logger.info("=" * 80)
        
        # Step 1: Load and filter
        self.load_and_filter()
        self.deduplicate()
        
        # Step 2: Validate (optional)
        if validate:
            self.validate_data_quality()
        
        # Step 3: Create spatial representation
        self.create_geodataframe()
        
        # Step 4: Enrich with external data
        self.enrich_with_external_sources(
            linkedin_data_path=linkedin_data,
            outscraper_data_path=outscraper_data,
            job_postings_path=job_postings_data
        )
        
        # Step 5: Model predictions
        self.estimate_employees()
        self.detect_survival_status()
        
        # Step 6: Quality scoring
        self.calculate_composite_quality_score()
        
        # Step 7: Prepare output
        output_df = self.prepare_parquet_output()
        
        # Step 8: Export
        output_file = self.export_parquet(output_df)
        
        self.logger.info("=" * 80)
        self.logger.info(f"Pipeline complete - Output: {output_file}")
        self.logger.info("=" * 80)
        
        return output_file


if __name__ == "__main__":
    # Example usage
    pipeline = NETSDataPipeline(
        nets_csv_path="data/raw/nets_minneapolis.csv",
        output_parquet_path="data/processed/nets_ai_minneapolis.parquet"
    )
    
    output = pipeline.run()
    print(f"Pipeline output: {output}")
