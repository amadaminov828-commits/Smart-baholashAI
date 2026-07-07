"""
This script lists all Gemini models available for this API key.
"""
import os
import requests
from dotenv import load_dotenv

# Load from absolute path
load_dotenv(r'c:\Users\Asus\Desktop\antigravity\backend\.env')
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("ERROR: GEMINI_API_KEY not found!")
    exit(1) 

api_key = api_key.strip('"\' ')
print(f"Using API Key: {api_key[:10]}...")
print("="*60)

for ver in ['v1', 'v1beta']:
    url = f"https://generativelanguage.googleapis.com/{ver}/models?key={api_key}"
    print(f"\n--- API Version: {ver} ---")
    try:
        r = requests.get(url)
        if r.status_code == 200:
            models = r.json().get('models', [])
            found = []
            for m in models:
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    found.append(m['name'])
            print(f"Models supporting generateContent ({len(found)}):")
            for name in found:
                print(f"  {name}")
        else:
            print(f"Error {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"Exception: {e}")

print("\n" + "="*60)
print("Copy the model names above and send to chat!")
