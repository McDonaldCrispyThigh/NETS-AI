"""
Quick Start Script - NETS-AI Minneapolis
一键执行完整的数据增强流程
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """执行命令并显示进度"""
    print(f"\n{'='*70}")
    print(f"▶ {description}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=False)
        if result.returncode != 0:
            print(f"⚠ Command returned non-zero exit code: {result.returncode}")
            return False
        return True
    except Exception as e:
        print(f"✗ Error executing command: {e}")
        return False


def main():
    """主入口"""
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                  NETS MINNEAPOLIS BUSINESS DATA ENHANCEMENT           ║
║                     Quick Start Setup & Execution                     ║
╚═══════════════════════════════════════════════════════════════════════╝
    """)
    
    # 激活虚拟环境
    activate_cmd = r".\AIAGENTNETS\Scripts\Activate.ps1"
    
    # 步骤1：验证环境
    print("\n📋 Step 1: Verifying environment setup...")
    if not run_command(f"{activate_cmd}; python verify_setup.py", "Environment Verification"):
        print("\n✗ Environment verification failed. Please ensure:")
        print("  - Python 3.10+ installed")
        print("  - Virtual environment created: .\AIAGENTNETS")
        print("  - Dependencies installed: pip install -r requirements.txt")
        return 1
    
    # 步骤2：生成样本数据
    print("\n📊 Step 2: Generating sample test data...")
    if not run_command(
        f"{activate_cmd}; python scripts/generate_sample_data.py",
        "Generate Sample Data (150 QSR + 80 Pharmacy)"
    ):
        print("\n✗ Sample data generation failed.")
        return 1
    
    # 步骤3：运行pipeline
    print("\n⚙️  Step 3: Running data enhancement pipeline...")
    if not run_command(
        f"{activate_cmd}; python scripts/run_pipeline.py "
        "--input data/raw/nets_minneapolis_sample.csv --validate",
        "NETS Data Enhancement Pipeline"
    ):
        print("\n✗ Pipeline execution failed.")
        return 1
    
    # 步骤4：启动dashboard
    print("\n📈 Step 4: Launching Streamlit Dashboard...")
    print(f"{'='*70}")
    print("▶ Starting Streamlit Server")
    print(f"{'='*70}")
    print("""
✓ Pipeline completed successfully!

NEXT: Opening Streamlit dashboard at http://localhost:8501

Features available:
  • Maps: Geographic distribution and heatmaps
  • Distribution: Employee count analysis  
  • Survival: Business status probabilities
  • Quality: Data quality metrics
  • Details: Filterable data table with export

Press Ctrl+C to stop the dashboard
    """)
    
    try:
        subprocess.run(
            f"{activate_cmd}; streamlit run dashboard/app.py",
            shell=True
        )
    except KeyboardInterrupt:
        print("\n✓ Dashboard stopped.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
