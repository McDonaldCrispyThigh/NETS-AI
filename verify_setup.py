#!/usr/bin/env python
"""
Virtual Environment Verification Report
Tests all key modules and provides summary
"""

import sys
import subprocess
from pathlib import Path

print("=" * 80)
print("NETS-AI PROJECT VERIFICATION REPORT")
print("=" * 80)
print(f"\nPython Version: {sys.version}")
print(f"Executable: {sys.executable}")
print(f"Project Root: {Path.cwd()}")

# Test 1: Core Data Processing
print("\n" + "=" * 80)
print("Test 1: Core Data Processing Libraries")
print("=" * 80)

core_libs = ['pandas', 'numpy', 'requests', 'dotenv']
for lib in core_libs:
    try:
        __import__(lib if lib != 'dotenv' else 'python_dotenv'.replace('python_', ''))
        print(f"  OK - {lib}")
    except ImportError:
        print(f"  FAIL - {lib} (missing)")

# Test 2: API Integration
print("\n" + "=" * 80)
print("Test 2: API Integration Libraries")
print("=" * 80)

api_libs = ['openai', 'googlemaps', 'waybackpy', 'bs4', 'pydantic']
for lib in api_libs:
    try:
        __import__(lib)
        print(f"  OK - {lib}")
    except ImportError:
        print(f"  FAIL - {lib} (missing)")

# Test 3: New ML/Geospatial Libraries
print("\n" + "=" * 80)
print("Test 3: Machine Learning & Geospatial Libraries (NEW)")
print("=" * 80)

ml_libs = ['geopandas', 'shapely', 'sklearn', 'xgboost']
for lib in ml_libs:
    try:
        if lib == 'sklearn':
            import sklearn
        else:
            __import__(lib)
        print(f"  OK - {lib}")
    except ImportError:
        print(f"  FAIL - {lib} (NEEDS INSTALL)")

# Test 4: Visualization Libraries
print("\n" + "=" * 80)
print("Test 4: Visualization Libraries (NEW)")
print("=" * 80)

viz_libs = ['streamlit', 'folium', 'altair']
for lib in viz_libs:
    try:
        __import__(lib)
        print(f"  OK - {lib}")
    except ImportError:
        print(f"  FAIL - {lib} (NEEDS INSTALL)")

# Test 5: Custom Modules
print("\n" + "=" * 80)
print("Test 5: Custom NETS-AI Modules")
print("=" * 80)

custom_modules = [
    ('src.config', 'Configuration'),
    ('src.utils.logger', 'Logger'),
    ('src.utils.helpers', 'Helpers'),
    ('src.data.nets_loader', 'NETS Loader (NEW)'),
    ('src.models.bayesian_employee_estimator', 'Employee Estimator (NEW)'),
    ('src.models.survival_detector', 'Survival Detector (NEW)'),
    ('src.data.pipeline', 'Pipeline Orchestrator (NEW)'),
]

for module_name, description in custom_modules:
    try:
        __import__(module_name)
        print(f"  OK - {description}")
    except ImportError as e:
        print(f"  FAIL - {description}: {str(e)[:50]}")
    except Exception as e:
        print(f"  ERROR - {description}: {str(e)[:50]}")

# Test 6: Documentation
print("\n" + "=" * 80)
print("Test 6: Documentation Files")
print("=" * 80)

docs = [
    'README.md',
    'requirements.txt',
    'src/config.py',
    'docs/ARCHITECTURE.md',
    'docs/QUICK_REFERENCE.md',
    'docs/DOCUMENTATION_INDEX.md',
    'PROJECT_REALIGNMENT_SUMMARY.md',
]

for doc in docs:
    path = Path(doc)
    status = "OK" if path.exists() else "MISSING"
    print(f"  {status} - {doc}")

# Summary and recommendations
print("\n" + "=" * 80)
print("INSTALLATION SUMMARY & NEXT STEPS")
print("=" * 80)

print("""
REQUIRED ACTIONS:
1. Complete installation of new ML/geospatial packages:
   pip install geopandas shapely scikit-learn xgboost pymc arviz

2. Complete installation of visualization packages:
   pip install streamlit folium altair pyarrow

3. After installation, re-run this verification script

QUICK START AFTER INSTALLATION:
Step 1: Prepare NETS data
   - Place NETS CSV in: data/raw/nets_minneapolis.csv
   - Optional external data in: data/external/

Step 2: Run pipeline
   python -c "
   from src.data.pipeline import NETSDataPipeline
   pipeline = NETSDataPipeline('data/raw/nets_minneapolis.csv')
   output = pipeline.run()
   print(f'Output: {output}')
   "

Step 3: Launch dashboard
   streamlit run dashboard/app.py

DOCUMENTATION:
- Full system guide: docs/ARCHITECTURE.md
- Daily operations: docs/QUICK_REFERENCE.md
- Module reference: docs/DOCUMENTATION_INDEX.md
- Changes summary: PROJECT_REALIGNMENT_SUMMARY.md
""")

print("=" * 80)
