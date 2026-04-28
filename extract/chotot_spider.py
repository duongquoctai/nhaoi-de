import requests
import time

class ChototSpider:
    def __init__(self, config):
        self.config = config # Sub-config for chotot
        self.url = self.config["url"]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_listings(self, region_id, area_id=None, page=0, limit=20):
        """
        Fetches raw listings from Chotot API with parameters.
        page is 0-indexed offset multiplier.
        """
        # Calculate offset
        offset = page * limit
        
        params = {
            "cg": self.config["categories"]["house"],
            "region_v2": region_id,
            "limit": limit,
            "o": offset,
            "st": "s" # Newest
        }
        
        if area_id:
            params["area_v2"] = area_id
            
        try:
            print(f"   [Spider] Fetching Chotot - region_v2: {region_id}, area_v2: {area_id}, page: {page}...")
            # Human-like delay
            time.sleep(1.5) 
            
            response = requests.get(self.url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            print(data)
            ads = data.get("ads", [])
            
            # Enrich ads with source_url
            for ad in ads:
                list_id = ad.get("list_id")
                if list_id:
                    ad["source_url"] = f"https://www.nhatot.com/mua-ban-bat-dong-san/{list_id}.htm"
                else:
                    ad["source_url"] = "N/A"
            
            return ads
        except Exception as e:
            print(f"Error fetching from Chotot: {e}")
            return []
