import os
import requests
import json
from dotenv import load_dotenv

load_dotenv('backend/.env')
api_key = os.getenv('GEMINI_API_KEY')

def log_models(version):
    url = f"https://generativelanguage.googleapis.com/{version}/models?key={api_key}"
    try:
        resp = requests.get(url)
        data = resp.json()
        print(f"--- Models for {version} ---")
        if 'models' in data:
            for m in data['models']:
                print(f"ID: {m['name']}, Methods: {m.get('supportedGenerationMethods', [])}")
        else:
            print(f"No models found: {data}")
    except Exception as e:
        print(f"Error {version}: {e}")

if __name__ == "__main__":
    log_models('v1')
    log_models('v1beta')
