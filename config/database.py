import os
import json
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_site_configs():
    """
    Loads site-specific configurations from config/site_configs.json
    """
    config_path = os.path.join(os.path.dirname(__file__), "site_configs.json")
    with open(config_path, "r") as f:
        return json.load(f)

def get_db_connection():
    """
    Returns a direct Postgres connection using the connection string from .env.
    """
    connection_string = os.getenv("SUPABASE_POSTGRES_CONNECTION")
    if not connection_string:
        raise ValueError("SUPABASE_POSTGRES_CONNECTION NOT FOUND in .env")
    
    try:
        conn = psycopg2.connect(connection_string)
        return conn
    except Exception as e:
        print(f"Error connecting to Postgres: {e}")
        return None

def get_supabase_client():
    """
    Legacy placeholder for Supabase client initialization.
    """
    return {
        "url": os.getenv("SUPABASE_URL"),
        "key": os.getenv("SUPABASE_KEY")
    }
