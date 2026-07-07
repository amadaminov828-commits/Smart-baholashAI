import os
import django

# Correct settings module based on the project structure
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from users.models import User

def create_user(username, password, full_name, role):
    user, created = User.objects.get_or_create(username=username)
    user.set_password(password)
    user.full_name = full_name
    user.role = role
    user.is_staff = True if role in ['super_admin', 'admin'] else False
    user.is_superuser = True if role == 'super_admin' else False
    # Storing password in last_name for admin visibility as requested before
    user.last_name = password 
    user.save()
    if created:
        print(f"Created {role}: {username}")
    else:
        print(f"Updated {role}: {username}")

if __name__ == "__main__":
    # Create Super Admin with new credentials
    create_user('azzam610', '2013nnnn', 'Asosiy Admin (Azzam)', 'super_admin')
    
    # Create Assistant Admin with new credentials
    create_user('smartbaholash', 'smartbaholashai', 'Smart Baholash Admin', 'admin')

    print("\nUsers created/updated successfully with the new credentials!")
