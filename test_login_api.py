import requests

url = "http://127.0.0.1:8000/api/v1/users/auth/login/"
payload = {
    "username": "331111111",
    "password": "2013nnnn"
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error connecting: {e}")
