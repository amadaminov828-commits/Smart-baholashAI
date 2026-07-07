import urllib.request
import json

url = "http://localhost:3000/django-api/v1/users/auth/login/"
data = json.dumps({"username": "911111111", "password": "password"}).encode("utf-8")
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

try:
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print("Response:", response.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Response:", e.read().decode("utf-8"))
except Exception as e:
    print("Error:", e)
