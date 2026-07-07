import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import os

query = urllib.parse.quote("Gentra 2017")
avtoelon_url = f"https://avtoelon.uz/avto/?search={query}"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'uz,ru;q=0.9,en-US;q=0.8,en;q=0.7',
}

resp = requests.get(avtoelon_url, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')

ad_links = soup.find_all('a', href=re.compile(r'/a/show/\d+'))
if ad_links:
    first_ad = ad_links[0]
    # Traverse up 4 levels to get the card
    card = first_ad.parent.parent.parent.parent
    html_content = card.prettify()
    
    with open('C:\\Users\\Asus\\.gemini\\antigravity\\brain\\2f45e962-c686-4ba9-89aa-0a92d2e28258\\avtoelon_debug.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
        f.write("\n\n--- ALL AD LINKS ---\n")
        for a in ad_links[:5]:
            f.write(str(a) + "\n")
