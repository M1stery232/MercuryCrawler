#!/usr/bin/env python3
"""
Mercury Investor Database Crawler
Scrapes investor information from Mercury's investor database
"""

import json
import time
import re
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests


class MercuryCrawler:
    def __init__(self, headless: bool = True, delay: float = 2.0):
        self.base_url = "https://mercury.com"
        self.database_url = "https://mercury.com/investor-database?perPage=All"
        self.delay = delay
        self.headless = headless
        self.driver = None
        self.session = requests.Session()
        
    def setup_driver(self):
        """Initialize Selenium WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        return self.driver

    def collect_investor_urls(self) -> List[str]:
        """Collect all investor URLs from the main database page"""
        print("🔍 Loading investor database page...")
        
        if not self.driver:
            self.setup_driver()
            
        self.driver.get(self.database_url)
        
        # Wait for page to load and investors to appear
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(5)  # Additional wait for dynamic content
            
        except Exception as e:
            print(f"❌ Error loading page: {e}")
            return []
        
        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        # Find investor links - they should match pattern /investor-database/[name]
        investor_urls = []
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            if '/investor-database/' in href and href != '/investor-database':
                if href.startswith('/'):
                    full_url = urljoin(self.base_url, href)
                else:
                    full_url = href
                    
                if full_url not in investor_urls:
                    investor_urls.append(full_url)
        
        print(f"✅ Found {len(investor_urls)} investor URLs")
        return investor_urls

    def scrape_investor_data(self, url: str) -> Dict:
        """Scrape data from an individual investor page"""
        investor_data = {
            "url": url,
            "name": "",
            "industries": [],
            "stages": [],
            "check_range": "",
            "bio": "",
            "geography": [],
            "contacts": {
                "email": "",
                "linkedin": "",
                "twitter": "",
                "website": ""
            },
            "contact_info": {},
            "scraped_date": datetime.now().isoformat(),
            "status": "pending"
        }
        
        try:
            print(f"📄 Scraping: {url}")
            
            # Always use Selenium for consistent JavaScript rendering
            if not self.driver:
                self.setup_driver()
                
            self.driver.get(url)
            
            # Wait for content to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "main"))
                )
                time.sleep(3)  # Extra wait for dynamic content
            except:
                time.sleep(5)  # Fallback wait
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract investor name - try multiple strategies
            investor_data["name"] = (
                self._extract_text(soup, ['h1']) or
                self._extract_text(soup, ['[data-cy="investor-name"]', '.name']) or
                self._extract_text_by_content(soup, "investor") or
                self._get_name_from_url(url)
            )
            
            # Extract structured data using Mercury's specific HTML structure
            # Find h3 headings with class 'arcadia-heading-9' and get their content
            
            # Extract Industries using the correct HTML structure
            investor_data["industries"] = self._extract_industries(soup)
            
            # Extract Stages
            stages_content = self._extract_structured_field(soup, "Stages")
            if stages_content:
                investor_data["stages"] = self._parse_list_field(stages_content)
            
            # Extract Check Range
            check_range_content = self._extract_structured_field(soup, "Check Range")
            if check_range_content:
                investor_data["check_range"] = check_range_content.strip()
            
            # Extract Geography
            geography_content = self._extract_structured_field(soup, "Geography")
            if geography_content:
                investor_data["geography"] = self._parse_list_field(geography_content)
            
            # Extract bio using structured approach
            bio_content = self._extract_structured_field(soup, "Bio")
            if not bio_content:
                # Fallback: look for longer text blocks after Bio heading
                bio_heading = soup.find('h3', string=re.compile(r'bio', re.I))
                if bio_heading:
                    next_element = bio_heading.find_next(['p', 'div'])
                    if next_element:
                        bio_content = next_element.get_text(strip=True)
            
            if bio_content and len(bio_content) > 50:
                investor_data["bio"] = bio_content
            
            # Extract contact links - be more specific about investor contacts
            links = soup.find_all('a', href=True)
            personal_contacts = {"email": "", "linkedin": "", "twitter": "", "website": ""}
            
            for link in links:
                href = link['href']
                link_text = link.get_text().lower()
                
                # Skip Mercury's general social links
                if any(mercury_term in href for mercury_term in ['mercuryhq', 'mercury.com', 'app.mercury']):
                    continue
                    
                if 'mailto:' in href:
                    personal_contacts["email"] = href.replace('mailto:', '')
                elif 'linkedin.com/in/' in href:  # Personal LinkedIn profiles
                    personal_contacts["linkedin"] = href
                elif ('twitter.com' in href or 'x.com' in href) and '/mercury' not in href:
                    personal_contacts["twitter"] = href
                elif href.startswith('http') and self.base_url not in href:
                    # Look for personal websites
                    if any(personal_indicator in link_text for personal_indicator in ['website', 'blog', 'personal']):
                        personal_contacts["website"] = href
            
            investor_data["contacts"] = personal_contacts
            
            # Extract contact info from Contact Links section
            investor_data["contact_info"] = self._extract_contact_info(soup)
            
            investor_data["status"] = "success"
            print(f"✅ Successfully scraped: {investor_data['name']}")
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            investor_data["status"] = "error"
            investor_data["error"] = str(e)
        
        return investor_data

    def _extract_text(self, soup: BeautifulSoup, selectors: List[str]) -> str:
        """Extract text using multiple selector strategies"""
        for selector in selectors:
            try:
                if ':contains(' in selector:
                    # Handle pseudo-selector
                    text_to_find = selector.split(':contains("')[1].split('")')[0]
                    elements = soup.find_all(text=re.compile(text_to_find, re.I))
                    if elements:
                        return elements[0].parent.get_text(strip=True)
                else:
                    element = soup.select_one(selector)
                    if element:
                        return element.get_text(strip=True)
            except:
                continue
        return ""

    def _parse_list_field(self, text: str) -> List[str]:
        """Parse comma-separated or bullet-pointed lists"""
        if not text:
            return []
        
        # Split by common delimiters and clean
        items = re.split(r'[,;•·\n]', text)
        cleaned_items = []
        
        for item in items:
            cleaned = item.strip()
            if cleaned and len(cleaned) > 1:
                cleaned_items.append(cleaned)
        
        return cleaned_items

    def _extract_text_by_content(self, soup: BeautifulSoup, content: str) -> str:
        """Extract text from elements containing specific content"""
        elements = soup.find_all(text=re.compile(content, re.I))
        if elements:
            return elements[0].parent.get_text(strip=True)
        return ""

    def _get_name_from_url(self, url: str) -> str:
        """Extract name from URL path as fallback"""
        try:
            name_part = url.split('/')[-1]
            return name_part.replace('-', ' ').title()
        except:
            return ""

    def _extract_field_by_patterns(self, text: str, patterns: List[str]) -> str:
        """Extract field content using regex patterns"""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                if match.groups():
                    return match.group(1).strip()
                else:
                    return match.group(0).strip()
        return ""

    def _extract_structured_field(self, soup: BeautifulSoup, field_name: str) -> str:
        """Extract field content using Mercury's structured HTML format"""
        # Find h3 with class 'arcadia-heading-9' that contains the field name
        headings = soup.find_all('h3', class_='arcadia-heading-9')
        
        for h3 in headings:
            if h3.get_text().strip().lower() == field_name.lower():
                # Find the next sibling paragraph
                next_p = h3.find_next_sibling('p')
                if next_p:
                    return next_p.get_text(strip=True)
                
                # Sometimes content might be in a different structure
                parent = h3.parent
                if parent:
                    next_p = parent.find_next('p')
                    if next_p:
                        return next_p.get_text(strip=True)
        
        return ""

    def _extract_industries(self, soup: BeautifulSoup) -> List[str]:
        """Extract industries from the specific HTML structure with individual <a> tags"""
        industries = []
        
        # Find Industries heading
        headings = soup.find_all('h3', class_='arcadia-heading-9')
        for h3 in headings:
            if h3.get_text().strip().lower() == 'industries':
                # Find the next div container with industry links
                next_div = h3.find_next('div')
                if next_div:
                    # Look for all <a> tags within this section
                    industry_links = next_div.find_all('a', href=True)
                    for link in industry_links:
                        # Only get links that seem to be industry filters
                        if 'industries=' in link.get('href', ''):
                            industry_text = link.get_text(strip=True)
                            if industry_text and industry_text not in industries:
                                industries.append(industry_text)
                    break
        
        return industries

    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract all contact information from Contact Links section - completely flexible"""
        contact_info = {}
        
        # Find Contact Links heading
        headings = soup.find_all('h3', class_='arcadia-heading-9')
        for h3 in headings:
            if 'contact links' in h3.get_text().strip().lower():
                # Find the next div container with contact links
                next_div = h3.find_next('div')
                if next_div:
                    contact_links = next_div.find_all('a', href=True)
                    for link in contact_links:
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        
                        # Skip empty text
                        if not text or len(text.strip()) < 2:
                            continue
                        
                        # Use the actual text as the key, cleaned up
                        key = text.strip()
                        
                        # Handle email decoding if it's obfuscated
                        if 'mailto:' in href:
                            contact_info[key] = href.replace('mailto:', '')
                        else:
                            contact_info[key] = href
                            
                break
        
        return contact_info

    def crawl_all_investors(self) -> Dict:
        """Main crawling function"""
        start_time = datetime.now()
        print("🚀 Starting Mercury Investor Database Crawler")
        
        # Collect investor URLs
        investor_urls = self.collect_investor_urls()
        
        if not investor_urls:
            print("❌ No investor URLs found. Exiting.")
            return {"error": "No URLs found"}
        
        # Scrape each investor
        investors_data = []
        successful_scrapes = 0
        failed_scrapes = 0
        
        for i, url in enumerate(investor_urls, 1):
            print(f"📊 Progress: {i}/{len(investor_urls)}")
            
            investor_data = self.scrape_investor_data(url)
            investors_data.append(investor_data)
            
            if investor_data["status"] == "success":
                successful_scrapes += 1
            else:
                failed_scrapes += 1
            
            # Rate limiting
            if i < len(investor_urls):
                time.sleep(self.delay)
        
        # Compile final result
        result = {
            "metadata": {
                "scraped_date": start_time.isoformat(),
                "completion_date": datetime.now().isoformat(),
                "total_investors": len(investor_urls),
                "successful_scrapes": successful_scrapes,
                "failed_scrapes": failed_scrapes,
                "success_rate": f"{(successful_scrapes/len(investor_urls)*100):.1f}%"
            },
            "investors": investors_data
        }
        
        print(f"🎉 Crawling completed!")
        print(f"📈 Success rate: {result['metadata']['success_rate']}")
        
        return result

    def save_to_json(self, data: Dict, filename: str = None) -> str:
        """Save data to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mercury_investors_{timestamp}.json"
        
        filepath = f"/Users/williamcheng/Desktop/MercuryCrawler/{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Data saved to: {filepath}")
        return filepath

    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()


def main():
    """Main execution function"""
    crawler = MercuryCrawler(headless=True, delay=1.5)  # Reduced delay for faster crawling
    
    try:
        # Run the crawler
        data = crawler.crawl_all_investors()
        
        # Save results
        if "error" not in data:
            filepath = crawler.save_to_json(data)
            print(f"🏁 Crawler completed successfully!")
            print(f"📄 Results saved to: {filepath}")
        else:
            print(f"❌ Crawler failed: {data['error']}")
            
    except KeyboardInterrupt:
        print("\n⚠️ Crawler interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        crawler.cleanup()


if __name__ == "__main__":
    main()