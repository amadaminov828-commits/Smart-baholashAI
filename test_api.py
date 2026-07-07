import os
import requests
import json
from dotenv import load_dotenv

load_dotenv('backend/.env')
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env")
    exit(1)

# List models to see what's available
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
resp = requests.get(url)

if resp.status_code == 200:
    models = resp.json().get('models', [])
    print("Available Models:")
    for m in models:
        if 'generateContent' in m.get('supportedGenerationMethods', []):
            print(f" - {m['name']}")
else:
    print(f"Failed to list models ({resp.status_code}): {resp.text}")

# Test a simple prompt with gemini-1.5-flash
test_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
payload = {
    "contents": [{"parts": [{"text": "Say hello in one word."}]}]
}
test_resp = requests.post(test_url, json=payload)
if test_resp.status_code == 200:
    print("\ngemini-1.5-flash test: SUCCESS")
else:
    print(f"\ngemini-1.5-flash test: FAILED ({test_resp.status_code})")
