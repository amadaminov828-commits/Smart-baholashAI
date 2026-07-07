import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportDocument
from vehicles.models import VehicleValuation

def check_valuation(vid):
    print(f"\n--- Checking Valuation {vid} ---")
    try:
        v = VehicleValuation.objects.get(id=vid)
        print(f"Valuation: {v.car_model}, Owner: {v.owner_name}")
        reports = ReportDocument.objects.filter(object_id=vid, object_type='vehicle').order_by('-created_at')
        if not reports.exists():
            print("No reports found.")
            return
        
        print(f"Found {reports.count()} reports.")
        for r in reports:
            print(f"ID: {r.id}, Created: {r.created_at}, File: {r.file.name if r.file else 'None'}")
            if r.file:
                try:
                    exists = os.path.exists(r.file.path)
                    size = os.path.getsize(r.file.path) if exists else 0
                    print(f"  Path: {r.file.path}")
                    print(f"  Exists on disk: {exists}, Size: {size}")
                except Exception as fe:
                    print(f"  File error: {fe}")
    except Exception as e:
        print(f"Error: {e}")

check_valuation(135)
check_valuation(138)
