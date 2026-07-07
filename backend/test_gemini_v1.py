import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
# Note the 'v1' instead of 'v1beta'
url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"

payload = {
    "contents": [{
        "parts": [{"text": "Hi. Faqat 'OK' deb javob ber."}]
    }]
}
headers = {"Content-Type": "application/json"}

print(f"Sending raw HTTP request to: {url.split('?')[0]}...")
try:
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"HTTP ERROR: {e}")
