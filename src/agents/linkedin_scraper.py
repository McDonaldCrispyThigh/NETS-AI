"""
LinkedIn Company Data Scraper
Uses linkedin_scraper library: https://github.com/joeyism/linkedin_scraper
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class LinkedInScraper:
 """
 LinkedIn scraping for employee validation and company information.
 Uses selenium-based scraping - requires LinkedIn credentials.
 
 WARNING: Automated LinkedIn scraping may violate LinkedIn ToS.
 Use only for academic research with proper disclosure.
 """
 
 def __init__(self):
 self.email = os.getenv("LINKEDIN_EMAIL")
 self.password = os.getenv("LINKEDIN_PASSWORD")
 
 if not self.email or not self.password:
 print("Warning: LINKEDIN_EMAIL or LINKEDIN_PASSWORD not found in .env")
 self.scraper = None
 else:
 try:
 from linkedin_scraper import Person, actions
 from selenium import webdriver
 from selenium.webdriver.chrome.options import Options
 
 # Setup headless Chrome
 chrome_options = Options()
 chrome_options.add_argument("--headless")
 chrome_options.add_argument("--no-sandbox")
 chrome_options.add_argument("--disable-dev-shm-usage")
 
 self.driver = webdriver.Chrome(options=chrome_options)
 actions.login(self.driver, self.email, self.password)
 
 self.scraper = True
 
 except ImportError:
 print("linkedin_scraper not installed. Install with: pip install linkedin_scraper")
 self.scraper = None
 except Exception as e:
 print(f"LinkedIn login failed: {e}")
 self.scraper = None
 
 def search_company(self, company_name: str, location: str = None) -> Optional[Dict]:
 """
 Search for a company on LinkedIn
 
 Args:
 company_name: Business name
 location: Optional location filter
 
 Returns:
 Company data including employee count
 """
 if not self.scraper:
 return None
 
 try:
 from linkedin_scraper import Company
 
 # Build search URL
 search_name = company_name.replace(' ', '-').lower()
 company_url = f"https://www.linkedin.com/company/{search_name}/"
 
 company = Company(company_url, driver=self.driver)
 
 return {
 'company_name': company.name,
 'linkedin_url': company_url,
 'employee_count': self._parse_employee_count(company.company_size),
 'company_size': company.company_size,
 'industry': company.industry,
 'founded_year': company.founded,
 'company_type': company.company_type,
 'headquarters': company.headquarters,
 'specialties': company.specialties
 }
 
 except Exception as e:
 print(f"LinkedIn search error: {e}")
 return None
 
 def get_company_by_url(self, linkedin_url: str) -> Optional[Dict]:
 """
 Get company details from LinkedIn URL
 
 Args:
 linkedin_url: LinkedIn company page URL
 
 Returns:
 Detailed company information
 """
 if not self.scraper:
 return None
 
 try:
 from linkedin_scraper import Company
 
 company = Company(linkedin_url, driver=self.driver)
 
 return {
 'company_name': company.name,
 'linkedin_url': linkedin_url,
 'employee_count': self._parse_employee_count(company.company_size),
 'company_size': company.company_size,
 'industry': company.industry,
 'founded_year': company.founded,
 'company_type': company.company_type,
 'headquarters': company.headquarters,
 'specialties': company.specialties
 }
 
 except Exception as e:
 print(f"LinkedIn details error: {e}")
 return None
 
 def _parse_employee_count(self, size_str: Optional[str]) -> Optional[int]:
 """
 Convert LinkedIn employee range to midpoint estimate
 
 Examples:
 "1-10" -> 5
 "11-50" -> 30
 "51-200" -> 125
 """
 if not size_str:
 return None
 
 # Extract numbers from string
 import re
 numbers = re.findall(r'\d+', size_str)
 
 if len(numbers) >= 2:
 # Range like "51-200"
 low = int(numbers[0])
 high = int(numbers[1])
 return (low + high) // 2
 elif len(numbers) == 1:
 # Single number or "10000+"
 return int(numbers[0])
 
 # Fallback to predefined ranges
 range_map = {
 "1-10": 5,
 "11-50": 30,
 "51-200": 125,
 "201-500": 350,
 "501-1000": 750,
 "1001-5000": 3000,
 "5001-10000": 7500,
 "10000+": 15000
 }
 
 return range_map.get(size_str, None)
 
 def close(self):
 """Close the browser driver"""
 if hasattr(self, 'driver'):
 try:
 self.driver.quit()
 except:
 pass
