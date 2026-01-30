"""
Improved LinkedIn Company Data Scraper
Uses playwright with extended timeouts and better error handling
"""

import os
import time
from typing import Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class LinkedInScraper:
    """
    LinkedIn scraping for employee validation using Playwright.
    Implements with extended timeouts and improved error handling to prevent
    "Error getting company name: Locator.inner_text: Timeout exceeded" errors.
    """
    
    def __init__(self):
        self.email = os.getenv("LINKEDIN_EMAIL")
        self.password = os.getenv("LINKEDIN_PASSWORD")
        self.session_file = Path(__file__).parent.parent.parent / ".linkedin_session.json"
        
        self.available = False
        if self.email and self.password:
            try:
                import playwright
                self.available = True
            except ImportError:
                print("playwright not installed. Install with: pip install playwright>=1.40.0")
    
    def search_company(self, company_name: str, location: str = None) -> Optional[Dict]:
        """
        Search for a company on LinkedIn by name
        
        Implements improved error handling with:
        - Extended page load timeout (60 seconds)
        - Network wait before element lookup
        - Graceful failure on LinkedIn search errors
        
        Args:
            company_name: Business name to search
            location: Optional location (for future use)
            
        Returns:
            Dict with employee_count, company_size, industry, or None on error
        """
        if not self.available:
            return None
        
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("playwright not available")
            return None
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ])
                
                context = self._create_context(browser)
                if context is None:
                    browser.close()
                    return None

                page = context.new_page()
                
                # Extended timeout for slow connections
                page.set_default_timeout(90000)  # 90 seconds
                page.set_default_navigation_timeout(90000)
                
                try:
                    # Clean company name for search
                    search_name = company_name.strip().lower()
                    search_name = ''.join(c for c in search_name if c.isalnum() or c == ' ')
                    
                    # LinkedIn search URL
                    search_url = f"https://www.linkedin.com/search/results/companies/?keywords={search_name.replace(' ', '%20')}"
                    
                    # Navigate with error recovery
                    try:
                        page.goto(search_url, wait_until='domcontentloaded', timeout=90000)
                    except Exception as e:
                        # If domcontentloaded times out, try load
                        print(f"Search page timeout, retrying with load wait: {e}")
                        try:
                            page.goto(search_url, wait_until='load', timeout=90000)
                        except:
                            print(f"LinkedIn search page failed to load")
                            return None

                    # If redirected to login, session is not valid
                    if self._is_login_wall(page):
                        print("LinkedIn requires login. Session not valid.")
                        return None
                    
                    # Wait for results to appear
                    try:
                        page.wait_for_selector('a[data-control-name*="entity_result"]', timeout=45000)
                    except:
                        print(f"No search results found for '{company_name}'")
                        return None
                    
                    # Get first result link
                    try:
                        first_result = page.query_selector('a[data-control-name*="entity_result"]')
                        if not first_result:
                            print(f"Could not find company link for '{company_name}'")
                            return None
                        
                        company_url = first_result.get_attribute('href')
                        if not company_url:
                            return None
                        
                        # Navigate to company page
                        page.goto(company_url, wait_until='load', timeout=90000)
                        
                        # Extended wait for company info to load
                        time.sleep(3)  # Give page time to fully render
                        
                        # Try to extract company size with error recovery
                        company_size = self._extract_company_size(page, company_name)
                        employee_count = self._parse_employee_count(company_size)
                        
                        return {
                            'company_name': company_name,
                            'employee_count': employee_count,
                            'company_size': company_size,
                            'linkedin_url': company_url
                        }
                        
                    except Exception as e:
                        print(f"Error extracting company data for '{company_name}': {e}")
                        return None
                        
                finally:
                    context.close()
                    browser.close()
                    
        except Exception as e:
            print(f"LinkedIn search error for '{company_name}': {e}")
            return None

    def _create_context(self, browser):
        """
        Create a browser context, loading saved session if available.
        """
        try:
            if self.session_file.exists():
                return browser.new_context(
                    storage_state=str(self.session_file),
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
            print("LinkedIn session file not found. Run session login first.")
            return None
        except Exception as e:
            print(f"Failed to create browser context: {e}")
            return None

    def _is_login_wall(self, page) -> bool:
        """
        Detect LinkedIn login wall.
        """
        try:
            url = page.url.lower()
            if "login" in url or "checkpoint" in url:
                return True
            if page.query_selector("input#username") or page.query_selector("input#password"):
                return True
        except Exception:
            return True
        return False
    
    def _extract_company_size(self, page, company_name: str) -> Optional[str]:
        """
        Extract company size from LinkedIn company page
        
        Implements multiple fallback strategies to avoid timeout errors:
        1. Try h1 (company name)
        2. Try dedicated company size element
        3. Return None if not found
        """
        try:
            # Try to find company info section with extended timeout
            try:
                # Look for company size in main info section
                size_element = page.query_selector(
                    'div[class*="company-info"] >> text=employees',
                    timeout=10000
                )
                if size_element:
                    text = size_element.text_content()
                    return text.strip()
            except:
                pass
            
            # Try alternative selector for company size
            try:
                size_text = page.text_content('div[class*="topcard__company-info"]')
                if size_text and 'employees' in size_text.lower():
                    return size_text.strip()
            except:
                pass
            
            # Last resort: Look for any size mention in visible text
            try:
                all_text = page.text_content()
                import re
                # Match patterns like "10,000 employees" or "1,000-5,000 employees"
                matches = re.findall(r'([\d,]+(?:-[\d,]+)?)\s+employees', all_text, re.IGNORECASE)
                if matches:
                    return f"{matches[0]} employees"
            except:
                pass
            
            return None
            
        except Exception as e:
            print(f"Error extracting company size for '{company_name}': {e}")
            return None
    
    def _parse_employee_count(self, company_size: Optional[str]) -> Optional[int]:
        """
        Parse employee count from company size string
        
        Examples:
            "10,000-50,000 employees" -> 30000 (midpoint)
            "1,000+ employees" -> 1000
            "51-200 employees" -> 125 (midpoint)
        """
        if not company_size:
            return None
        
        try:
            import re
            
            # Remove commas and normalize
            text = company_size.replace(',', '').lower()
            
            # Match patterns
            if '+' in text:
                # "1000+ employees"
                match = re.search(r'(\d+)\+', text)
                if match:
                    return int(match.group(1))
            
            # Range "10-50"
            match = re.search(r'(\d+)-(\d+)', text)
            if match:
                low = int(match.group(1))
                high = int(match.group(2))
                return (low + high) // 2
            
            # Single number
            match = re.search(r'\b(\d+)\b', text)
            if match:
                return int(match.group(1))
            
        except Exception as e:
            print(f"Error parsing employee count '{company_size}': {e}")
        
        return None
