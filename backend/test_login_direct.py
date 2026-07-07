import requests

BASE_URL = "http://127.0.0.1:8000/api/v1/users/auth/login/"

def test_login(username, password):
    print(f"\nTesting login for: {username}")
    try:
        res = requests.post(BASE_URL, json={"username": username, "password": password})
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print("✅ MUVAFFARIYATLI! Token olindi.")
            print(f"Access Token (boshi): {res.json().get('access')[:20]}...")
        else:
            print(f"❌ XATO: {res.text}")
    except Exception as e:
        print(f"❌ XATO: {e}")

print("--- BACKENDNI TO'G'RIDAN-TO'G'RI TEKSHIRISH ---")
test_login("admin6179", "2013nnn")
test_login("911111111", "12345678")
