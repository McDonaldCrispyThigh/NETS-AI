"""
Quick Start Script - NETS-AI Minneapolis
Automated end-to-end data enhancement workflow
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run command and display progress"""
    print(f"\n{'='*70}")
    print(f"[*] {description}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=False)
        if result.returncode != 0:
            print(f"[!] Command returned non-zero exit code: {result.returncode}")
            return False
        return True
    except Exception as e:
        print(f"[ERROR] Error executing command: {e}")
        return False


def main():
    """Main entry point"""
    print("""
========================================================================
 NETS MINNEAPOLIS BUSINESS DATA ENHANCEMENT 
 Quick Start Setup & Execution 
========================================================================
 """)
    
    # Activate virtual environment
    activate_cmd = r".\AIAGENTNETS\Scripts\Activate.ps1"
    
    # Step 1: Verify environment
    print("\n[*] Step 1: Verifying environment setup...")
    if not run_command(f"{activate_cmd}; python verify_setup.py", "Environment Verification"):
        print("\n[ERROR] Environment verification failed. Please ensure:")
        print(" - Python 3.11 installed")
        print(" - Virtual environment created: .\\AIAGENTNETS")
        print(" - Dependencies installed: pip install -r requirements.txt")
        return 1

    # Step 2: Generate test fixtures
    print("\n[*] Step 2: Generating test fixtures...")
    if not run_command(
        f"{activate_cmd}; python scripts/generate_sample_data.py",
        "Generate Test Fixtures (5 QSR + 3 Pharmacy)"
    ):
        print("\n[ERROR] Test fixture generation failed.")
        return 1

    # Step 3: Run pipeline in test mode
    print("\n[*] Step 3: Running data enhancement pipeline in test mode...")
    if not run_command(
        f"{activate_cmd}; python scripts/run_pipeline.py --mode test --validate",
        "NETS Data Enhancement Pipeline - Test Mode"
    ):
        print("\n[ERROR] Pipeline execution failed.")
        return 1

    # Step 4: Launch dashboard
    print("\n[*] Step 4: Launching Streamlit Dashboard...")
    print(f"{'='*70}")
    print("[*] Starting Streamlit Server")
    print(f"{'='*70}")
    print("""
[SUCCESS] Pipeline completed successfully!

NEXT: Opening Streamlit dashboard at http://localhost:8501

Features available:
 - Maps: Geographic distribution and heatmaps
 - Distribution: Employee count analysis 
 - Survival: Business status probabilities
 - Quality: Data quality metrics
 - Details: Filterable data table with export

Press Ctrl+C to stop the dashboard
    """)

    try:
        subprocess.run(
            f"{activate_cmd}; streamlit run dashboard/app.py",
            shell=True
        )
    except KeyboardInterrupt:
        print("\n[*] Dashboard stopped.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
