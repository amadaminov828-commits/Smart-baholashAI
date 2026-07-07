import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportDocument
from vehicles.models import VehicleValuation

print("Updating historical reports to pending to fix the user's view...")
reports = ReportDocument.objects.all().order_by('-created_at')[:10]
for r in reports:
    if r.status == 'draft' or not r.status:
        r.status = 'pending'
        r.save()
        print(f"Updated ReportDocument {r.id} to pending")
    
    if r.object_type == 'vehicle' and r.object_id:
        val = VehicleValuation.objects.filter(id=r.object_id).first()
        if val and (val.status == 'draft' or not val.status):
            val.status = 'pending'
            val.save()
            print(f"Updated VehicleValuation {val.id} to pending")

print("Done.")
