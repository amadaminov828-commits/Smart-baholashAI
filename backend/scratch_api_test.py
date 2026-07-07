import requests
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/json, text/plain, */*',
}

def test_avtoelon_api():
    print("Testing Avtoelon...")
    # Avtoelon Next.js data or direct search
    try:
        r = requests.get("https://avtoelon.uz/avto/", headers=HEADERS, timeout=10)
        print("Status:", r.status_code)
        
        m = re.search(r'allaqachon\s+([\d\s\xa0]+)\s+ta', r.text, re.IGNORECASE)
        if m:
            print("Total found:", m.group(1).strip())
        else:
            print("Total not found")
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    test_avtoelon_api()
