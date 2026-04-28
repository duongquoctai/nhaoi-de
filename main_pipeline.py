import argparse
import sys
from extract.chotot_spider import ChototSpider
from extract.alonhadat_spider import AlonhadatSpider
from transform.cleaner import DataCleaner
from load.supabase_loader import SupabaseLoader
from config.database import get_db_connection, load_site_configs
import time
import random

def run_pipeline(site_name, city_name, district_name=None):
    print(f"=== Muanha Data Pipeline: {site_name} | {city_name} | {district_name or 'All Districts'} ===")
    
    # 1. Setup
    site_configs = load_site_configs()
    if site_name not in site_configs:
        print(f"Error: Site '{site_name}' not found in configs.")
        return
        
    config = site_configs[site_name]
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database. Exiting.")
        return
        
    try:
        cleaner = DataCleaner()
        loader = SupabaseLoader(conn)
        
        # Determine Spider
        if site_name == "chotot":
            spider = ChototSpider(config)
        else:
            spider = AlonhadatSpider(config)
            
        region_id = config["cities"].get(city_name)
        if not region_id:
            print(f"Error: City '{city_name}' not mapped for '{site_name}'.")
            return
            
        # Determine Districts to crawl
        districts_to_crawl = {}
        if district_name:
            d_id = config["districts"].get(city_name, {}).get(district_name)
            if not d_id:
                print(f"Error: District '{district_name}' not found for '{city_name}'.")
                return
            districts_to_crawl = {district_name: d_id}
        else:
            districts_to_crawl = config["districts"].get(city_name, {})

        # 2. Extract, Transform, Load Loop
        for d_name, d_id in districts_to_crawl.items():
            print(f"\n[Processing District: {d_name}]")
            existing_count = 0
            MAX_EXISTING_THRESHOLD = 15
            
            for page in range(0, 50): # Max 50 pages safety
                raw_data = spider.fetch_listings(region_id=region_id, area_id=d_id, page=page)
                if not raw_data:
                    print(f"   No more records found in {d_name} page {page}.")
                    break
                    
                # Incremental Check
                new_on_page = 0
                for item in raw_data:
                    # Construct source_url (Spider already does this)
                    url = item.get("source_url")
                    if loader.is_url_exists(url):
                        existing_count += 1
                    else:
                        new_on_page += 1
                
                print(f"   Page {page}: found {new_on_page} new, total existing so far: {existing_count}")
                
                # Transform & Load
                clean_data = cleaner.clean(raw_data, source=site_name)
                loader.load(clean_data)
                sleep_time = random.uniform(2, 5)
                print(f"   -> Break {sleep_time:.1f}s before {page + 1}")
                time.sleep(sleep_time)
                
                # Break condition
                if existing_count >= MAX_EXISTING_THRESHOLD:
                    print(f"   Threshold reached ({existing_count} existing). Breaking loop for {d_name}.")
                    break
            
        print("\n=== Pipeline Execution Finished Successfully ===")
        
    except Exception as e:
        print(f"Pipeline execution failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Muanha Data ETL Pipeline")
    parser.add_argument("--site", required=True, help="Site to crawl (chotot, alonhadat)")
    parser.add_argument("--city", required=True, help="City to crawl (hcm, hn)")
    parser.add_argument("--district", help="Specific district key (e.g., q1, q2)")
    
    args = parser.parse_args()
    run_pipeline(args.site, args.city, args.district)
