import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from vehicles.models import VehicleValuation, VehicleAnalog
from vehicles.scraper import search_analogs

print("Refreshing analogs for all valuations...")
valuations = VehicleValuation.objects.all()
for index, val in enumerate(valuations):
    try:
        print(f"[{index+1}/{len(valuations)}] Processing: {val.car_model} ({val.year})")
        # Delete old analogs
        val.analogs.all().delete()
        
        # Fetch new analogs
        analogs_data = search_analogs(val.car_model, val.year)
        
        for data in analogs_data:
            VehicleAnalog.objects.create(valuation=val, **data)
            
        print(f"  -> Saved {len(analogs_data)} analogs.")
    except Exception as e:
        print(f"  -> Error: {e}")

print("Done!")
