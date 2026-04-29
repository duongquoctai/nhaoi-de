import requests
from bs4 import BeautifulSoup

url = "https://alonhadat.com.vn/nha-dat/can-ban/nha-dat/ho-chi-minh/132/quan-1.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")
# print(response.text[:1000])

soup = BeautifulSoup(response.content, "lxml")
items = soup.select("div.content-item")
print(f"Found {len(items)} items with div.content-item")

if len(items) == 0:
    # Try another selector
    items = soup.select(".content-item")
    print(f"Found {len(items)} items with .content-item")
    
    # Let's print all div classes
    # divs = soup.find_all("div", limit=50)
    # for d in divs:
    #     if d.get("class"):
    #         print(d.get("class"))

# Write html to file for inspection
with open("alonhadat_debug.html", "w") as f:
    f.write(response.text)
