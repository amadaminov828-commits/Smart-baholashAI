import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment if needed (though scraper doesn't depend on Django models directly)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

from vehicles.scraper import search_analogs

print("Starting Scraper Debug Test...")
try:
    results = search_analogs("LACETTI", 2017, usd_rate=12600.0)
    print(f"Scraper returned {len(results)} results:")
    for i, r in enumerate(results):
        print(f"[{i}] Title: {r['model_name']} | Price: {r['price']} | URL: {r['url']} | Source: {r['source']}")
except Exception as e:
    import traceback
    print("CRITICAL ERROR running scraper:")
    traceback.print_exc()
