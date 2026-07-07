import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportDocument

target_uuid = '99ca6838-8ca6-4fb4-89c0-8451f28b3b64'
report = ReportDocument.objects.filter(pk=target_uuid).first()

if report:
    print(f"FOUND: ID={report.id}, status={report.status}, file={report.file.name if report.file else 'EMPTY'}")
else:
    print(f"NOT FOUND: {target_uuid}")
    # Let's list the last 5 reports to see what's in there
    print("\nLast 5 reports:")
    for r in ReportDocument.objects.order_by('-created_at')[:5]:
        print(f"ID={r.id}, status={r.status}, file={r.file.name if r.file else 'EMPTY'}")
