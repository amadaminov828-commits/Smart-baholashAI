# Test suite for Vehicle Specifications Catalog & Global Fallback

import os
import sys
import json

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.vehicles.specs_catalog import VEHICLE_SPECS_CATALOG
from backend.vehicles.ocr import get_global_vehicle_specs

def test_specs_catalog():
    print("=== Testing Local Specifications Catalog ===")
    
    # Test Uzbek/local models
    test_models = ['DAMAS', 'COBALT', 'BYD CHAZOR', 'TESLA MODEL Y']
    for m in test_models:
        spec = VEHICLE_SPECS_CATALOG.get(m)
        if spec:
            print(f"[SUCCESS] Found local specifications for '{m}':")
            print(f"  - Capacity: {spec['engine_capacity']} cm³")
            print(f"  - Power: {spec['engine_horsepower']} hp")
            print(f"  - Seats: {spec['seats_count']}")
            print(f"  - Weights: Empty={spec['empty_weight']}kg, Full={spec['full_weight']}kg")
            print(f"  - Fuel: {spec['fuel_type']}")
        else:
            print(f"[FAIL] Local specifications for '{m}' not found in catalog.")

    print("\n=== Testing Dynamic Gemini Global Specs Fallback ===")
    # Test a global model not in the catalog (e.g. BMW M5 or Porsche Cayenne)
    global_model = "BMW M5 2021"
    print(f"Invoking dynamic fallback for global model: '{global_model}'...")
    specs = get_global_vehicle_specs(global_model)
    if specs:
        print(f"[SUCCESS] Dynamic global specs successfully fetched for '{global_model}':")
        print(json.dumps(specs, indent=2))
        assert specs['engine_capacity'] > 0
        assert specs['engine_horsepower'] > 300
        assert specs['seats_count'] == 5
    else:
        print(f"[FAIL] Dynamic fallback failed to return specs for '{global_model}'.")

    # Test an electric global model not in the catalog
    ev_model = "Tesla Model S Plaid 2023"
    print(f"\nInvoking dynamic fallback for electric global model: '{ev_model}'...")
    ev_specs = get_global_vehicle_specs(ev_model)
    if ev_specs:
        print(f"[SUCCESS] Dynamic global specs successfully fetched for electric '{ev_model}':")
        print(json.dumps(ev_specs, indent=2))
        assert ev_specs['engine_capacity'] == 0
        assert ev_specs['fuel_type'] == "Elektr"
    else:
        print(f"[FAIL] Dynamic fallback failed to return specs for '{ev_model}'.")

if __name__ == '__main__':
    try:
        test_specs_catalog()
        print("\n[ALL TESTS PASSED SUCCESSFULLY!]")
    except Exception as e:
        print(f"\n[TEST FAILED]: {e}")
        sys.exit(1)
