"""
LinkedIn Company Data Scraper (v3.0+ Playwright)
Uses linkedin_scraper v3.x: https://github.com/joeyism/linkedin_scraper

Requirements:
    pip install linkedin-scraper>=3.1.0 playwright
    playwright install chromium
"""

import os
import asyncio
from typing import Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class LinkedInScraperV3:
    """
    LinkedIn scraping for employee validation using Playwright (v3.0+).
    Async implementation with better performance and reliability.
    
    WARNING: Automated LinkedIn scraping may violate LinkedIn ToS.
    Use only for academic research with proper disclosure.
    """
    
    def __init__(self):
        self.email = os.getenv("LINKEDIN_EMAIL")
        self.password = os.getenv("LINKEDIN_PASSWORD")
        self.session_file = Path(__file__).parent.parent.parent / ".linkedin_session.json"
        
        if not self.email or not self.password:
            print("Warning: LINKEDIN_EMAIL or LINKEDIN_PASSWORD not found in .env")
            self.available = False
        else:
            try:
                # Import check
                from linkedin_scraper import BrowserManager, CompanyScraper
                self.available = True
            except ImportError:
                print("linkedin_scraper v3+ not installed. Install with: pip install linkedin-scraper>=3.1.0 playwright")
                print("Then run: playwright install chromium")
                self.available = False
    
    async def _ensure_session(self):
        """Ensure we have a valid LinkedIn session"""
        from linkedin_scraper import BrowserManager, login_with_credentials
        
        # If session file exists, try to use it
        if self.session_file.exists():
            return
        
        # Create new session - must complete within this context
        print("Creating LinkedIn session (first time only)...")
        print("A browser window will open for login. Please complete any security challenges.")
        
        browser = None
        try:
            browser = BrowserManager(headless=False)
            await browser.__aenter__()
            
            await login_with_credentials(
                browser.page,
                email=self.email,
                password=self.password
            )
            await browser.save_session(str(self.session_file))
            print(f"Session saved to {self.session_file}")
            
        except Exception as e:
            print(f"Session creation failed: {e}")
            raise
        finally:
            if browser:
                try:
                    await browser.__aexit__(None, None, None)
                except:
                    pass
    
    async def _search_company_async(self, company_name: str) -> Optional[Dict]:
        """
        Internal async method to search for a company
        
        Args:
            company_name: Business name
            
        Returns:
            Company data including employee count
        """
        if not self.available:
            return None
        
        browser = None
        try:
            from linkedin_scraper import BrowserManager, CompanyScraper
            
            # Ensure session exists first
            await self._ensure_session()
            
            # Create new browser instance for scraping
            browser = BrowserManager(headless=True)
            await browser.__aenter__()
            
            # Load saved session
            await browser.load_session(str(self.session_file))
            
            # Build LinkedIn company URL
            search_name = company_name.replace(' ', '-').lower()
            search_name = ''.join(c for c in search_name if c.isalnum() or c == '-')
            company_url = f"https://www.linkedin.com/company/{search_name}/"
            
            # Scrape company data
            scraper = CompanyScraper(browser.page)
            company = await scraper.scrape(company_url)
            
            result = {
                'company_name': company.name,
                'linkedin_url': company_url,
                'employee_count': self._parse_employee_count(company.company_size),
                'company_size': company.company_size,
                'industry': company.industry,
                'founded_year': company.founded,
                'headquarters': company.headquarters,
                'about': company.about_us[:200] if company.about_us else None
            }
            
            return result
                
        except Exception as e:
            print(f"LinkedIn search error: {e}")
            return None
        finally:
            if browser:
                try:
                    await browser.__aexit__(None, None, None)
                except:
                    pass
    
    def search_company(self, company_name: str, location: str = None) -> Optional[Dict]:
        """
        Search for a company on LinkedIn (synchronous wrapper)
        
        Args:
            company_name: Business name
            location: Optional location filter (ignored in v3)
            
        Returns:
            Company data including employee count
        """
        if not self.available:
            return None
        
        # Run async code in new event loop
        try:
            return asyncio.run(self._search_company_async(company_name))
        except RuntimeError as e:
            # If event loop already running, create new loop
            if "running event loop" in str(e):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(self._search_company_async(company_name))
                finally:
                    loop.close()
            raise
    
    async def get_company_by_url_async(self, linkedin_url: str) -> Optional[Dict]:
        """
        Get company details from LinkedIn URL (async)
        
        Args:
            linkedin_url: LinkedIn company page URL
            
        Returns:
            Detailed company information
        """
        if not self.available:
            return None
        
        browser = None
        try:
            from linkedin_scraper import BrowserManager, CompanyScraper
            
            await self._ensure_session()
            
            browser = BrowserManager(headless=True)
            await browser.__aenter__()
            await browser.load_session(str(self.session_file))
            
            scraper = CompanyScraper(browser.page)
            company = await scraper.scrape(linkedin_url)
            
            result = {
                'company_name': company.name,
                'linkedin_url': linkedin_url,
                'employee_count': self._parse_employee_count(company.company_size),
                'company_size': company.company_size,
                'industry': company.industry,
                'founded_year': company.founded,
                'headquarters': company.headquarters,
                'about': company.about_us[:200] if company.about_us else None
            }
            
            return result
                
        except Exception as e:
            print(f"LinkedIn details error: {e}")
            return None
        finally:
            if browser:
                try:
                    await browser.__aexit__(None, None, None)
                except:
                    pass
    
    def get_company_by_url(self, linkedin_url: str) -> Optional[Dict]:
        """Get company details from LinkedIn URL (synchronous wrapper)"""
        if not self.available:
            return None
        
        try:
            return asyncio.run(self.get_company_by_url_async(linkedin_url))
        except RuntimeError as e:
            if "running event loop" in str(e):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(self.get_company_by_url_async(linkedin_url))
                finally:
                    loop.close()
            raise
    
    def _parse_employee_count(self, size_str: Optional[str]) -> Optional[int]:
        """
        Convert LinkedIn employee range to midpoint estimate
        
        Examples:
            "1-10 employees" -> 5
            "11-50 employees" -> 30
            "51-200 employees" -> 125
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
            num = int(numbers[0])
            if '+' in size_str:
                return num + 5000  # Estimate for "10000+"
            return num
        
        # Fallback to predefined ranges
        range_map = {
            "1-10": 5,
            "11-50": 30,
            "51-200": 125,
            "201-500": 350,
            "501-1000": 750,
            "1001-5000": 3000,
            "5001-10000": 7500,
            "10000+": 15000,
            "self-employed": 1,
            "myself only": 1
        }
        
        # Normalize and check
        normalized = size_str.lower().strip()
        for key, value in range_map.items():
            if key in normalized:
                return value
        
        return None
    
    def close(self):
        """Cleanup - not needed for Playwright (auto-managed)"""
        pass


# Compatibility: expose as LinkedInScraper
LinkedInScraper = LinkedInScraperV3
