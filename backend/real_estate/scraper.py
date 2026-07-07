import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

def search_real_estate_analogs(purpose, location=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'uz,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    
    analogs = []
    loc_query = location or "Toshkent"
    
    # 1. OLX.uz Scraper
    try:
        # Multiple URL formats to increase success rate
        urls = [
            f"https://www.olx.uz/oz/nedvizhimost/kvartiry/prodazha/q-{urllib.parse.quote(loc_query)}/",
            f"https://www.olx.uz/oz/list/q-{urllib.parse.quote(loc_query)}/",
            f"https://www.olx.uz/oz/nedvizhimost/q-{urllib.parse.quote(loc_query)}/"
        ]
        
        for url in urls:
            if len(analogs) >= 5: break
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200: continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                cards = soup.find_all('div', {'data-cy': 'l-card'}, limit=20) or soup.select('div[data-cy="l-card"]')
                
                for card in cards:
                    title_el = card.find('h6') or card.find('h4') or card.find('h3')
                    if not title_el: continue
                    title = title_el.get_text(strip=True)

                    price_els = card.find_all(string=re.compile(r"so['`’‘]?m|сум|y\.e\.|usd|\$", re.IGNORECASE))
                    price_str = price_els[0] if price_els else "0"
                    
                    location_el = card.find('p', {'data-testid': 'location-date'})
                    loc_str = location_el.get_text(strip=True) if location_el else ""
                    
                    norm_loc_query = re.sub(r'[\'ʻ`’‘]', '', loc_query.lower())
                    norm_loc_str = re.sub(r'[\'ʻ`’‘]', '', loc_str.lower())
                    norm_title = re.sub(r'[\'ʻ`’‘]', '', title.lower())
                    
                    # Translate basic cyrillic and known russian cities mapping
                    cyrillic_to_latin = {
                        'қ': 'q', 'ў': 'o', 'ғ': 'g', 'ш': 'sh', 'ч': 'ch', 'ё': 'yo', 'ю': 'yu', 'я': 'ya',
                        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'э': 'e', 'ж': 'j',
                        'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
                        'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'x', 'ц': 'ts'
                    }
                    for cyr, lat in cyrillic_to_latin.items():
                        norm_loc_str = norm_loc_str.replace(cyr, lat)
                        norm_title = norm_title.replace(cyr, lat)
                        
                    synonyms = {
                        "qoqon": ["kokand", "коканд"],
                        "fargona": ["fergana", "фергана"],
                        "buxoro": ["bukhara", "бухара"],
                        "samarqand": ["samarkand", "самарканд"],
                        "toshkent": ["tashkent", "ташкент"],
                        "chirchiq": ["chirchik", "чирчик"],
                        "navoiy": ["navoi", "навои"]
                    }
                    
                    is_match = norm_loc_query in norm_loc_str or norm_loc_query in norm_title
                    if norm_loc_query in synonyms:
                        for syn in synonyms[norm_loc_query]:
                            if syn in loc_str.lower() or syn in title.lower():
                                is_match = True
                                break
                    
                    # Real-world verification: must contain location or be from high-confidence search
                    if not is_match and loc_query != "Toshkent":
                        continue

                    link_el = card.find('a')
                    url_link = "https://www.olx.uz" + link_el['href'] if link_el and 'href' in link_el.attrs else ""
                    
                    clean_price = re.sub(r'[^\d]', '', price_str)
                    price_val = int(clean_price) if clean_price.isdigit() else 0
                    if price_val > 0:
                        if any(curr in str(price_str).lower() for curr in ["y.e", "usd", "$"]) or price_val < 1000000:
                            price_val *= 12850 

                    if price_val < 20000000: continue # Skip fake/token listings

                    rooms_match = re.search(r'(\d+)\s*[-\s]?xona', title.lower())
                    # Extract Area (m2) from title (e.g. "72 m2", "72 kv.m", "72 м2")
                    area_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:m2|м2|kv\.m|кв\.м|square|sq\.m)', title.lower())
                    clean_area = f"{area_match.group(1)} m²" if area_match else "Noma'lum"

                    # Extract real date from loc_str (e.g. "Qo'qon - 29/03/2026")
                    date_match = re.search(r'(\d{2}/\d{2}/\d{4})', loc_str)
                    real_date = date_match.group(1) if date_match else ""
                    clean_location = re.sub(r'\s*-\s*\d{2}/\d{2}/\d{4}', '', loc_str).strip() or loc_query

                    analogs.append({
                        'rooms': int(rooms_match.group(1)) if rooms_match else 3, 
                        'area': clean_area,
                        'price': price_val,
                        'condition': 'Evro' if any(w in title.lower() for w in ['evro', 'lyuks', 'euro']) else 'O`rtacha',
                        'location': clean_location,
                        'url': url_link,
                        'date_posted': real_date,
                        'source': "OLX.uz"
                    })
                    if len(analogs) >= 5: break
            except Exception as inner_e:
                print(f"Scraper individual URL error: {inner_e}")
                continue
    except Exception as e:
        print(f"OLX Scraper main error: {e}")

    # No simulation/mocking. Return only real scraped results.
    return analogs[:5]
