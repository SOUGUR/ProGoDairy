import os
from dotenv import load_dotenv
import requests
from django.core.cache import cache

load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

def fetch_milk_prices():
    url = "https://www.ncdfi.coop/index.php/civil-consumer-prices/" 
    return _scrape_with_firecrawl(url)

def fetch_dairy_news():
    url = "https://economictimes.indiatimes.com/topic/dairy-industry-in-india"  
    return _scrape_with_firecrawl(url)

def _scrape_with_firecrawl(target_url):
    cache_key = f"firecrawl_{hash(target_url)}"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        print("======="*34)
        print(cached_data)
        print("======="*34)
        return cached_data
    
    api_url = "https://api.firecrawl.dev/v1/scrape"
    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "url": target_url,
        "formats": ["markdown"]
    }
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        scraped_content = data.get("data", {}).get("markdown", "")
        cache.set(cache_key, {"success": True, "content": scraped_content}, timeout=3)  
        return {"success": True, "content": scraped_content}
    except Exception as e:
        return {"success": False, "error": str(e)}