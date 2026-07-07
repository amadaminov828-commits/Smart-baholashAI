import sys
import os

sys.path.append(r'C:\Users\Asus\Desktop\antigravity\backend')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "valuation_platform.settings")

import django
django.setup()

from users.models import User
users = User.objects.all()

with open(r'C:\Users\Asus\Desktop\antigravity\backend\test_results.txt', 'w') as f:
    for u in users:
        f.write(f"User: {u.username}, Phone: {getattr(u, 'phone_number', 'N/A')}, Role: {getattr(u, 'role', 'N/A')}, Active: {u.is_active}\n")
        if u.username == '331111111' or getattr(u, 'phone_number', '') == '331111111':
            f.write("Found target user! Resetting password to 2013nnnn...\n")
            u.set_password('2013nnnn')
            u.is_active = True
            u.save()
            f.write("Password reset successful.\n")
