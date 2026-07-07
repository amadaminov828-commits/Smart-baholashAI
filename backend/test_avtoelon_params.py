import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'uz,ru;q=0.9,en-US;q=0.8,en;q=0.7',
}

urls_to_test = [
    "https://avtoelon.uz/avto/?q=Gentra+2017",
    "https://avtoelon.uz/avto/?text=Gentra+2017",
    "https://avtoelon.uz/avto/chevrolet/lacetti/",
]

for u in urls_to_test:
    resp = requests.get(u, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    ad_links = soup.find_all('a', href=re.compile(r'/a/show/\d+'))
    
    titles = []
    for a in ad_links[:5]:
        titles.append(a.get_text(strip=True))
    
    print(f"URL: {u}")
    print(f"Status: {resp.status_code}")
    print(f"Titles: {titles}")
    print("-" * 30)
