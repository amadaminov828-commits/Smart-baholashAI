import os
import sys
import django

sys.path.append(r'C:\Users\Asus\Desktop\antigravity\backend')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "valuation_platform.settings")
django.setup()

from users.models import User
users = User.objects.all()
for u in users:
    print(f"User: {u.username}, Phone: {getattr(u, 'phone_number', 'N/A')}, Role: {getattr(u, 'role', 'N/A')}, Active: {u.is_active}")

    # Let's reset 331111111 if it exists
    if u.username == '331111111' or getattr(u, 'phone_number', '') == '331111111':
        print("Found target user! Resetting password to 2013nnnn...")
        u.set_password('2013nnnn')
        u.is_active = True
        u.save()
        print("Password reset successful.")
