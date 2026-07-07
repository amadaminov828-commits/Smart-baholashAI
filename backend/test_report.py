import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from vehicles.models import VehicleValuation
from reports.models import ReportDocument
from vehicles.serializers import VehicleValuationSerializer

valuations = VehicleValuation.objects.filter(status='pending').order_by('-id')
for val in valuations:
    print(f"\n--- Valuation ID: {val.id} ---")
    reports = ReportDocument.objects.filter(object_id=val.id, object_type='vehicle')
    print(f"Found reports: {reports.count()}")
    for r in reports:
        print(f" - Report ID: {r.id}, File: {r.file}, URL: {getattr(r.file, 'url', None)}")
    
    # Let's see what the serializer outputs!
    serializer = VehicleValuationSerializer(val)
    print(f"Serializer Output: pdf={serializer.data.get('report_file_pdf')}, docx={serializer.data.get('report_file_docx')}, qr={serializer.data.get('qr_url')}")
    
print('\nDone.')
