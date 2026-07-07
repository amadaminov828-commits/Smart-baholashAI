import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from vehicles.views import convert_docx_to_pdf
import inspect

print(f"Function convert_docx_to_pdf is defined in: {inspect.getfile(convert_docx_to_pdf)}")

# Check for valuation 135
from vehicles.models import VehicleValuation
from reports.models import ReportDocument

try:
    v135 = VehicleValuation.objects.get(id=135)
    print(f"Valuation 135 found: {v135.car_model}")
    report = ReportDocument.objects.filter(object_id=v135.id, object_type='vehicle').first()
    if report:
        print(f"ReportDocument for 135 found: ID={report.id}, File={report.file}")
        if report.file:
            print(f"File exists: {os.path.exists(report.file.path)} (Path: {report.file.path})")
            if os.path.exists(report.file.path):
                print(f"File size: {os.path.getsize(report.file.path)} bytes")
    else:
        print("No ReportDocument found for valuation 135")
except VehicleValuation.DoesNotExist:
    print("Valuation 135 does not exist")
except Exception as e:
    print(f"Error checking 135: {e}")
