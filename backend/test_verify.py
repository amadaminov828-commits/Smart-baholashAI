import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import RequestFactory
from reports.views import ReportViewSet
from vehicles.models import VehicleValuation

v = VehicleValuation.objects.filter(status='pending').order_by('-id').first()
if v:
    factory = RequestFactory()
    request = factory.get(f'/api/v1/reports/{v.id}/verify/')
    view = ReportViewSet.as_view({'get': 'verify'})
    
    try:
        response = view(request, pk=v.id)
        print(f"Status Code: {response.status_code}")
        print(f"Data: {response.data}")
    except Exception as e:
        print(f"Exception: {type(e).__name__} - {str(e)}")
else:
    print("No valuations found to test.")
