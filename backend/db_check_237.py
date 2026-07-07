import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportDocument
from vehicles.models import VehicleValuation

val_id = 237
val = VehicleValuation.objects.filter(id=val_id).first()
if val:
    print(f"VehicleValuation {val_id} exists. Status: {val.status}")
    reports = ReportDocument.objects.filter(object_id=val_id, object_type='vehicle')
    print(f"Found {reports.count()} reports for this valuation.")
    for r in reports:
        print(f" - Report ID: {r.id}, Created at: {r.created_at}, File: {r.file.name if r.file else 'No file'}")
else:
    print(f"VehicleValuation {val_id} NOT FOUND in database.")
