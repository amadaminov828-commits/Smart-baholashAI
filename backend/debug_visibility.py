import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportDocument
from vehicles.models import VehicleValuation

print("--- RECENT REPORTS INSPECTION ---")
reports = ReportDocument.objects.all().order_by('-created_at')[:5]

for r in reports:
    print(f"Report ID: {r.id}")
    print(f"  Object ID: {r.object_id}")
    print(f"  Status: {r.status}")
    print(f"  User (Creator): {r.user}")
    print(f"  Assigned To: {r.assigned_to}")
    
    if r.object_type == 'vehicle' and r.object_id:
        v = VehicleValuation.objects.filter(id=r.object_id).first()
        if v:
            print(f"  Vehicle Status: {v.status}")
            print(f"  Vehicle Assigned To: {v.assigned_to}")
    print("-" * 30)
