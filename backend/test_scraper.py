import os
import sys
import django

# Setup Django environment to reuse search_analogs
sys.path.append('c:/Users/Asus/Desktop/antigravity/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# django.setup() # Not strictly needed if we just import the scraper

try:
    from vehicles.scraper import search_analogs
    print("Scraper imported successfully.")
except Exception as e:
    print(f"Import error: {e}")
    # Fallback to local import simulation if django setup fails
    sys.path.append('.')

def test_scraper_logic():
    # We want to test the regex and logic inside search_analogs
    # Since search_analogs makes real web requests, we might mock it or just check the logic if we could.
    # But I can also just run it for a known model and see if it picks up years and handles prices.
    
    print("\n--- Testing search_analogs with 'Nexia 3' ---")
    analogs = search_analogs("Nexia 3", year=2022, usd_rate=12600.0)
    
    for a in analogs:
        print(f"Title: {a['model_name']}")
        print(f"Extracted Year: {a['year']}")
        print(f"Extracted Price: ${a['price']}")
        print(f"Source: {a['source']}")
        print("-" * 20)

if __name__ == "__main__":
    test_scraper_logic()
