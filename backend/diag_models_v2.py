import google.generativeai as genai
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('c:/Users/Asus/Desktop/antigravity/backend/.env')
load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

try:
    models = genai.list_models()
    with open('c:/Users/Asus/Desktop/antigravity/backend/list_of_models.txt', 'w', encoding='utf-8') as f:
        for m in models:
            f.write(f"Name: {m.name}\n")
            f.write(f"Supported methods: {m.supported_generation_methods}\n\n")
    print("Models listed in list_of_models.txt")
except Exception as e:
    with open('c:/Users/Asus/Desktop/antigravity/backend/list_of_models.txt', 'w', encoding='utf-8') as f:
        f.write(f"Error: {str(e)}")
