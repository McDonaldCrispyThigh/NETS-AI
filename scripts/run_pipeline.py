"""
NETS Pipeline Runner - Execute complete data processing workflow
Complete end-to-end processing from NETS CSV to Parquet export
"""

import argparse
import logging
from pathlib import Path
import sys
from datetime import datetime
import traceback

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.pipeline import NETSDataPipeline
from src.utils.logger import setup_logger

logger = setup_logger("NETSPipelineRunner")


def create_argument_parser():
    """Create CLI argument parser"""
    parser = argparse.ArgumentParser(
        description="NETS Business Data Enhancement Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with sample data
  python run_pipeline.py --input data/raw/nets_minneapolis_sample.csv

  # Run with real NETS data and custom output
  python run_pipeline.py \\
    --input data/raw/nets_minneapolis_full.csv \\
    --output data/processed/nets_enhanced_20260130.parquet \\
    --validate \\
    --verbose

  # Run with specific NAICS codes
  python run_pipeline.py \\
    --input data/raw/nets.csv \\
    --naics 722513 446110

  # Generate sample data first, then run pipeline
  python scripts/generate_sample_data.py
  python run_pipeline.py --input data/raw/nets_minneapolis_sample.csv --dashboard
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        required=True,
        help='Path to input NETS CSV file'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='data/processed/nets_ai_minneapolis.parquet',
        help='Path to output Parquet file (default: data/processed/nets_ai_minneapolis.parquet)'
    )
    
    parser.add_argument(
        '--naics',
        type=str,
        nargs='+',
        default=['722513', '446110'],
        help='Target NAICS codes (default: 722513 446110)'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Run data quality validation before export'
    )
    
    parser.add_argument(
        '--dashboard',
        action='store_true',
        help='Launch Streamlit dashboard after pipeline completes'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--sample-size',
        type=int,
        default=None,
        help='Limit to N records for testing (optional)'
    )
    
    return parser


def validate_input(input_path: str) -> bool:
    """Validate input file exists and is readable"""
    try:
        path = Path(input_path)
        if not path.exists():
            logger.error(f"Input file not found: {input_path}")
            return False
        if path.suffix.lower() != '.csv':
            logger.error(f"Input file must be CSV: {input_path}")
            return False
        logger.info(f"Input file validated: {input_path}")
        return True
    except Exception as e:
        logger.error(f"Error validating input: {e}")
        return False


def run_pipeline(
    input_path: str,
    output_path: str,
    naics_codes: list,
    validate: bool = False,
    sample_size: int = None,
    verbose: bool = False
) -> bool:
    """
    Run the NETS data enhancement pipeline
    
    Args:
        input_path: Input CSV file path
        output_path: Output Parquet file path
        naics_codes: List of NAICS codes to process
        validate: Whether to run validation
        sample_size: Optional limit on records
        verbose: Enable verbose logging
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("="*70)
        logger.info("NETS BUSINESS DATA ENHANCEMENT PIPELINE")
        logger.info("="*70)
        logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Validate input
        if not validate_input(input_path):
            return False
        
        # Create output directory
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")
        
        # Initialize pipeline
        logger.info(f"Initializing pipeline with NAICS codes: {naics_codes}")
        pipeline = NETSDataPipeline(
            nets_csv_path=input_path,
            output_parquet_path=output_path,
            target_naics_codes=naics_codes
        )
        
        # Load and filter data
        logger.info("\nPhase 1: Loading and filtering NETS data...")
        df = pipeline.load_and_filter(filter_by_zip=True, filter_active_only=True)
        logger.info(f"Records after filtering: {len(df)}")
        
        if df.empty:
            logger.error("No records found after filtering!")
            return False
        
        # Apply sample size if specified
        if sample_size and len(df) > sample_size:
            logger.info(f"Limiting to sample size: {sample_size}")
            df = df.sample(n=sample_size, random_state=42)
        
        # Create geodataframe
        logger.info("\nPhase 2: Creating geospatial data structure...")
        gdf = pipeline.create_geodataframe()
        logger.info(f"GeoDataFrame created with {len(gdf)} geometries")
        
        # Estimate employees
        logger.info("\nPhase 3: Estimating employee counts...")
        df_with_employees = pipeline.estimate_employees()
        logger.info(f"Employee estimates completed")
        logger.info(f"  Mean employees: {df_with_employees['employees_optimized'].mean():.1f}")
        logger.info(f"  Median employees: {df_with_employees['employees_optimized'].median():.1f}")
        
        # Detect survival status
        logger.info("\nPhase 4: Detecting business survival status...")
        df_with_survival = pipeline.detect_survival_status()
        active_pct = (df_with_survival['is_active_prob'] > 0.7).sum() / len(df_with_survival) * 100
        logger.info(f"Survival detection completed")
        logger.info(f"  Likely active (>0.7): {active_pct:.1f}%")
        
        # Calculate quality score
        logger.info("\nPhase 5: Calculating data quality scores...")
        df_with_quality = pipeline.calculate_composite_quality_score()
        avg_quality = df_with_quality['data_quality_score'].mean()
        logger.info(f"Quality calculation completed")
        logger.info(f"  Average quality score: {avg_quality:.1f}/100")
        
        # Prepare and export
        logger.info("\nPhase 6: Preparing Parquet output...")
        df_output = pipeline.prepare_parquet_output()
        
        logger.info(f"Exporting to {output_path}...")
        pipeline.export_parquet(df_output)
        logger.info("✓ Export completed successfully")
        
        # Validation
        if validate:
            logger.info("\nPhase 7: Running validation checks...")
            from src.data.nets_loader import NETSValidator
            
            is_valid, missing_cols = NETSValidator.check_required_columns(df_output)
            if not is_valid:
                logger.warning(f"Missing columns: {missing_cols}")
            else:
                logger.info("✓ All required columns present")
        
        # Summary statistics
        logger.info("\n" + "="*70)
        logger.info("PIPELINE EXECUTION SUMMARY")
        logger.info("="*70)
        logger.info(f"Total records processed: {len(df_output)}")
        logger.info(f"Output file size: {Path(output_path).stat().st_size / 1024 / 1024:.2f} MB")
        logger.info(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*70)
        
        return True
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        logger.error(traceback.format_exc())
        return False


def launch_dashboard(parquet_path: str):
    """Launch Streamlit dashboard"""
    import subprocess
    try:
        logger.info("\nLaunching Streamlit dashboard...")
        logger.info("Dashboard URL: http://localhost:8501")
        logger.info("Press Ctrl+C to stop the dashboard")
        subprocess.run([
            'streamlit', 'run',
            'dashboard/app.py',
            '--logger.level=warning'
        ])
    except Exception as e:
        logger.error(f"Failed to launch dashboard: {e}")
        logger.info("You can manually start the dashboard with:")
        logger.info("  streamlit run dashboard/app.py")


def main():
    """Main entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info(f"Command line arguments: {args}")
    
    # Run pipeline
    success = run_pipeline(
        input_path=args.input,
        output_path=args.output,
        naics_codes=args.naics,
        validate=args.validate,
        sample_size=args.sample_size,
        verbose=args.verbose
    )
    
    if success:
        logger.info("\n✓ Pipeline completed successfully!")
        
        # Launch dashboard if requested
        if args.dashboard:
            launch_dashboard(args.output)
        else:
            logger.info("\nTo view results, run:")
            logger.info(f"  streamlit run dashboard/app.py")
        
        return 0
    else:
        logger.error("\n✗ Pipeline execution failed!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
