"""Quick test to verify Avtoelon.uz scraping works."""
import requests
import re
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

def test_avtoelon():
    url = "https://avtoelon.uz/avto/?search=cobalt&price-currency=1"
    print(f"Testing: {url}")
    
    resp = requests.get(url, headers=HEADERS, timeout=15)
    print(f"Status: {resp.status_code}")
    print(f"Content length: {len(resp.text)}")
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Try different selectors
    selectors = [
        'div.a-list-item',
        'div.a-elem',
        'a.a-elem__title',
        'span.a-elem__price',
        '.products-list-item',
        'div[class*="list"]',
        'div[class*="item"]',
        'div[class*="card"]',
        'div[class*="product"]',
    ]
    
    for sel in selectors:
        found = soup.select(sel)
        if found:
            print(f"\n✅ '{sel}' → {len(found)} items found")
            if len(found) > 0:
                first = found[0]
                print(f"   First item classes: {first.get('class', [])}")
                print(f"   First item text[:200]: {first.get_text(strip=True)[:200]}")
        else:
            print(f"❌ '{sel}' → 0 items")
    
    # Also check total count pattern
    count_patterns = [
        r'allaqachon\s+([\d\s\xa0]+)\s+ta',
        r'([\d\s\xa0]+)\s+ta\s+mavjud',
    ]
    for p in count_patterns:
        m = re.search(p, resp.text, re.IGNORECASE)
        if m:
            print(f"\n📊 Count found: {m.group(1).strip()}")
    
    # Print all unique class names containing relevant words
    print("\n--- All relevant class names ---")
    all_classes = set()
    for el in soup.find_all(True, class_=True):
        for cls in el.get('class', []):
            if any(w in cls.lower() for w in ['list', 'item', 'elem', 'card', 'price', 'title', 'auto', 'product']):
                all_classes.add(cls)
    for c in sorted(all_classes):
        print(f"  .{c}")

if __name__ == '__main__':
    test_avtoelon()
