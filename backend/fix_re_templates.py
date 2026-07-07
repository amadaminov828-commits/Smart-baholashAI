import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportTemplate

# Noto'g'ri shablonlarni o'chirish (mashina shabloni va 11.docx real_estate sifatida yozilgan)
wrong_ids = [144, 148]
for wid in wrong_ids:
    try:
        t = ReportTemplate.objects.get(id=wid)
        print(f"O'chirilmoqda: ID {t.id} | {t.name} | {t.file}")
        t.delete()
        print(f"  -> O'chirildi!")
    except ReportTemplate.DoesNotExist:
        print(f"ID {wid} topilmadi, davom etilmoqda...")

# Natijani ko'rsatish
print("\nJoriy real_estate shablonlari:")
for t in ReportTemplate.objects.filter(object_type='real_estate'):
    print(f"  - ID: {t.id} | {t.name} | default: {t.is_default} | fayl: {t.file}")
