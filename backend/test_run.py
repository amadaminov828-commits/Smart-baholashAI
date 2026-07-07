import requests
import json

base_url = 'http://127.0.0.1:8000/api/v1/vehicles'

def test():
    # 1. Create a dummy valuation
    print("Creating valuation...")
    res = requests.post(f"{base_url}/valuations/", json={
        "method": "qiyosiy",
        "car_model": "Lacetti",
        "year": 2020,
        "engine_capacity": "1500",
        "owner_name": "Test Pasport Egasi",
        "tech_passport_owner": "Test Tech Pasport Egasi",
        "valuation_date": "2025-01-01"
    })
    
    if res.status_code != 201:
        print("Failed to create:", res.text)
        return
        
    vid = res.json()['id']
    print("Created ID:", vid)
    
    # 2. Get Report
    print("Generating report...")
    # NOTE: Assuming a default template will be created or used
    res_repo = requests.post(f"{base_url}/valuations/{vid}/generate-report/")
    print(res_repo.status_code)
    try:
        print(res_repo.json())
    except:
        print(res_repo.text)

if __name__ == "__main__":
    test()
