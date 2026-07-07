import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportTemplate

def register():
    # 1. Odiy shablon
    t1, created = ReportTemplate.objects.get_or_create(
        name='Odiy shablon', 
        object_type='vehicle'
    )
    t1.file = 'templates/SHABLON.docx'
    t1.save()
    print(f"{'Created' if created else 'Updated'}: {t1.name} (ID: {t1.id})")

    # 2. Professional shablon
    t2, created = ReportTemplate.objects.get_or_create(
        name='Professional shablon', 
        object_type='vehicle'
    )
    t2.file = 'templates/Professional_shablon.docx'
    t2.save()
    print(f"{'Created' if created else 'Updated'}: {t2.name} (ID: {t2.id})")

if __name__ == "__main__":
    register()
