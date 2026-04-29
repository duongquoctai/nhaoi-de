# transform/cleaner.py
import datetime

class DataCleaner:
    def clean_chotot_data(self, raw_ads):
        """
        Transforms raw Chotot data into a unified schema matching properties + locations.
        """
        clean_data = []
        for ad in raw_ads:
            # Basic info
            price = ad.get("price", 0)
            size = ad.get("size", 0)
            
            # Price per m2 calculation
            price_per_m2 = price / size if size > 0 else 0
            
            # Mapping property type
            # Categories: 1020 is Houses
            property_type_name = "Nhà ngõ / Hẻm" 
            subject = ad.get("subject", "").lower()
            if "mặt phố" in subject or ad.get("is_main_street"):
                property_type_name = "Nhà mặt phố"
            elif "biệt thự" in subject:
                property_type_name = "Biệt thự"
            elif ad.get("category") == 1010: # Apartment
                property_type_name = "Căn hộ / Chung cư"

            # Date handling: Use list_time (timestamp in ms)
            list_time = ad.get("list_time")
            posted_at = None
            if list_time:
                posted_at = datetime.datetime.fromtimestamp(list_time / 1000.0, tz=datetime.timezone.utc).isoformat()
            else:
                posted_at = ad.get("date") # Fallback to relative string

            # Seller info
            seller_info = ad.get("seller_info", {})
            seller_type = "Môi giới" if ad.get("company_ad") else "Cá nhân"
            
            # Seller phone extraction (Chotot often doesn't give this in listing json)
            # We'll leave it empty for now or try to find it in body if user wants
            seller_phone = None 

            # Robust media handling: ensure we only have strings
            image_urls = []
            for img in ad.get("images", []):
                if isinstance(img, str):
                    image_urls.append(img)
                elif isinstance(img, dict) and "image" in img: # Handle potential thumb objects
                    image_urls.append(img["image"])

            video_urls = []
            for vid in ad.get("videos", []):
                if isinstance(vid, str):
                    video_urls.append(vid)
                elif isinstance(vid, dict) and "url" in vid:
                    video_urls.append(vid["url"])

            clean_item = {
                "source_site": "chotot",
                "source_url": ad.get("source_url"),
                "title": ad.get("subject"),
                "body": ad.get("body", ""),
                "price": price,
                "area": size,
                "price_per_m2": price_per_m2,
                "bedrooms": ad.get("rooms"),
                "bathrooms": ad.get("toilets"),
                "posted_at": posted_at,
                "image_urls": image_urls,
                "videos": video_urls,
                "seller_name": seller_info.get("full_name") or ad.get("account_name"),
                "seller_phone": seller_phone,
                "seller_avatar": seller_info.get("avatar") or ad.get("avatar"),
                "seller_type": seller_type,
                "longitude": str(ad.get("longitude")) if ad.get("longitude") else None,
                "latitude": str(ad.get("latitude")) if ad.get("latitude") else None,
                
                # Location info for the loader to handle
                "location": {
                    "city": "TP Hồ Chí Minh",
                    "district": ad.get("area_name"),
                    "ward": ad.get("ward_name")
                },
                "property_type_name": property_type_name
            }
            clean_data.append(clean_item)
        return clean_data

    def parse_vn_price(self, price_str):
        """
        Parses Vietnamese price strings like '65 tỷ', '5,26 tỷ', '28 triệu/tháng'
        Returns price in VND as integer.
        """
        if not price_str or "thỏa thuận" in price_str.lower():
            return 0
            
        try:
            # Remove non-numeric characters except comma and dot
            import re
            
            # Extract number
            match = re.search(r"(\d+([,.]\d+)?)", price_str.replace(",", "."))
            if not match:
                return 0
                
            value = float(match.group(1))
            
            if "tỷ" in price_str.lower():
                return int(value * 1_000_000_000)
            elif "triệu" in price_str.lower():
                return int(value * 1_000_000)
            return int(value)
        except:
            return 0

    def parse_vn_area(self, area_str):
        """
        Parses area strings like '700 m²', '123m2'
        Returns area as float.
        """
        if not area_str:
            return 0.0
        try:
            import re
            match = re.search(r"(\d+([,.]\d+)?)", area_str.replace(",", "."))
            if match:
                return float(match.group(1))
            return 0.0
        except:
            return 0.0

    def parse_vn_date(self, date_str):
        """
        Parses Alonhadat date strings like 'Hôm nay', 'Hôm qua', '28/04/2026'
        Returns ISO timestamp or None.
        """
        if not date_str:
            return None
        
        now = datetime.datetime.now(datetime.timezone.utc)
        date_str = date_str.lower()
        
        try:
            if "hôm nay" in date_str:
                return now.isoformat()
            elif "hôm qua" in date_str:
                yesterday = now - datetime.timedelta(days=1)
                return yesterday.isoformat()
            
            # Match dd/mm/yyyy
            import re
            match = re.search(r"(\d{2}/\d{2}/\d{4})", date_str)
            if match:
                dt = datetime.datetime.strptime(match.group(1), "%d/%m/%Y")
                dt = dt.replace(tzinfo=datetime.timezone.utc)
                return dt.isoformat()
        except:
            pass
            
        return None

    def clean_alonhadat_data(self, raw_ads):
        """
        Transforms raw Alonhadat data into unified schema.
        """
        clean_data = []
        for ad in raw_ads:
            price = self.parse_vn_price(ad.get("price_text", ""))
            size = self.parse_vn_area(ad.get("area_text", ""))
            
            price_per_m2 = price / size if size > 0 else 0
            
            # Simple property type mapping from title
            property_type_name = "Nhà ngõ / Hẻm" 
            title_lower = ad.get("title", "").lower()
            if "mặt tiền" in title_lower or "mặt phố" in title_lower:
                property_type_name = "Nhà mặt phố"
            elif "biệt thự" in title_lower:
                property_type_name = "Biệt thự"
            elif "căn hộ" in title_lower or "chung cư" in title_lower:
                property_type_name = "Căn hộ / Chung cư"

            # Date handling
            posted_at = self.parse_vn_date(ad.get("date_text", ""))
            
            # Location parsing from location_text
            # e.g. "Đường Điện Biên Phủ, Phường Đa Kao, Quận 1, Hồ Chí Minh"
            loc_parts = [p.strip() for p in ad.get("location_text", "").split(",")]
            city = loc_parts[-1] if len(loc_parts) > 0 else "TP Hồ Chí Minh"
            district = loc_parts[-2] if len(loc_parts) > 1 else ""
            ward = loc_parts[-3] if len(loc_parts) > 2 else ""

            clean_item = {
                "source_site": "alonhadat",
                "source_url": ad.get("source_url"),
                "title": ad.get("title"),
                "body": ad.get("description", ""),
                "price": price,
                "area": size,
                "price_per_m2": price_per_m2,
                "bedrooms": None, 
                "bathrooms": None,
                "posted_at": posted_at,
                "image_urls": [ad.get("image_url")] if ad.get("image_url") else [],
                "videos": [],
                "seller_name": None, 
                "seller_phone": None,
                "seller_avatar": None,
                "seller_type": "Cá nhân", 
                "longitude": None,
                "latitude": None,
                
                "location": {
                    "city": city,
                    "district": district,
                    "ward": ward
                },
                "property_type_name": property_type_name
            }
            clean_data.append(clean_item)
        return clean_data

    def clean(self, raw_data, source):
        if source == "chotot":
            return self.clean_chotot_data(raw_data)
        elif source == "alonhadat":
            return self.clean_alonhadat_data(raw_data)
        return []
