import requests
from bs4 import BeautifulSoup
import time
import random

class AlonhadatSpider:
    def __init__(self, config):
        self.config = config
        self.name = "Alonhadat"
        self.base_url = config.get("base_url", "https://alonhadat.com.vn")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_listings(self, region_id, area_id=None, page=0, limit=20):
        """
        Fetches listings from Alonhadat using HTML scraping.
        Note: Alonhadat page starts from 1. Pipeline sends page starting from 0.
        """
        alon_page = page + 1
        city_slug = region_id # e.g. "ho-chi-minh"
        
        # area_id for alonhadat is a dict: {"id": 132, "slug": "quan-1"}
        if not area_id or not isinstance(area_id, dict):
            print(f"   [Spider] Invalid area_id for Alonhadat: {area_id}")
            return []
            
        dist_id = area_id["id"]
        dist_slug = area_id["slug"]
        
        # Construct URL
        # Pattern: /nha-dat/can-ban/nha-dat/{city}/{district_id}/{district_slug}.html
        # Page 2+: /nha-dat/can-ban/nha-dat/{city}/{district_id}/{district_slug}/trang--{page}.html
        
        path = self.config["listing_path"].format(
            city=city_slug,
            district_id=dist_id,
            district_slug=dist_slug
        )
        
        if alon_page > 1:
            path = path.replace(".html", f"/trang--{alon_page}.html")
            
        url = f"{self.base_url}{path}"
        print(f"   [Spider] Fetching Alonhadat: {url}")
        
        # Human-like delay to anti-bot
        time.sleep(random.uniform(2, 5))
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "lxml")
            items = soup.select("article.property-item")
            
            raw_ads = []
            for item in items:
                # Title & URL
                link_tag = item.select_one("a.link")
                if not link_tag:
                    continue
                    
                title_tag = link_tag.select_one("h3.property-title")
                title = title_tag.get_text(strip=True) if title_tag else link_tag.get_text(strip=True)
                source_url = self.base_url + link_tag["href"] if link_tag["href"].startswith("/") else link_tag["href"]
                
                # Price & Area
                price_tag = item.select_one("span.price")
                price_text = price_tag.get_text(strip=True) if price_tag else ""
                
                area_tag = item.select_one("span.area")
                area_text = area_tag.get_text(strip=True) if area_tag else ""
                
                # Description
                description_tag = item.select_one("p.brief")
                description = description_tag.get_text(strip=True) if description_tag else ""
                
                # Image
                img_tag = item.select_one("div.thumbnail img")
                image_url = img_tag["src"] if img_tag else None
                if image_url and image_url.startswith("/"):
                    image_url = self.base_url + image_url
                
                # Date
                date_tag = item.select_one("time.created-date")
                date_text = date_tag.get_text(strip=True) if date_tag else ""
                
                # Location (District/Ward)
                # Alonhadat has old-address span
                location_tag = item.select_one("p.old-address span")
                location_text = location_tag.get_text(strip=True) if location_tag else ""
                
                raw_ads.append({
                    "title": title,
                    "source_url": source_url,
                    "price_text": price_text,
                    "area_text": area_text,
                    "description": description,
                    "image_url": image_url,
                    "date_text": date_text,
                    "location_text": location_text,
                    "site": "alonhadat"
                })
                
            return raw_ads
            
        except Exception as e:
            print(f"   [Spider] Error fetching Alonhadat: {e}")
            return []
