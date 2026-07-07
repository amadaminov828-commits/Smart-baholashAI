import os
import django
import sys

# Add current directory to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from users.models import User

username = '916996179'
user = User.objects.filter(username__iexact=username).first()

if user:
    print(f"USER_FOUND: {user.username}")
    print(f"IS_ACTIVE: {user.is_active}")
    print(f"PASSWORD_HASH: {user.password[:20]}...")
else:
    print("USER_NOT_FOUND")

all_users = User.objects.all()
print("ALL_USERS:")
for u in all_users:
    print(f"- {u.username} (Active: {u.is_active}, Role: {u.role})")
