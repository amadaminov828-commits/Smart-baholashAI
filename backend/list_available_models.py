import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
load_dotenv('backend/.env')
api_key = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)

print("Available models:")
try:
    for m in client.models.list():
        print(f"Name: {m.name}, Supported: {m.supported_actions}")
except Exception as e:
    print(f"Error listing models: {e}")
