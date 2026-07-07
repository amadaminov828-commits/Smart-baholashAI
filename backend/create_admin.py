import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from users.models import User

# Check if admin already exists
if not User.objects.filter(role='admin').exists():
    admin = User.objects.create_superuser(
        username='998901234567',
        phone_number='+998901234567',
        password='adminpassword123',
        role='admin',
        full_name='Bosh Administrator'
    )
    print("Admin created: 998901234567 / adminpassword123")
else:
    admin = User.objects.filter(role='admin').first()
    # Let's reset the password to be safe so they can login
    admin.set_password('adminpassword123')
    admin.save()
    print(f"Admin found and password reset: {admin.username} / adminpassword123")
