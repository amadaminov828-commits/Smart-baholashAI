import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportDocument
from vehicles.models import VehicleValuation

reports = ReportDocument.objects.all().order_by('-created_at')[:10]
print("Recent Reports:")
for r in reports:
    print(f"Report ID: {r.id}, Object ID: {r.object_id}, Object Type: {r.object_type}, Report Status: {getattr(r, 'status', 'N/A')}")
    if r.object_type == 'vehicle' and r.object_id:
        val = VehicleValuation.objects.filter(id=r.object_id).first()
        if val:
            print(f"  -> Valuation ID: {val.id}, Valuation Status: {val.status}")
