import os
import django
import sys

# Bootstrap Django
sys.path.append(r"c:\Users\Asus\Desktop\antigravity\backend")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "valuation_platform.settings")
django.setup()

from vehicles.models import VehicleValuation, VehicleAnalog
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from vehicles.views import VehicleValuationViewSet

def test_caching():
    print("=== Starting Pricing Caching and Stability Test ===")
    
    User = get_user_model()
    # Find or create a test user
    user = User.objects.filter(role="appraiser").first() or User.objects.first()
    if not user:
        print("No user found in database. Creating a test appraiser...")
        user = User.objects.create_user(
            username="test_stability_user",
            password="testpassword123",
            role="appraiser"
        )
        
    print(f"Using test user: {user.username} (Role: {user.role})")
    
    # 1. Clean existing test valuations to prevent pollution
    VehicleValuation.objects.filter(car_model="Test Stable Sedan").delete()
    
    # 2. Create the first valuation (which will act as the cache source)
    v1 = VehicleValuation.objects.create(
        user=user,
        car_model="Test Stable Sedan",
        year=2020,
        plate_number="01A777AA",
        mileage="50000",
        price_amount=100000.00
    )
    print(f"Created primary valuation V1 (ID: {v1.id})")
    
    # Add 3 mock analogs to V1 (as if they were successfully scraped or saved)
    analogs_to_create = [
        {
            "source": "OLX Mock", "model_name": "Test Stable Sedan", "year": 2020,
            "engine_capacity": "1.5", "mileage": "45000 km", "price": 11500.00,
            "price_string": "11 500 y.e.", "location": "Toshkent", "url": "https://olx.uz/1"
        },
        {
            "source": "Avtoelon Mock", "model_name": "Test Stable Sedan", "year": 2020,
            "engine_capacity": "1.5", "mileage": "52000 km", "price": 11200.00,
            "price_string": "11 200 y.e.", "location": "Farg'ona", "url": "https://avtoelon.uz/2"
        },
        {
            "source": "OLX Mock 2", "model_name": "Test Stable Sedan", "year": 2020,
            "engine_capacity": "1.5", "mileage": "48000 km", "price": 11800.00,
            "price_string": "11 800 y.e.", "location": "Samarqand", "url": "https://olx.uz/3"
        }
    ]
    
    for analog_data in analogs_to_create:
        VehicleAnalog.objects.create(valuation=v1, **analog_data)
        
    print(f"Successfully populated 3 mock analogs for V1.")
    
    # 3. Create the second valuation for the exact same vehicle details (model and year)
    v2 = VehicleValuation.objects.create(
        user=user,
        car_model="Test Stable Sedan",
        year=2020,
        plate_number="40B999BB",
        mileage="50000",
        price_amount=100000.00
    )
    print(f"Created secondary valuation V2 (ID: {v2.id})")
    
    # 4. Trigger the find-analogs action via API request on V2
    factory = APIRequestFactory()
    view = VehicleValuationViewSet.as_view({'post': 'find_analogs'})
    
    request = factory.post(f"/api/vehicles/{v2.id}/find-analogs/", {"method": "qiyosiy"}, format="json")
    force_authenticate(request, user=user)
    
    print("Calling find_analogs endpoint for V2...")
    response = view(request, pk=v2.id)
    
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.data}")
    
    # Verify that V2 successfully hit the cache and copied the identical analogs
    v2.refresh_from_db()
    v2_analogs = list(v2.analogs.all())
    
    print(f"Number of analogs copied to V2: {len(v2_analogs)}")
    
    assert len(v2_analogs) == 3, f"Expected 3 analogs, got {len(v2_analogs)}"
    assert response.data.get("cached") is True, "Expected response to indicate cache hit"
    assert response.data.get("cached_from_id") == v1.id, f"Expected cache source ID {v1.id}, got {response.data.get('cached_from_id')}"
    
    # Verify the copied analog details are identical to the originals
    v1_analogs = list(v1.analogs.all())
    for i in range(3):
        assert v2_analogs[i].price == v1_analogs[i].price, f"Price mismatch at index {i}: {v2_analogs[i].price} vs {v1_analogs[i].price}"
        assert v2_analogs[i].url == v1_analogs[i].url, f"URL mismatch at index {i}"
        assert v2_analogs[i].source == v1_analogs[i].source, f"Source mismatch at index {i}"
        print(f"Analog {i+1} verified identical: {v2_analogs[i].price_string} ({v2_analogs[i].source})")
        
    print("\n=== Pricing Caching and Stability Test PASSED successfully! ===")
    
    # Cleanup test records
    VehicleValuation.objects.filter(car_model="Test Stable Sedan").delete()
    print("Test records cleaned up successfully.")

if __name__ == "__main__":
    test_caching()
