
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportTemplate

print("Currently registered templates:")
templates = ReportTemplate.objects.all()
for t in templates:
    print(f"ID: {t.id}, Name: {t.name}, Type: {t.object_type}, File: {t.file.name}")


# Rename templates to be more professional
t1 = ReportTemplate.objects.filter(id=1).first()
if t1:
    t1.name = "Professional Baholash (Standart)"
    t1.save()
    print(f"Renamed ID 1 to: {t1.name}")

t3 = ReportTemplate.objects.filter(id=3).first()
if t3:
    t3.name = "Professional Baholash"
    t3.save()
    print(f"Renamed ID 3 to: {t3.name}")

