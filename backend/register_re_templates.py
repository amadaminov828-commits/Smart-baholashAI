import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportTemplate

def register():
    # 1. Ko'chmas mulk asosiy shabloni (SHABLON.docx - mavjud)
    t1, created = ReportTemplate.objects.get_or_create(
        name='Ko\'chmas mulk shabloni',
        object_type='real_estate'
    )
    t1.file = 'templates/SHABLON.docx'
    t1.is_default = True
    t1.save()
    print(f"{'Yaratildi' if created else 'Yangilandi'}: {t1.name} (ID: {t1.id})")

    # 2. Ko'chmas mulk - Professional shablon
    t2, created = ReportTemplate.objects.get_or_create(
        name='Professional ko\'chmas mulk shabloni',
        object_type='real_estate'
    )
    t2.file = 'templates/Professional_shablon.docx'
    t2.is_default = False
    t2.save()
    print(f"{'Yaratildi' if created else 'Yangilandi'}: {t2.name} (ID: {t2.id})")

    # 3. Garov shabloni - SHABLON.docx ni garov uchun ham ro'yxatdan o'tkazamiz
    t3, created = ReportTemplate.objects.get_or_create(
        name='Garov qiymati shabloni',
        object_type='real_estate'
    )
    t3.file = 'templates/SHABLON.docx'
    t3.is_default = False
    t3.save()
    print(f"{'Yaratildi' if created else 'Yangilandi'}: {t3.name} (ID: {t3.id})")

    print("\nBarcha ko'chmas mulk shablonlari ro'yxatdan o'tkazildi!")
    
    # Barcha real_estate shablonlarini ko'rsatish
    all_re = ReportTemplate.objects.filter(object_type='real_estate')
    print(f"\nJami real_estate shablonlari: {all_re.count()}")
    for t in all_re:
        print(f"  - ID: {t.id} | {t.name} | default: {t.is_default} | fayl: {t.file}")

if __name__ == "__main__":
    register()
