import os
import django
import sys

# Add current directory to path to ensure imports work
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
try:
    django.setup()
    print("✅ Django setup muvaffaqiyatli bajarildi")
except Exception as e:
    print(f"❌ Django setup xatosi: {e}")
    exit(1)

from users.models import User

def fix_user(username, password):
    print(f"\n--- '{username}' foydalanuvchisini tekshirish ---")
    user = User.objects.filter(username__iexact=username).first()
    if user:
        print(f"✅ Foydalanuvchi topildi: {user.username}")
        print(f"   Eski holati: is_active={user.is_active}, role={user.role}")
        user.is_active = True
        user.set_password(password)
        user.save()
        print(f"🚀 Yangilandi: is_active=True qilib belgilandi va parol '{password}' ga o'zgartirildi.")
    else:
        print(f"ℹ️ '{username}' topilmadi. Yangi yaratilmoqda...")
        user = User.objects.create_user(
            username=username,
            password=password,
            is_active=True,
            role='assistant'
        )
        print(f"✨ Yangi foydalanuvchi yaratildi: {username} (Parol: {password})")

# Asosiy foydalanuvchini tuzatish
fix_user('911111111', '12345678')

# Adminni tekshirish
print("\n--- Admin holati ---")
admin = User.objects.filter(username__iexact='admin6179').first()
if admin:
    print(f"👤 Admin mavjud: {admin.username}, is_active: {admin.is_active}")
else:
    print("⚠️ 'admin6179' hali yaratilmagan (Loginda avtomat yaratiladi).")

print("\n--- Barcha foydalanuvchilar ro'yxati ---")
users = User.objects.all()
if not users:
    print("Bazada foydalanuvchilar yo'q.")
for u in users:
    print(f"🔹 {u.username} (Active: {u.is_active}, Role: {u.role})")

print("\n✅ Tamom. Endi brauzerda qayta kiring.")
