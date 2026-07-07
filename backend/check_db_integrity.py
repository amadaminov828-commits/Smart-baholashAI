import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportDocument
from vehicles.models import VehicleValuation

print("Checking ReportDocument table...")
all_reports = ReportDocument.objects.all().order_by('-created_at')[:10]
if not all_reports.exists():
    print("No reports found in the entire database!")
else:
    for r in all_reports:
        print(f"ID: {r.id} | ObjType: {r.object_type} | ObjID: {r.object_id} | Status: {r.status}")

print("\nChecking VehicleValuation 237...")
v = VehicleValuation.objects.filter(id=237).first()
if v:
    print(f"Vehicle 237 found: {v.car_model} | Status: {v.status}")
    r237 = ReportDocument.objects.filter(object_id=237, object_type='vehicle').first()
    if r237:
        print(f"MATCH FOUND: Report {r237.id} refers to Vehicle 237")
    else:
        print("NO ReportDocument found for Vehicle 237.")
else:
    print("Vehicle 237 not found in DB.")
