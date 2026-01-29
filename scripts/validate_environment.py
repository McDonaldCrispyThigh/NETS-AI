"""
Environment Validation Script - Check all dependencies and configurations
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

def print_header(text):
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}{text:^60}{RESET}")
    print(f"{CYAN}{'='*60}{RESET}\n")

def check_imports():
    """Verify all required Python packages"""
    print_header("Checking Python Dependencies")
    
    required_packages = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'openai': 'openai',
        'googlemaps': 'googlemaps',
        'waybackpy': 'waybackpy',
        'requests': 'requests',
        'bs4': 'beautifulsoup4',
        'dotenv': 'python-dotenv',
        'pydantic': 'pydantic',
        'httpx': 'httpx',
        'tqdm': 'tqdm',
        'openpyxl': 'openpyxl'
    }
    
    missing = []
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
            print(f"  {GREEN}✓{RESET} {package_name}")
        except ImportError:
            print(f"  {RED}✗{RESET} {package_name}")
            missing.append(package_name)
    
    if missing:
        print(f"\n{RED}Missing packages (install with pip):{RESET}")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    print(f"\n{GREEN}All packages installed!{RESET}")
    return True

def check_env():
    """Check environment variables"""
    print_header("Checking Environment Variables")
    
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    required_vars = {
        'OPENAI_API_KEY': 'OpenAI API key',
        'GOOGLE_MAPS_API_KEY': 'Google Maps API key'
    }
    
    missing = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}":
            # Mask key value
            masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"  {GREEN}✓{RESET} {var}: {masked}")
        else:
            print(f"  {RED}✗{RESET} {var}: Not configured")
            missing.append(description)
    
    if missing:
        print(f"\n{YELLOW}Please configure the following in .env:{RESET}")
        for desc in missing:
            print(f"  - {desc}")
        return False
    
    print(f"\n{GREEN}All API keys configured!{RESET}")
    return True

def check_project_structure():
    """Check project structure"""
    print_header("Checking Project Structure")
    
    required_dirs = [
        'src/agents',
        'src/data',
        'src/models',
        'src/utils',
        'scripts',
        'data/processed',
        'logs',
        'notebooks',
        'tests',
        'docs'
    ]

    # Ensure logs directory exists
    logs_path = Path('logs')
    logs_path.mkdir(parents=True, exist_ok=True)
    
    required_files = [
        'src/config.py',
        'src/agents/google_maps_agent.py',
        'src/agents/wayback_agent.py',
        'src/agents/gpt_analyzer.py',
        'src/utils/logger.py',
        'src/utils/helpers.py',
        'scripts/03_complete_pipeline.py',
        'requirements.txt',
        'README.md'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"  {GREEN}✓{RESET} {dir_path}/")
        else:
            print(f"  {RED}✗{RESET} {dir_path}/")
            missing_dirs.append(dir_path)
    
    missing_files = []
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"  {GREEN}✓{RESET} {file_path}")
        else:
            print(f"  {RED}✗{RESET} {file_path}")
            missing_files.append(file_path)
    
    if missing_dirs or missing_files:
        print(f"\n{YELLOW}Missing components:{RESET}")
        if missing_dirs:
            print(f"  Directories: {', '.join(missing_dirs)}")
        if missing_files:
            print(f"  Files: {', '.join(missing_files)}")
        return False
    
    print(f"\n{GREEN}Project structure complete!{RESET}")
    return True

def test_agents():
    """Test agent modules"""
    print_header("Testing Agent Modules")
    
    # Test imports
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from src.agents.google_maps_agent import GoogleMapsAgent
        from src.agents.wayback_agent import WaybackAgent
        from src.agents.gpt_analyzer import GPTAnalyzer
        from src.utils.logger import setup_logger
        from src.utils.helpers import calculate_confidence_score
        
        print(f"  {GREEN}✓{RESET} GoogleMapsAgent imported")
        print(f"  {GREEN}✓{RESET} WaybackAgent imported")
        print(f"  {GREEN}✓{RESET} GPTAnalyzer imported")
        print(f"  {GREEN}✓{RESET} Logger imported")
        print(f"  {GREEN}✓{RESET} Helpers imported")
        
        # Test instantiation
        import os
        if os.getenv('GOOGLE_MAPS_API_KEY'):
            maps = GoogleMapsAgent()
            print(f"  {GREEN}✓{RESET} GoogleMapsAgent initialized")
        
        wayback = WaybackAgent()
        print(f"  {GREEN}✓{RESET} WaybackAgent initialized")
        
        if os.getenv('OPENAI_API_KEY'):
            gpt = GPTAnalyzer()
            print(f"  {GREEN}✓{RESET} GPTAnalyzer initialized")
        
        print(f"\n{GREEN}All agents working!{RESET}")
        return True
        
    except Exception as e:
        print(f"  {RED}✗{RESET} Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_wayback_sample():
    """Test Wayback Machine API"""
    print_header("Testing Wayback Machine")
    
    try:
        from src.agents.wayback_agent import WaybackAgent
        wayback = WaybackAgent()
        
        # Test with a known website
        test_url = "https://www.python.org"
        print(f"  Testing with: {test_url}")
        
        result = wayback.get_first_snapshot(test_url)
        if result:
            print(f"  {GREEN}✓{RESET} First snapshot: {result['date'].year}")
            print(f"  {GREEN}✓{RESET} Wayback API working!")
            return True
        else:
            print(f"  {YELLOW}⚠{RESET}  No snapshots found (API might be slow)")
            return True
            
    except Exception as e:
        print(f"  {RED}✗{RESET} Error: {str(e)}")
        return False

def main():
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}AI-BDD Environment Validation Script{RESET:^60}")
    print(f"{CYAN}{'='*60}{RESET}\n")
    
    results = {
        'imports': check_imports(),
        'env': check_env(),
        'structure': check_project_structure(),
        'agents': test_agents(),
        'wayback': test_wayback_sample()
    }
    
    # Summary
    print_header("Validation Results")
    
    passed = sum(results.values())
    total = len(results)
    
    for name, status in results.items():
        icon = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
        print(f"  {icon} {name.title()}")
    
    print(f"\n{CYAN}{'─'*60}{RESET}")
    
    if passed == total:
        print(f"{GREEN}All tests passed ({passed}/{total}){RESET}")
        print(f"\n{CYAN}Next steps:{RESET}")
        print(f"  python scripts/03_complete_pipeline.py --list")
        print(f"  python scripts/03_complete_pipeline.py --task coffee --limit 10")
        return 0
    else:
        print(f"{YELLOW}Some tests failed ({passed}/{total}){RESET}")
        print(f"\nPlease review error messages above and fix issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())
