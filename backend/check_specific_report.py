import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportDocument

target_uuid = "d46937bc-750b-429e-845f-9d48a8dce75e"
print(f"Checking Report {target_uuid}...")

try:
    r = ReportDocument.objects.get(id=uuid.UUID(target_uuid))
    print(f"ID: {r.id}")
    print(f"Object ID: {r.object_id}")
    print(f"File Name: {r.file.name if r.file else 'None'}")
    print(f"File Size: {r.file.size if r.file and r.file.name else 'N/A'}")
    print(f"Status: {r.status}")
except Exception as e:
    print(f"Error finding report: {e}")

print("\nListing all reports for object_id 237:")
for r in ReportDocument.objects.filter(object_id=237).order_by('-created_at'):
    print(f"UUID: {r.id} | File: {r.file.name if r.file else 'None'} | Created: {r.created_at}")
