#!/usr/bin/env python3
"""
Single investor test - Aaron Holiday
Test script to verify data extraction accuracy
"""

from mercury_crawler import MercuryCrawler
import json
from datetime import datetime


def test_aaron_holiday():
    """Test crawling Aaron Holiday's investor page"""
    print("🧪 Testing Aaron Holiday's investor page...")
    
    crawler = MercuryCrawler(headless=False, delay=1.0)  # Non-headless for verification
    
    try:
        url = "https://mercury.com/investor-database/aaron-holiday"
        print(f"📄 Scraping: {url}")
        
        # Scrape Aaron Holiday's data
        investor_data = crawler.scrape_investor_data(url)
        
        # Display results
        print("\n" + "="*60)
        print("📊 AARON HOLIDAY - SCRAPED DATA")
        print("="*60)
        print(f"Name: {investor_data['name']}")
        print(f"Industries: {investor_data['industries']}")
        print(f"Stages: {investor_data['stages']}")
        print(f"Check Range: {investor_data['check_range']}")
        print(f"Geography: {investor_data['geography']}")
        print(f"Bio (first 200 chars): {investor_data['bio'][:200]}...")
        print(f"Email: {investor_data['contacts']['email']}")
        print(f"LinkedIn: {investor_data['contacts']['linkedin']}")
        print(f"Twitter: {investor_data['contacts']['twitter']}")
        print(f"Website: {investor_data['contacts']['website']}")
        print(f"Status: {investor_data['status']}")
        print("="*60)
        
        # Save to JSON file
        result = {
            "test_info": {
                "target_investor": "Aaron Holiday",
                "url": url,
                "test_date": datetime.now().isoformat(),
                "purpose": "Data accuracy verification"
            },
            "investor_data": investor_data
        }
        
        filename = "aaron_holiday_test.json"
        with open(f"/Users/williamcheng/Desktop/MercuryCrawler/{filename}", 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Test results saved to: {filename}")
        print("✅ Test completed successfully!")
        
        return investor_data
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None
    finally:
        crawler.cleanup()


if __name__ == "__main__":
    test_aaron_holiday()