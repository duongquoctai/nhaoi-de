import time
import random
from config.database import load_site_configs
from main_pipeline import run_pipeline

def main():
    print("=== Starting Muanha ETL Orchestrator ===")
    site_configs = load_site_configs()
    
    for site_name, config in site_configs.items():
        # Task 3: Check if site is enabled
        is_enabled = config.get("enable", True)
        if not is_enabled:
            print(f"\n--- Site '{site_name}' is disabled, skipping. ---")
            continue
            
        print(f"\n>>> Processing Site: {site_name} <<<")
        
        cities = config.get("cities", {})
        for city_name in cities.keys():
            print(f"\n--- Running Job: {site_name} | {city_name} ---")
            
            try:
                # Run the pipeline for the entire city (all districts)
                run_pipeline(site_name, city_name, district_name=None)
                
                # Anti-bot delay between cities
                city_delay = random.randint(10, 20)
                print(f"\n[Orchestrator] Finished {city_name}. Waiting {city_delay}s before next city...")
                time.sleep(city_delay)
                
            except Exception as e:
                print(f"Error running pipeline for {site_name}/{city_name}: {e}")
                
        # Anti-bot delay between sites
        site_delay = 10
        print(f"\n[Orchestrator] Finished all cities for {site_name}. Waiting {site_delay}s before next site...")
        time.sleep(site_delay)

    print("\n=== All ETL Jobs Completed ===")

if __name__ == "__main__":
    main()
