#!/usr/bin/env python3
"""
NETS Business Data Enhancement System - Main Entry Point
=========================================================

This is the primary command-line interface for the NETS Enhancement pipeline.
Supports both test mode (--test) and production mode.

Usage:
    # Test mode - uses small fixture data, no expensive API calls
    python main.py --test

    # Production mode - full NETS dataset
    python main.py --input data/raw/nets_minneapolis.csv

    # Production with options
    python main.py --input data/raw/nets.csv --skip linkedin wayback --verbose

Environment:
    Requires Python 3.11 (PyMC3 incompatible with 3.12+)
    API keys configured in .env file

Author: NETS Enhancement System
"""

import argparse
import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

def setup_logging(verbose: bool = False, log_file: Optional[str] = None) -> logging.Logger:
    """Configure logging for the application"""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_path = Path("logs") / log_file
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
    
    return logging.getLogger("NETS-Main")


# =============================================================================
# CLI ARGUMENT PARSER
# =============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="NETS Business Data Enhancement System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Test Mode (recommended for first run):
    python main.py --test
    python main.py --test --verbose
    python main.py --test --skip linkedin wayback

  Production Mode:
    python main.py --input data/raw/nets_minneapolis.csv
    python main.py --input data/raw/nets.csv --city Minneapolis
    python main.py --input data/raw/nets.csv --skip gpt --validate

  Available --skip options:
    linkedin   - Skip LinkedIn employee scraping
    wayback    - Skip Wayback Machine verification
    gpt        - Skip LLM entity resolution
    gmaps      - Skip Google Maps verification
    outscraper - Skip Outscraper review collection
    yelp       - Skip Yelp review collection
    employees  - Skip Bayesian employee estimation
    survival   - Skip survival status detection

  Output:
    Results saved to: data/processed/nets_enhanced_<city>_<timestamp>.parquet
    View results: streamlit run dashboard/app.py
"""
    )
    
    # Mode selection
    mode_group = parser.add_argument_group("Mode Selection")
    mode_group.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode with fixture data (no expensive API calls)"
    )
    
    # Input/Output
    io_group = parser.add_argument_group("Input/Output")
    io_group.add_argument(
        "--input", "-i",
        type=str,
        metavar="FILE",
        help="Path to input NETS CSV file (required for production mode)"
    )
    io_group.add_argument(
        "--output", "-o",
        type=str,
        metavar="FILE",
        help="Path to output Parquet file (auto-generated if not specified)"
    )
    io_group.add_argument(
        "--city",
        type=str,
        default="Minneapolis",
        help="City name for configuration (default: Minneapolis)"
    )
    
    # Processing options
    proc_group = parser.add_argument_group("Processing Options")
    proc_group.add_argument(
        "--skip",
        type=str,
        nargs="+",
        default=[],
        metavar="AGENT",
        help="Skip specific agents/operations (see --help for options)"
    )
    proc_group.add_argument(
        "--naics",
        type=str,
        nargs="+",
        default=["722513", "446110"],
        help="Target NAICS codes (default: 722513 446110)"
    )
    proc_group.add_argument(
        "--sample",
        type=int,
        metavar="N",
        help="Limit to N records for testing"
    )
    
    # Validation and output
    output_group = parser.add_argument_group("Validation and Output")
    output_group.add_argument(
        "--validate",
        action="store_true",
        help="Run data quality validation after processing"
    )
    output_group.add_argument(
        "--dashboard",
        action="store_true",
        help="Launch Streamlit dashboard after completion"
    )
    output_group.add_argument(
        "--export-csv",
        action="store_true",
        help="Also export results as CSV (in addition to Parquet)"
    )
    
    # Logging
    log_group = parser.add_argument_group("Logging")
    log_group.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose/debug logging"
    )
    log_group.add_argument(
        "--log-file",
        type=str,
        metavar="FILE",
        help="Write logs to file (in logs/ directory)"
    )
    log_group.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress non-essential output"
    )
    
    return parser


# =============================================================================
# CONFIGURATION VALIDATION
# =============================================================================

def check_environment() -> dict:
    """Check environment configuration and API keys"""
    env_status = {
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        "GOOGLE_MAPS_API_KEY": bool(os.getenv("GOOGLE_MAPS_API_KEY")),
        "YELP_API_KEY": bool(os.getenv("YELP_API_KEY")),
        "OUTSCRAPER_API_KEY": bool(os.getenv("OUTSCRAPER_API_KEY")),
        "LINKEDIN_EMAIL": bool(os.getenv("LINKEDIN_EMAIL")),
        "LINKEDIN_PASSWORD": bool(os.getenv("LINKEDIN_PASSWORD")),
    }
    return env_status


def validate_input_file(input_path: str) -> bool:
    """Validate input file exists and is readable"""
    path = Path(input_path)
    if not path.exists():
        return False
    if path.suffix.lower() != ".csv":
        return False
    return True


def get_test_fixture() -> Optional[Path]:
    """Get path to test fixture file"""
    fixture_paths = [
        PROJECT_ROOT / "tests" / "fixtures" / "nets_test_data.csv",
    ]
    for path in fixture_paths:
        if path.exists():
            return path
    return None


def generate_output_path(city: str, test_mode: bool = False) -> Path:
    """Generate output file path with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if test_mode:
        filename = f"nets_test_output_{timestamp}.parquet"
    else:
        filename = f"nets_enhanced_{city}_{timestamp}.parquet"
    return PROJECT_ROOT / "data" / "processed" / filename


# =============================================================================
# PIPELINE EXECUTION
# =============================================================================

def run_test_mode(args, logger: logging.Logger) -> int:
    """Run pipeline in test mode"""
    logger.info("=" * 70)
    logger.info("NETS ENHANCEMENT SYSTEM - TEST MODE")
    logger.info("=" * 70)
    
    # Check for test fixture
    fixture_path = get_test_fixture()
    if fixture_path is None and args.input is None:
        logger.error("Test mode requires test data.")
        logger.error("Please create: tests/fixtures/nets_test_data.csv")
        logger.error("Or specify --input with a test CSV file.")
        logger.info("\nRun 'python scripts/generate_sample_data.py' to see required schema.")
        return 1
    
    input_path = args.input or str(fixture_path)
    output_path = args.output or str(generate_output_path(args.city, test_mode=True))
    
    logger.info(f"Test input:  {input_path}")
    logger.info(f"Test output: {output_path}")
    
    # In test mode, skip expensive operations by default
    skip_ops = set(args.skip)
    if not args.skip:
        skip_ops = {"linkedin", "wayback", "gpt", "outscraper", "yelp"}
        logger.info(f"Test mode: auto-skipping expensive operations")
    
    logger.info(f"Skipping: {', '.join(sorted(skip_ops)) if skip_ops else 'none'}")
    
    # Run pipeline
    return execute_pipeline(
        input_path=input_path,
        output_path=output_path,
        city=args.city,
        naics_codes=args.naics,
        skip_operations=list(skip_ops),
        validate=args.validate,
        sample_size=args.sample,
        verbose=args.verbose,
        logger=logger
    )


def run_production_mode(args, logger: logging.Logger) -> int:
    """Run pipeline in production mode"""
    logger.info("=" * 70)
    logger.info("NETS ENHANCEMENT SYSTEM - PRODUCTION MODE")
    logger.info("=" * 70)
    
    # Validate input
    if not args.input:
        logger.error("Production mode requires --input argument")
        logger.error("Usage: python main.py --input data/raw/nets_minneapolis.csv")
        return 1
    
    if not validate_input_file(args.input):
        logger.error(f"Input file not found or not CSV: {args.input}")
        return 1
    
    input_path = args.input
    output_path = args.output or str(generate_output_path(args.city))
    
    logger.info(f"Input:  {input_path}")
    logger.info(f"Output: {output_path}")
    logger.info(f"City:   {args.city}")
    logger.info(f"NAICS:  {', '.join(args.naics)}")
    
    if args.skip:
        logger.info(f"Skipping: {', '.join(args.skip)}")
    
    # Check environment
    env_status = check_environment()
    available_apis = [k for k, v in env_status.items() if v]
    missing_apis = [k for k, v in env_status.items() if not v]
    
    logger.info(f"\nConfigured APIs: {', '.join(available_apis) if available_apis else 'none'}")
    if missing_apis:
        logger.warning(f"Missing API keys: {', '.join(missing_apis)}")
    
    # Run pipeline
    return execute_pipeline(
        input_path=input_path,
        output_path=output_path,
        city=args.city,
        naics_codes=args.naics,
        skip_operations=args.skip,
        validate=args.validate,
        sample_size=args.sample,
        verbose=args.verbose,
        logger=logger
    )


def execute_pipeline(
    input_path: str,
    output_path: str,
    city: str,
    naics_codes: List[str],
    skip_operations: List[str],
    validate: bool,
    sample_size: Optional[int],
    verbose: bool,
    logger: logging.Logger
) -> int:
    """Execute the data processing pipeline"""
    try:
        from src.data.pipeline import NETSDataPipeline
        
        start_time = datetime.now()
        logger.info(f"\nPipeline started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Create output directory
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize pipeline
        logger.info("\n[Phase 1] Loading NETS data...")
        pipeline = NETSDataPipeline(
            nets_csv_path=input_path,
            output_parquet_path=output_path,
            target_naics_codes=naics_codes
        )
        
        df = pipeline.load_and_filter(filter_by_zip=True, filter_active_only=True)
        logger.info(f"  Records loaded: {len(df)}")
        
        if df.empty:
            logger.error("No records found after filtering!")
            return 1
        
        # Sample if requested
        if sample_size and len(df) > sample_size:
            df = df.sample(n=sample_size, random_state=42)
            logger.info(f"  Sampled to: {sample_size} records")
        
        # Create geodataframe
        logger.info("\n[Phase 2] Creating geospatial structure...")
        gdf = pipeline.create_geodataframe()
        logger.info(f"  Geometries created: {len(gdf)}")
        
        # Employee estimation
        if "employees" not in skip_operations:
            logger.info("\n[Phase 3] Estimating employee counts...")
            df_employees = pipeline.estimate_employees()
            logger.info(f"  Mean estimate: {df_employees['employees_optimized'].mean():.1f}")
        else:
            logger.info("\n[Phase 3] Employee estimation: SKIPPED")
        
        # Survival detection
        if "survival" not in skip_operations:
            logger.info("\n[Phase 4] Detecting operational status...")
            df_survival = pipeline.detect_survival_status()
            active_pct = (df_survival['is_active_prob'] > 0.7).mean() * 100
            logger.info(f"  Likely active: {active_pct:.1f}%")
        else:
            logger.info("\n[Phase 4] Survival detection: SKIPPED")
        
        # Quality scoring
        logger.info("\n[Phase 5] Calculating quality scores...")
        df_quality = pipeline.calculate_composite_quality_score()
        avg_quality = df_quality['data_quality_score'].mean()
        logger.info(f"  Average quality: {avg_quality:.1f}/100")
        
        # Export
        logger.info("\n[Phase 6] Exporting results...")
        df_output = pipeline.prepare_parquet_output()
        pipeline.export_parquet(df_output)
        
        file_size = Path(output_path).stat().st_size / 1024 / 1024
        logger.info(f"  Output: {output_path}")
        logger.info(f"  Size: {file_size:.2f} MB")
        
        # Validation
        if validate:
            logger.info("\n[Phase 7] Validating output...")
            from src.data.nets_loader import NETSValidator
            is_valid, missing = NETSValidator.check_required_columns(df_output)
            if is_valid:
                logger.info("  Validation: PASSED")
            else:
                logger.warning(f"  Missing columns: {missing}")
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "=" * 70)
        logger.info("PIPELINE COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Records processed: {len(df_output)}")
        logger.info(f"Duration: {duration:.1f} seconds")
        logger.info(f"Output: {output_path}")
        logger.info("=" * 70)
        
        return 0
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Run: pip install -r requirements.txt")
        return 1
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        if verbose:
            import traceback
            logger.error(traceback.format_exc())
        return 1


def launch_dashboard(logger: logging.Logger):
    """Launch Streamlit dashboard"""
    import subprocess
    logger.info("\nLaunching dashboard at http://localhost:8501")
    logger.info("Press Ctrl+C to stop")
    try:
        subprocess.run(["streamlit", "run", "dashboard/app.py"])
    except KeyboardInterrupt:
        logger.info("Dashboard stopped")
    except Exception as e:
        logger.error(f"Failed to launch dashboard: {e}")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main() -> int:
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    log_file = args.log_file or (
        f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        if args.verbose else None
    )
    logger = setup_logging(verbose=args.verbose, log_file=log_file)
    
    # Print banner
    if not args.quiet:
        print()
        print("=" * 60)
        print("  NETS Business Data Enhancement System")
        print("  Statistical Employee Estimation and Status Detection")
        print("=" * 60)
        print()
    
    # Execute appropriate mode
    if args.test:
        exit_code = run_test_mode(args, logger)
    else:
        exit_code = run_production_mode(args, logger)
    
    # Launch dashboard if requested
    if exit_code == 0 and args.dashboard:
        launch_dashboard(logger)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
