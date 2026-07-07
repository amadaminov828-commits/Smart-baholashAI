import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'uz,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

def test_search(query_str):
    query = urllib.parse.quote(query_str)
    url_olx = f"https://www.olx.uz/oz/transport/legkovye-avtomobili/q-{query}/"
    url_avto = f"https://avtoelon.uz/avto/?search={query}"
    
    print(f"Testing queries for: '{query_str}'")
    
    # Test OLX
    try:
        r = requests.get(url_olx, headers=headers, timeout=10)
        print(f"OLX Status: {r.status_code}")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            cards = soup.find_all('div', {'data-cy': 'l-card'})
            print(f"OLX Cards found: {len(cards)}")
            if len(cards) > 0:
                print("First OLX title:", cards[0].find('h6').get_text(strip=True) if cards[0].find('h6') else "No title")
    except Exception as e:
        print(f"OLX error: {e}")
        
    # Test Avtoelon
    try:
        r = requests.get(url_avto, headers=headers, timeout=10)
        print(f"Avtoelon Status: {r.status_code}")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            ad_links = soup.find_all('a', href=re.compile(r'/a/show/\d+'))
            print(f"Avtoelon links found: {len(ad_links)}")
            if len(ad_links) > 0:
                print("First Avtoelon title:", ad_links[0].get_text(strip=True))
    except Exception as e:
        print(f"Avtoelon error: {e}")

test_search("Lacetti 2017")
test_search("Lacetti")
