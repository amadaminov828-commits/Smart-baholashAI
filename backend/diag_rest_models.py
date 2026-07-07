import os
import requests
from dotenv import load_dotenv

load_dotenv('c:/Users/Asus/Desktop/antigravity/backend/.env')
api_key = os.getenv('GEMINI_API_KEY')

def list_models(version):
    output = f"--- Models for {version} ---\n"
    url = f"https://generativelanguage.googleapis.com/{version}/models?key={api_key}"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            for m in models:
                output += f"{m.get('name')} - {m.get('supportedGenerationMethods')}\n"
        else:
            output += f"Error {version}: {resp.status_code} - {resp.text}\n"
    except Exception as e:
        output += f"Failed {version}: {e}\n"
    return output

if __name__ == "__main__":
    res = list_models('v1')
    res += "\n" + list_models('v1beta')
    with open('c:/Users/Asus/Desktop/antigravity/backend/rest_models_list.txt', 'w', encoding='utf-8') as f:
        f.write(res)
    print("Done")
