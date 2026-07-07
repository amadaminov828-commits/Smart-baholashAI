import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportDocument

try:
    reports = ReportDocument.objects.filter(object_id=138, object_type='vehicle').order_by('-created_at')
    if not reports:
        print("No reports found for valuation 138")
    for report in reports:
        print(f"ID: {report.id}, File: {report.file.name if report.file else 'None'}")
        if report.file:
            try:
                print(f"  Path: {report.file.path}")
                print(f"  Exists: {os.path.exists(report.file.path)}")
                if os.path.exists(report.file.path):
                    print(f"  Size: {os.path.getsize(report.file.path)} bytes")
            except Exception as e:
                print(f"  Error checking file: {e}")
except Exception as e:
    print(f"Error querying 138: {e}")
