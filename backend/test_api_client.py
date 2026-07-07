import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from django.test import Client
from vehicles.models import VehicleValuation
from reports.models import ReportDocument

# Get latest pending report id to test
val = VehicleValuation.objects.filter(status='pending').order_by('-id').first()
if getattr(val, 'id', None):
    # Try fetching the ID that the QR code is trying to use
    test_id = val.id
else:
    test_id = 195 # fallback

print(f"Testing /api/v1/reports/{test_id}/verify/")

c = Client()
response = c.get(f'/api/v1/reports/{test_id}/verify/')
print("Status Code:", response.status_code)

try:
    print("Response JSON:", response.json())
except Exception as e:
    print("Response Content:", response.content.decode('utf-8'))
