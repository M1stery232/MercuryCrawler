#!/usr/bin/env python3
"""
Test URL collection from main investor database page
Focus on extracting first 5 investor URLs to verify accuracy
"""

from mercury_crawler import MercuryCrawler
import json
from datetime import datetime


def test_url_collection():
    """Test collecting investor URLs from main page"""
    print("🔍 Testing URL Collection from Main Page...")
    print("📄 Loading: https://mercury.com/investor-database?perPage=All")
    
    crawler = MercuryCrawler(headless=False, delay=1.0)  # Non-headless to see what happens
    
    try:
        # Collect all URLs
        all_urls = crawler.collect_investor_urls()
        
        if not all_urls:
            print("❌ No URLs found!")
            return
            
        print(f"✅ Total URLs found: {len(all_urls)}")
        
        # Show first 5 URLs for verification
        print(f"\n📋 First 5 Investor URLs:")
        print("="*60)
        
        first_five = all_urls[:5]
        for i, url in enumerate(first_five, 1):
            print(f"{i}. {url}")
            
            # Extract investor name from URL for verification
            if '/investor-database/' in url:
                investor_slug = url.split('/investor-database/')[-1]
                investor_name = investor_slug.replace('-', ' ').title()
                print(f"   → Likely name: {investor_name}")
            print()
        
        # Verify URL patterns
        print("🔍 URL Pattern Analysis:")
        print("="*60)
        
        valid_patterns = 0
        for url in all_urls:
            if url.startswith('https://mercury.com/investor-database/') and url != 'https://mercury.com/investor-database':
                valid_patterns += 1
        
        print(f"✅ URLs with correct pattern: {valid_patterns}/{len(all_urls)}")
        print(f"📊 Pattern match rate: {(valid_patterns/len(all_urls)*100):.1f}%")
        
        # Check for duplicates
        unique_urls = list(set(all_urls))
        duplicates = len(all_urls) - len(unique_urls)
        print(f"🔄 Duplicate URLs found: {duplicates}")
        
        # Save results for inspection
        result = {
            "test_info": {
                "test_date": datetime.now().isoformat(),
                "purpose": "URL collection verification",
                "total_urls_found": len(all_urls),
                "unique_urls": len(unique_urls),
                "duplicates": duplicates,
                "pattern_match_rate": f"{(valid_patterns/len(all_urls)*100):.1f}%"
            },
            "first_five_urls": first_five,
            "all_urls": all_urls
        }
        
        filename = "url_collection_test.json"
        with open(f"/Users/williamcheng/Desktop/MercuryCrawler/{filename}", 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {filename}")
        print("🎉 URL collection test completed!")
        
        return first_five
        
    except Exception as e:
        print(f"❌ URL collection test failed: {e}")
        return None
    finally:
        crawler.cleanup()


if __name__ == "__main__":
    test_url_collection()