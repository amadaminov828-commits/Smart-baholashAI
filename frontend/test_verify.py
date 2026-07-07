import urllib.request
import json

url = "http://127.0.0.1:8000/api/v1/reports/195/verify/"
req = urllib.request.Request(url)

try:
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print("Response:", response.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Error Body:", e.read().decode())
except Exception as e:
    print("Error:", str(e))
