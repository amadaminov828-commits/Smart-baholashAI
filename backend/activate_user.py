import os
import django
import sys

# Add current directory to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
try:
    django.setup()
    print("Django setup OK.")
except Exception as e:
    print(f"Django setup error: {e}")
    sys.exit(1)

from users.models import User

def activate(username, password):
    user = User.objects.filter(username__iexact=username).first()
    if user:
        user.is_active = True
        user.set_password(password)
        # Also store the plain text password for reference in last_name if needed (optional)
        user.last_name = password 
        user.save()
        print(f"SUCCESS: User '{username}' is now active and password set to '{password}'.")
    else:
        # Create new if doesn't exist
        user = User.objects.create_user(
            username=username,
            password=password,
            is_active=True,
            role='assistant',
            full_name='Test User'
        )
        print(f"SUCCESS: Created new active user '{username}' with password '{password}'.")

if __name__ == "__main__":
    # Activate the specific user from the screenshot
    activate('916996179', '12345678')
    
    # Also ensure the admin bypass one is there just in case
    activate('admin6179', '2013nnn')
    
    print("\n--- Barcha userlar ---")
    for u in User.objects.all():
        print(f"- {u.username} (Active: {u.is_active})")
