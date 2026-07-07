import requests
import json

# Log in first to get auth token or session
login_url = "http://127.0.0.1:8000/api/v1/users/auth/login/"
report_url = "http://127.0.0.1:8000/api/v1/vehicles/valuations/155/generate-report/" # Usually the latest ID, let's try the last one

# Need to find latest valuation ID first
try:
    import sys
    import os
    sys.path.append(r'C:\Users\Asus\Desktop\antigravity\backend')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "valuation_platform.settings")
    import django
    django.setup()
    from vehicles.models import VehicleValuation
    latest_id = VehicleValuation.objects.latest('id').id
    print(f"Latest Valuation ID: {latest_id}")
    report_url = f"http://127.0.0.1:8000/api/v1/vehicles/valuations/{latest_id}/generate-report/"

    from users.models import User
    valuation_obj = VehicleValuation.objects.get(id=latest_id)
    admin_user = valuation_obj.user or User.objects.filter(role='admin').first() or User.objects.first()
    if not admin_user:
        raise Exception("No users found in DB")
    print(f"Using User: {admin_user.username} (Role: {getattr(admin_user, 'role', 'None')})")
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(admin_user)
    token = str(refresh.access_token)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    print(f"Calling: {report_url}")
    response = requests.post(report_url, headers=headers, json={"template_id": 233})
    print(f"Status: {response.status_code}")
    print(response.text)

except Exception as e:
    print(f"Script error: {e}")
