#!/usr/bin/env python3
"""
Multi-investor test script
Test 3 different investors to verify data extraction consistency
"""

from mercury_crawler import MercuryCrawler
import json
from datetime import datetime


def test_multiple_investors():
    """Test multiple investors to verify extraction consistency"""
    
    test_urls = [
        "https://mercury.com/investor-database/abbie-strabala",
        "https://mercury.com/investor-database/adam-gries", 
        "https://mercury.com/investor-database/allen-gannett"
    ]
    
    print("🧪 Testing Multiple Investors...")
    print(f"📊 Testing {len(test_urls)} investors")
    
    crawler = MercuryCrawler(headless=True, delay=1.0)
    
    try:
        all_results = []
        
        for i, url in enumerate(test_urls, 1):
            print(f"\n🔄 Progress: {i}/{len(test_urls)}")
            print(f"📄 Scraping: {url}")
            
            investor_data = crawler.scrape_investor_data(url)
            all_results.append(investor_data)
            
            # Display summary
            print(f"✅ Name: {investor_data['name']}")
            print(f"📋 Industries: {len(investor_data['industries'])} found")
            print(f"🎯 Stages: {investor_data['stages']}")
            print(f"💰 Check Range: {investor_data['check_range']}")
            print(f"🌍 Geography: {investor_data['geography']}")
            print(f"📧 Contact Info Keys: {list(investor_data['contact_info'].keys())}")
            print(f"📱 Status: {investor_data['status']}")
        
        # Save comprehensive results
        result = {
            "test_info": {
                "test_date": datetime.now().isoformat(),
                "purpose": "Multi-investor extraction verification",
                "tested_investors": len(test_urls),
                "successful_extractions": sum(1 for r in all_results if r["status"] == "success")
            },
            "investors": all_results
        }
        
        filename = "multi_investor_test.json"
        with open(f"/Users/williamcheng/Desktop/MercuryCrawler/{filename}", 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {filename}")
        print(f"🎉 Test completed! Success rate: {result['test_info']['successful_extractions']}/{result['test_info']['tested_investors']}")
        
        # Display summary comparison
        print(f"\n{'='*80}")
        print("📊 COMPARISON SUMMARY")
        print(f"{'='*80}")
        for investor in all_results:
            name = investor['name']
            industries_count = len(investor['industries'])
            contact_types = list(investor['contact_info'].keys())
            print(f"{name:20} | Industries: {industries_count:2d} | Contacts: {', '.join(contact_types)}")
        
        return all_results
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None
    finally:
        crawler.cleanup()


if __name__ == "__main__":
    test_multiple_investors()