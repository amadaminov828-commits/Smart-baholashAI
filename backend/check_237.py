import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportDocument

target_id = 237
print(f"--- DATABASE INSPECTION FOR OBJECT_ID {target_id} ---")

reports = ReportDocument.objects.filter(object_id=target_id).order_by('-created_at')
for r in reports:
    print(f"ID: {r.id}")
    print(f"  Created: {r.created_at}")
    print(f"  Status: {r.status}")
    print(f"  File Field: '{r.file}'")
    if r.file:
        full_path = r.file.path
        exists = os.path.exists(full_path)
        print(f"  Physical Path: {full_path}")
        print(f"  File Exists on Disk: {exists}")
    print("-" * 30)
