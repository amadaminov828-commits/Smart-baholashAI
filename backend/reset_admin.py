import os
import sys
import django

sys.path.append(r'C:\Users\Asus\Desktop\antigravity\backend')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from users.models import User

try:
    u = User.objects.get(username='admin6179')
    u.set_password('2013nnn')
    u.is_active = True
    u.save()
    print("Password reset successful")
except Exception as e:
    print(f"Error: {e}")
