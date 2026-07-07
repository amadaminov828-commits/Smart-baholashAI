import os
import pkg_resources
from google import genai
from dotenv import load_dotenv

load_dotenv()
load_dotenv('backend/.env')
api_key = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)

with open('c:/Users/Asus/Desktop/antigravity/backend/diag_models_clean.txt', 'w', encoding='utf-8') as f:
    f.write("Installed Packages:\n")
    try:
        packages = [pkg.key + '==' + pkg.version for pkg in pkg_resources.working_set if 'google' in pkg.key.lower()]
        for p in packages: f.write(f"{p}\n")
    except Exception as e:
        f.write(f"Err packages: {e}\n")
    
    f.write("\nAvailable Models for generateContent:\n")
    try:
        for m in client.models.list():
            if 'generateContent' in m.supported_actions:
                f.write(f"- {m.name}\n")
    except Exception as e:
        f.write(f"Err models: {e}\n")
