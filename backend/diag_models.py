import google.generativeai as genai
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('c:/Users/Asus/Desktop/antigravity/backend/.env')
load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("Listing available models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"Model: {m.name}")
