import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from vehicles.scraper import search_analogs

model = "Chevrolet Cobalt"
year = 2020
usd_rate = 12600.0

print(f"Searching analogs for {model} ({year})...")
try:
    results = search_analogs(model, year, usd_rate=usd_rate)
    print(f"Found {len(results)} analogs.")
    for i, a in enumerate(results):
        print(f"{i+1}. {a['model_name']} - {a['price']} USD - {a['url'][:50]}...")
except Exception as e:
    print(f"Scraping Error: {e}")
    import traceback
    traceback.print_exc()
