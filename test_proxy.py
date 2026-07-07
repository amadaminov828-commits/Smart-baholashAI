import requests

BASE_URL = "http://127.0.0.1:3000/api-proxy/v1/users/auth/login/"

def test_login(username, password):
    print(f"\nTesting proxy login for: {username}")
    try:
        res = requests.post(BASE_URL, json={"phone": username, "password": password})
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print("✅ MUVAFFARIYATLI! Token olindi.")
            print(f"Access Token (boshi): {res.json().get('access')[:20]}...")
        else:
            print(f"❌ XATO: {res.text}")
    except Exception as e:
        print(f"❌ XATO: {e}")

print("--- NEXT.JS PROXY ORQALI TEKSHIRISH ---")
test_login("911111111", "12345678")
