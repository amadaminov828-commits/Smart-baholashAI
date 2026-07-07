import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from users.models import User

username = 'admin6179'
password = '2013nnnn'

try:
    admin = User.objects.filter(username=username).first()
    if not admin:
        admin = User.objects.create_superuser(
            username=username,
            phone_number=username, # telefon raqam o'rniga shu loginni ishlatamiz
            password=password,
            role='admin',
            full_name='Asosiy Administrator'
        )
        print(f"✅ Admin muvaffaqiyatli yaratildi!\nLogin: {username}\nParol: {password}")
    else:
        admin.set_password(password)
        admin.role = 'admin'
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()
        print(f"✅ Admin topildi va parol yangilandi!\nLogin: {username}\nParol: {password}")
except Exception as e:
    print(f"❌ Xatolik yuz berdi: {e}")
