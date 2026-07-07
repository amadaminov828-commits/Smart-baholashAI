import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportTemplate

count = ReportTemplate.objects.all().count()
ReportTemplate.objects.all().delete()
print(f"Successfully deleted {count} templates.")
