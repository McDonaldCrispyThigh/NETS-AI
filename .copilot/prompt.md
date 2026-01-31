# NETS Business Data Enhancement System - Development Context for Code Generation

## Project Identity
Project Name: NETS Business Data Enhancement System
Repository URL: https://github.com/McDonaldCrispyThigh/NETS-AI/
Documentation Version: January 31 2026
License: MIT

Note: Repository name contains historical identifier. All code artifacts, documentation, and commit messages must avoid the string "AI" per project constraints. Use "enhancement", "computational", or "statistical" as alternatives.

## Core Research Objective
Develop an extensible computational pipeline to enhance the National Establishment Time-Series (NETS) database through multi-source signal integration for two specific applications:
1. Employee count estimation with quantified uncertainty intervals
2. Business operational status detection to reduce closure reporting lag compared to standard NETS updates

## Strict Scope Constraints
Primary Deployment City: Minneapolis Minnesota (Census Tract boundaries; ZIP codes 55401-55415)
Target Industries: 
  - NAICS 722513 (Limited-Service Restaurants / Quick Service Restaurants)
  - NAICS 446110 (Pharmacies and Drug Stores)
Excluded Categories: Coffee shops (NAICS 722515), fitness centers (NAICS 713940), and all other NAICS codes outside primary scope
Sample Size Target: 500-1000 establishments per city (minimum viable product scale)
Primary Data Source: NETS database snapshot (external signals supplement but never replace NETS records)

## Multi-City Extensibility Requirements
The system must support deployment to additional cities (e.g., Denver Colorado) without code modifications. All city-specific parameters must be externalized:

City Configuration Structure (src/config/cities/):
  minneapolis_mn.py    # Minneapolis configuration module
  denver_co.py         # Denver configuration module (template provided)
  city_registry.py     # City metadata registry and validation

Required City Parameters (all configurable via Python module):
  - city_name: "Minneapolis"
  - state_abbr: "MN"
  - state_full: "Minnesota"
  - target_zip_codes: List[str] (e.g., ["55401", "55402", ..., "55415"])
  - census_tract_filter: Optional[Callable] for boundary validation
  - geographic_bounds: Tuple[float, float, float, float] (min_lon, min_lat, max_lon, max_lat)
  - naics_targets: List[int] (default: [722513, 446110])
  - industry_baselines: Dict[int, float] (employee/review density baselines per NAICS)
  - coordinate_validation: Callable[[float, float], bool] for boundary checking

Pipeline Execution Protocol:
  python scripts/run_pipeline.py --city minneapolis --input nets_snapshot.csv
  python scripts/run_pipeline.py --city denver --input nets_snapshot.csv

All hard-coded city references prohibited. Geographic operations must use abstract interfaces:
  - src/geospatial/boundary_validator.py (city-agnostic validation)
  - src/geospatial/coordinate_transformer.py (EPSG:4326 enforcement)
  - src/geospatial/distance_calculator.py (haversine implementation)

## Mandatory Technical Specifications
Python Environment: Version 3.11 (required for PyMC3 compatibility; versions 3.12+ prohibited)
Coordinate System: EPSG:4326 (WGS84) for all geospatial operations
Address Matching Protocol: Haversine distance threshold less than 50 meters combined with fuzzy string matching
Temporal Alignment: Monthly period aggregation using pandas to_period('M') method
Uncertainty Quantification: All numerical estimates must include 95 percent confidence intervals via bootstrap resampling or Bayesian posterior distributions
Output Format: Apache Parquet (primary); CSV permitted only as secondary export option
Required Output Columns:
  - employees_optimized (point estimate)
  - employees_lower_ci (lower 95 percent confidence bound)
  - employees_upper_ci (upper 95 percent confidence bound)
  - is_active_prob (operational probability 0.0-1.0)
  - confidence_level (categorical: high/medium/low)
  - data_quality_score (composite metric 0-100)
  - city_name (deployment city identifier)
  - census_tract_id (geographic unit for health equity analysis)

## File Organization Standards
All project files must adhere to the following directory structure without deviation:

NETS-AI/
  requirements.txt
  .env.example
  .gitignore
  LICENSE
  README.md
  scripts/
    run_pipeline.py          # Parameterized entry point (--city, --input, --sample-size)
    filter_nets_snapshot.py  # City-aware NETS filtering utility
    validate_environment.py  # Dependency checker
    generate_sample_data.py  # Schema documentation generator
    deploy_to_city.py        # City deployment automation script
  src/
    config/
      __init__.py            # Configuration loader
      pipeline_settings.py   # Global parameters
      cities/                # City configuration modules
        __init__.py
        minneapolis_mn.py
        denver_co.py
        city_registry.py
        city_factory.py      # City configuration instantiation
    geospatial/              # City-agnostic geographic utilities
      boundary_validator.py
      coordinate_transformer.py
      distance_calculator.py
      census_tract_mapper.py
    pipeline.py              # Core orchestration logic (city-parameterized)
    agents/                  # Data collection modules (city-aware)
      google_maps_agent.py
      outscraper_agent.py
      linkedin_scraper.py
      wayback_agent.py
      language_model_analyzer.py
    data/
      nets_loader.py         # NETS ingestion with city filtering
      external_signals.py    # Supplementary data integration
      validator.py           # Output quality assurance
    models/
      bayesian_employee_estimator.py
      survival_detector.py
      employee_estimator.py
    utils/
      logger.py
      helpers.py
      city_context.py        # Runtime city context manager
  data/
    raw/                   # NETS input files (git-ignored; organized by city)
      minneapolis/
      denver/
    processed/             # Parquet outputs (git-ignored; city namespaced)
      nets_enhanced_minneapolis.parquet
      nets_enhanced_denver.parquet
    reviews/               # Review timeseries JSON (git-ignored; city namespaced)
    outputs/               # Analysis figures (git-ignored; city namespaced)
  tests/
    fixtures/              # Test datasets (city-specific subdirectories)
    test_geospatial.py     # City-agnostic geographic tests
    test_city_config.py    # City configuration validation
    test_pipeline.py
  dashboard/
    app.py                 # Streamlit visualization (city selector interface)
  docs/
    QUICKSTART.md
    MULTI_CITY_DEPLOYMENT.md  # Denver deployment guide
    TESTING.md
    USAGE.md
    IMPLEMENTATION_STATUS.md
    api_costs_breakdown.md
    SYSTEM_REFERENCE.md
  notebooks/
    01_crane_decker_replication.ipynb
    02_minneapolis_pilot.ipynb
    03_denver_deployment_template.ipynb
    04_cross_city_comparison.ipynb
    05_statistical_validation.ipynb

## Automation and Maintainability Standards
Parameterization Principle: All city-specific values must be configurable without code changes
  - Prohibited: Hard-coded ZIP code lists in pipeline logic
  - Required: Configuration-driven filtering via city modules

Deployment Automation:
  - scripts/deploy_to_city.py must accept --city parameter and execute full pipeline
  - Must validate city configuration completeness before execution
  - Must generate city-specific output paths automatically

Testing Requirements:
  - tests/test_city_config.py must validate all city modules against schema
  - Must include Denver configuration template with placeholder values
  - Cross-city regression tests required before merging to main branch

Documentation Standards:
  - docs/MULTI_CITY_DEPLOYMENT.md must contain step-by-step Denver deployment guide
  - Each city configuration module requires docstring with data source references
  - notebooks/03_denver_deployment_template.ipynb must demonstrate parameterization

## GitHub Workflow Requirements
Commit Frequency: After each discrete analysis phase completion (minimum once per agent execution cycle)
Commit Message Format:
  - Must use imperative mood ("Add feature" not "Added feature")
  - Maximum 72 characters per line
  - First line summary only (no body required for routine commits)
  - Examples of valid commits:
      "Implement city configuration registry"
      "Add Denver deployment template with boundary parameters"
      "Parameterize pipeline for multi-city execution"
      "Fix coordinate validation in boundary validator module"
  - Prohibited elements in commits:
      * Emoji characters of any kind
      * Chinese or non-English text
      * The literal string "AI" in any case variation
      * Marketing language ("revolutionary", "game-changing")
Push Protocol: Push to main branch after each commit; no long-lived feature branches permitted for MVP development phase
Branch Protection: main branch requires passing tests for at least two city configurations (Minneapolis + Denver template)

## Absolute Prohibitions
The following elements are strictly forbidden in all project artifacts:
1. Emoji characters in any file (source code, documentation, commit messages, filenames)
2. Chinese language text or any non-English content except proper nouns (e.g., "Minneapolis", "Denver")
3. The string "AI" in any case variation ("ai", "Ai", "aI") across all contexts:
   - Replace with: "computational", "statistical", "automated", "model-based", "enhancement", or domain-specific terms
   - Examples:
        * "AI analysis" → "statistical analysis" or "language model analysis"
        * "AI status" → "operational status"
        * "AI-BDD" → "enhanced business database" or "NETS-Enhanced"
        * Project references must use "NETS Enhancement System" not "NETS AI"
        * Repository URL contains historical identifier but code/docs must avoid the term
4. Scope deviations from target industries (NAICS 722513/446110) without explicit advisor approval
5. Python version 3.12 or higher (PyMC3 compatibility constraint)
6. Hard-coded city parameters in pipeline logic (all geographic parameters must be configuration-driven)

## Current Implementation Phase
Phase 4: Model Development (January 2026)
Completed Milestones:
  - Phase 0: Environment setup and NETS ingestion framework
  - Phase 1: Multi-source data collection infrastructure
  - Phase 2: Address parsing and coordinate standardization
  - Phase 3: Feature engineering (review decay, hiring activity)
Current Focus:
  - Bayesian hierarchical employee estimation with NAICS-stratified priors
  - Random forest survival classification using review decay signals
  - Bootstrap confidence interval generation for all estimates
  - City configuration abstraction layer implementation
Next Milestone:
  - Phase 5: Signal fusion protocol and Parquet export validation
  - Phase 6: Health equity validation (food environment index, pharmacy access metrics)
  - Denver deployment validation (full pipeline execution on template configuration)

## Health Equity Validation Requirements
All model outputs must support downstream public health analysis across cities:
1. Food Environment Index: Census tract-level fast food density calculations weighted by operational probability
2. Pharmacy Desert Analysis: Identification of tracts with less than one operational pharmacy per 10000 residents
3. Zombie Lag Quantification: Measurement of closure detection improvement versus standard NETS updates (target: reduce 24-month lag to under 6 months)
4. Cross-City Comparability: Standardized metrics enabling Minneapolis-Denver comparisons
5. Validation Protocol: Manual ground truth verification of 100 randomly sampled establishments per city

## Contextual Usage Instructions for Code Generation
When generating code suggestions:
1. Always preserve NETS as primary data source; external signals are supplementary only
2. Enforce 95 percent confidence interval generation for all numerical estimates
3. Validate geographic coordinates against current city boundaries before processing
4. Apply NAICS-specific modeling parameters where applicable (separate baselines for 722513 vs 446110)
5. Implement comprehensive error handling for API rate limits and network failures
6. Maintain strict adherence to prohibited elements list (no emoji/Chinese/"AI")
7. Design all geographic operations to be city-agnostic (use boundary_validator interface)
8. Never hard-code city parameters; always reference current city context via city_context.py

Current File Context:
[Insert active file path and function context here before requesting code generation]
Example: "src/config/cities/denver_co.py - defining Denver ZIP codes and geographic bounds"

## Quality Assurance Checklist
Before committing any code change, verify:
[ ] No emoji characters present in file content
[ ] No Chinese or non-English text (except proper nouns)
[ ] No occurrence of "AI" string in any case variation
[ ] Python 3.11 compatibility confirmed
[ ] All numerical outputs include confidence intervals
[ ] Geographic coordinates validated as EPSG:4326
[ ] Haversine distance threshold enforced for entity matching
[ ] No hard-coded city parameters (all values from city configuration)
[ ] City configuration schema validation passes for Minneapolis and Denver
[ ] Commit message follows imperative mood format under 72 characters
[ ] Changes pushed to GitHub repository immediately after commit
[ ] Cross-city regression tests pass before main branch merge