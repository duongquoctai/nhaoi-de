import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn_str = os.getenv("SUPABASE_POSTGRES_CONNECTION")
conn = psycopg2.connect(conn_str)
cursor = conn.cursor()

cursor.execute("""
    SELECT source_site, title, price, area, posted_at 
    FROM properties 
    WHERE source_site = 'alonhadat' 
    LIMIT 5;
""")

rows = cursor.fetchall()
print("--- Sample Alonhadat Records ---")
for row in rows:
    print(row)

cursor.close()
conn.close()
