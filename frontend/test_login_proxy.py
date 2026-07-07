import urllib.request
import json

url = "http://127.0.0.1:3000/api/v1/users/auth/login/"
data = json.dumps({"username": "admin", "password": "password"}).encode("utf-8")
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

try:
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print("Response:", response.read().decode())
except Exception as e:
    print("Error:", str(e))
