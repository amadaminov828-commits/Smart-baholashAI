import os
import django
import sys

sys.path.append(r"c:\Users\Asus\Desktop\antigravity\backend")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "valuation_platform.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

target_user = User.objects.filter(username="331111111").first()
if target_user:
    target_user.set_password("12345678")
    target_user.save()
    print("Password reset successfully for 331111111 to 12345678")
else:
    print("User 331111111 not found")
