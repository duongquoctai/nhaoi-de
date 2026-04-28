import psycopg2
from psycopg2.extras import execute_values

class SupabaseLoader:
    def __init__(self, conn):
        self.conn = conn

    def load(self, clean_data):
        """
        Loads cleaned data into Supabase Postgres.
        Handles location lookups and property upserts.
        """
        if not clean_data:
            print("No data to load.")
            return

        cursor = self.conn.cursor()
        
        try:
            print(f"--- Loading {len(clean_data)} records to Postgres ---")
            
            for item in clean_data:
                # 1. Get or Insert Location
                loc = item["location"]
                cursor.execute(
                    """
                    INSERT INTO locations (city, district, ward)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (city, district, ward) DO UPDATE SET city=EXCLUDED.city
                    RETURNING id;
                    """,
                    (loc["city"], loc["district"], loc["ward"])
                )
                location_id = cursor.fetchone()[0]

                # 2. Get Property Type ID
                cursor.execute(
                    "SELECT id FROM property_types WHERE name = %s;",
                    (item["property_type_name"],)
                )
                res = cursor.fetchone()
                property_type_id = res[0] if res else 1 # Default to 1 if not found

                # 3. Upsert Property
                values = (
                    location_id, property_type_id, item["source_url"], item["source_site"],
                    item["title"], item["body"], item["price"], item["area"], item["price_per_m2"],
                    item["bedrooms"], item["bathrooms"],
                    item["image_urls"], item["videos"], 
                    item["seller_name"], item["seller_phone"], item["seller_avatar"], item["seller_type"],
                    item["posted_at"]
                )
                
                # 3. Upsert Property
                cursor.execute(
                    """
                    INSERT INTO properties (
                        location_id, property_type_id, source_url, source_site, 
                        title, body, price, area, price_per_m2, bedrooms, bathrooms,
                        image_urls, videos, seller_name, seller_phone, seller_avatar, seller_type,
                        longitude, latitude,
                        posted_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (source_url) DO UPDATE SET
                        price = EXCLUDED.price,
                        area = EXCLUDED.area,
                        price_per_m2 = EXCLUDED.price_per_m2,
                        image_urls = EXCLUDED.image_urls,
                        videos = EXCLUDED.videos,
                        longitude = EXCLUDED.longitude,
                        latitude = EXCLUDED.latitude,
                        is_active = TRUE,
                        updated_at = NOW();
                    """,
                    (
                        location_id, property_type_id, item["source_url"], item["source_site"],
                        item["title"], item["body"], item["price"], item["area"], item["price_per_m2"],
                        item["bedrooms"], item["bathrooms"],
                        item["image_urls"], item["videos"], 
                        item["seller_name"], item["seller_phone"], item["seller_avatar"], item["seller_type"],
                        item["longitude"], item["latitude"],
                        item["posted_at"]
                    )
                )
            
            self.conn.commit()
            print("--- Load Complete ---")
            
        except Exception as e:
            self.conn.rollback()
            print(f"Error loading to Postgres: {e}")
        finally:
            cursor.close()

    def is_url_exists(self, url):
        """
        Checks if a source_url already exists in the database.
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT 1 FROM properties WHERE source_url = %s;", (url,))
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error checking URL existence: {e}")
            return False
        finally:
            cursor.close()
