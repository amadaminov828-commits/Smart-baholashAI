import os
import django
import sys

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from users.models import User

def verify_user(username):
    print(f"\n--- Verifying: {username} ---")
    user = User.objects.filter(username__iexact=username).first()
    if not user:
        print(f"❌ User not found.")
        return

    print(f"✅ User found: {user.username}")
    print(f"   Active: {user.is_active}")
    print(f"   Role: {user.role}")
    print(f"   Visual Password (last_name): {user.last_name}")
    
    # Test passwords
    passwords_to_test = ['12345678', 'Abbusbek11']
    for p in passwords_to_test:
        if user.check_password(p):
            print(f"   🔓 Password '{p}' is CORRECT.")
        else:
            print(f"   🔒 Password '{p}' is INCORRECT.")

verify_user('911111111')
verify_user('admin6179')
