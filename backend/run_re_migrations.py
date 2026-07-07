import os
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

try:
    print("Running makemigrations for real_estate...")
    call_command('makemigrations', 'real_estate')
    print("Running migrate for real_estate...")
    call_command('migrate', 'real_estate')
    print("Migrations completed successfully!")
except Exception as e:
    print(f"Error during migrations: {e}")
