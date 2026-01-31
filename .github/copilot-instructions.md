# NETS Enhancement System - GitHub Copilot Instructions

## STRICT ABSOLUTE PROHIBITIONS - VIOLATION BLOCKS COMMIT
1. NEVER generate emoji characters in any context
2. NEVER generate Chinese or non-English text (except proper nouns like "Minneapolis")
3. NEVER generate "AI" string in any case. Use: "computational", "statistical", "language model analysis", "enhancement system"
4. NEVER hard-code geographic parameters (ZIP codes, coordinates, census tracts)
5. Python 3.11 ONLY (PyMC3 incompatible with 3.12+)

## Core Technical Requirements
- **GEO**: Minneapolis, MN (Census Tract boundaries); configurable cities via src/config/cities/
- **INDUSTRY**: NAICS 722513 (fast food) + 446110 (pharmacies) ONLY
- **SAMPLE**: 500-1000 establishments (MVP scale)
- **COORDINATES**: EPSG:4326 (WGS84) enforced for all geospatial operations
- **MATCHING**: Haversine distance < 50m + fuzzy name match
- **UNCERTAINTY**: All estimates MUST include 95% CI (bootstrap/Bayesian)
- **OUTPUT**: Parquet with columns: employees_optimized, employees_lower_ci, employees_upper_ci, is_active_prob, confidence_level, data_quality_score, city_name, census_tract_id
- **TEMPORAL**: Monthly periods using pd.to_period('M')

## Multi-City Architecture
- All city parameters externalized to src/config/cities/{city}_{state}.py
- Use city-agnostic interfaces: src/geospatial/boundary_validator.py, coordinate_transformer.py, distance_calculator.py
- Pipeline: `python scripts/run_pipeline.py --city [city_name] --input [nets_snapshot]`
- NEVER reference city parameters directly; use city_context.py runtime manager

## Data Workflow
1. NETS is PRIMARY data source - external signals (LinkedIn/reviews) are supplements ONLY
2. Address matching: haversine distance <50m + fuzzy name match
3. Temporal alignment: monthly periods
4. All numerical outputs MUST include uncertainty quantification

## Current Phase: 4 (Model Development)
- Employee estimation: XGBoost + PyMC hierarchical prior by NAICS
- Survival detection: Random Forest on review decay + job posting activity
- Next: Signal fusion (Phase 5) → Health equity validation (Phase 6)

## Workflow Requirements
- Commit after each discrete phase completion
- Commit messages: imperative mood, max 72 chars, no prohibited elements
- Push to main immediately; no long-lived feature branches during MVP
- Pre-commit: scripts/validate_commit_compliance.py must pass

## Code Generation Rules
- Include comprehensive error handling for API failures, boundary validation, NAICS scope
- All numerical outputs must include uncertainty quantification
- Documentation in English only with zero prohibited elements
- Production-ready code with proper logging and validation
