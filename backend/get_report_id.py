import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportDocument

r = ReportDocument.objects.exclude(file='').order_by('-created_at').first()
if r:
    print(f"REPORT_ID={r.id}")
else:
    print("No reports with files found")
