import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from users.models import User

def check_user(username):
    user = User.objects.filter(username__iexact=username).first()
    if user:
        print(f"User: {user.username}")
        print(f"  ID: {user.id}")
        print(f"  Active: {user.is_active}")
        print(f"  Role: {user.role}")
        print(f"  Has password: {user.has_usable_password()}")
        # We can't see the password, but we can see if it's set.
    else:
        print(f"User {username} not found.")

print("--- Checking 911111111 ---")
check_user('911111111')
print("\n--- Checking admin6179 ---")
check_user('admin6179')
