import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportDocument

target_id = 237
print(f"--- ANALYZING REPORTS FOR OBJECT_ID {target_id} ---")

reports = ReportDocument.objects.filter(object_id=target_id).order_by('-created_at')
print(f"Found {reports.count()} reports.\n")

for i, r in enumerate(reports):
    print(f"{i+1}. UUID: {r.id}")
    print(f"   Created: {r.created_at}")
    print(f"   Status: {r.status}")
    print(f"   File Value: '{r.file}'")
    if r.file:
        file_exists = os.path.exists(r.file.path) if r.file.name else False
        print(f"   Physical File Path: {r.file.path if r.file.name else 'N/A'}")
        print(f"   Physical File Exists: {file_exists}")
    else:
        print(f"   Physical File Exists: False (Field is empty)")
    print("-" * 40)

# Also check if there's any report for this ID that our current filter would find
test_filter = ReportDocument.objects.filter(
    object_id=target_id, 
    object_type='vehicle'
).exclude(file='').exclude(file__isnull=True).order_by('-created_at').first()

if test_filter:
    print(f"\nSUCCESS: Current filter found report: {test_filter.id}")
    print(f"File: {test_filter.file.url}")
else:
    print("\nFAILURE: Current filter found NOTHING with a file.")
