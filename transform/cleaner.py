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

    def clean(self, raw_data, source):
        if source == "chotot":
            return self.clean_chotot_data(raw_data)
        return []
