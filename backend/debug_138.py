import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from vehicles.models import VehicleValuation
from reports.models import ReportDocument

try:
    v138 = VehicleValuation.objects.get(id=138)
    print(f"Valuation 138 found: {v138.car_model}")
    reports = ReportDocument.objects.filter(object_id=v138.id, object_type='vehicle').order_by('-created_at')
    for report in reports:
        print(f"ReportDocument: ID={report.id}, File={report.file}, Created={report.created_at}")
        if report.file:
            path = report.file.path
            print(f"  Path: {path}")
            print(f"  Exists: {os.path.exists(path)}")
            if os.path.exists(path):
                print(f"  Size: {os.path.getsize(path)} bytes")
except Exception as e:
    print(f"Error checking 138: {e}")
