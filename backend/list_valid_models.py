import os
import requests
from dotenv import load_dotenv

load_dotenv('backend/.env')
api_key = os.getenv('GEMINI_API_KEY')

def list_models(version):
    print(f"--- Models for {version} ---")
    url = f"https://generativelanguage.googleapis.com/{version}/models?key={api_key}"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            for m in models:
                print(f"{m.get('name')} - {m.get('supportedGenerationMethods')}")
        else:
            print(f"Error {version}: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Failed {version}: {e}")

if __name__ == "__main__":
    list_models('v1')
    list_models('v1beta')
