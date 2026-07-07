import django
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "valuation_platform.settings")
django.setup()

from reports.models import ReportDocument
from vehicles.models import VehicleValuation

for v_id in [135, 151]:
    reports = ReportDocument.objects.filter(object_id=v_id, object_type='vehicle').order_by('-created_at')
    print(f"Valuation {v_id} Reports:")
    for r in reports:
        print(f" - Report ID: {r.id}, File: {r.file.name if r.file else 'NONE'}")
