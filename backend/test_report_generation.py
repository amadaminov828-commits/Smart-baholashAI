import requests
import json

def test_api():
    base_url = "http://127.0.0.1:8000/api/v1/vehicles/valuations/"
    
    print(f"Testing connectivity to: {base_url}")
    try:
        res = requests.get(base_url, timeout=10)
        print(f"Status Code: {res.status_code}")
        if res.status_code == 200:
            print("Successfully reached API List endpoint.")
        else:
            print(f"Failed with text: {res.text[:200]}")
    except Exception as e:
        print(f"Connectivity test failed: {e}")

    valuation_id = 1
    template_id = 77
    report_url = f"{base_url}{valuation_id}/generate-report/"
    
    payload = {
        "template_id": template_id
    }
    
    print(f"\nTesting report generation for Valuation ID: {valuation_id}, Template ID: {template_id}")
    try:
        response = requests.post(report_url, json=payload, timeout=60)
        print(f"Status Code: {response.status_code}")
        try:
            data = response.json()
            print("Response Data:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except:
            print("Response Text (Not JSON):")
            print(response.text[:500])
    except Exception as e:
        print(f"Report generation request failed: {e}")

if __name__ == "__main__":
    test_api()
