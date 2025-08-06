#!/usr/bin/env python3
"""
Sample run script - crawls first 10 investors for quick testing
"""

from mercury_crawler import MercuryCrawler
import sys


def sample_run(sample_size: int = 10):
    """Run crawler on a sample of investors"""
    print(f"🚀 Starting Mercury Crawler - Sample Mode ({sample_size} investors)")
    
    crawler = MercuryCrawler(headless=True, delay=1.0)
    
    try:
        # Collect URLs
        print("📥 Collecting investor URLs...")
        urls = crawler.collect_investor_urls()
        
        if not urls:
            print("❌ No URLs found")
            return
            
        # Take sample
        sample_urls = urls[:sample_size]
        print(f"📊 Running sample with {len(sample_urls)} investors")
        
        # Scrape sample
        investors_data = []
        for i, url in enumerate(sample_urls, 1):
            print(f"🔄 Progress: {i}/{len(sample_urls)} ({i/len(sample_urls)*100:.1f}%)")
            
            investor_data = crawler.scrape_investor_data(url)
            investors_data.append(investor_data)
            
            # Small delay
            if i < len(sample_urls):
                import time
                time.sleep(1.0)
        
        # Save results
        from datetime import datetime
        result = {
            "metadata": {
                "scraped_date": datetime.now().isoformat(),
                "sample_size": len(sample_urls),
                "total_available": len(urls),
                "successful_scrapes": sum(1 for inv in investors_data if inv["status"] == "success"),
                "mode": "sample"
            },
            "investors": investors_data
        }
        
        filename = f"mercury_sample_{sample_size}.json"
        filepath = crawler.save_to_json(result, filename)
        
        print(f"🎉 Sample completed!")
        print(f"📁 Results: {filepath}")
        
    except Exception as e:
        print(f"❌ Sample failed: {e}")
    finally:
        crawler.cleanup()


if __name__ == "__main__":
    sample_size = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    sample_run(sample_size)