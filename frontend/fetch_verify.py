import urllib.request
import json
import traceback

def test():
    try:
        url = "http://127.0.0.1:8000/api/v1/reports/b329987e-e932-4581-81e5-2b76ab4085d8/verify/"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            print("Status:", response.status)
            print("Response:", response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print("HTTP Error:", e.code)
        print("Response body:", e.read().decode('utf-8'))
    except Exception as e:
        print("Other Error:", str(e))

if __name__ == '__main__':
    test()
