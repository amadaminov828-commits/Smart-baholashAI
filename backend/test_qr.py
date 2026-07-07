import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from vehicles.models import VehicleValuation
from vehicles.serializers import VehicleValuationSerializer

v = VehicleValuation.objects.filter(status='pending').first()
if v:
    s = VehicleValuationSerializer(v)
    print("QR_URL for Valuation", v.id, ":", s.data.get('qr_url'))
else:
    print("No pending valuations found.")
