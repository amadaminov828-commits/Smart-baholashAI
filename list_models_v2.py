import os
import requests
from dotenv import load_dotenv

load_dotenv('backend/.env')
api_key = os.getenv('GEMINI_API_KEY')
if api_key: api_key = api_key.strip('"\' ')

print(f"Using API Key: {api_key[:10]}...")

for ver in ['v1', 'v1beta']:
    url = f"https://generativelanguage.googleapis.com/{ver}/models?key={api_key}"
    print(f"\nChecking version: {ver}")
    try:
        r = requests.get(url)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            models = r.json().get('models', [])
            for m in models:
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    print(f" - {m['name']}")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Exception: {e}")
