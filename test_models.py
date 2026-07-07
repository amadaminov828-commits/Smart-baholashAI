import os
from dotenv import load_dotenv
from google import genai

load_dotenv('backend/.env')
api_key = os.getenv('GEMINI_API_KEY') or os.getenv('OPENAI_API_KEY')

client = genai.Client(api_key=api_key)

print("Listing supported models:")
try:
    models = client.models.list()
    for m in models:
        print(m.name)
except Exception as e:
    print(f"Failed to list: {e}")
