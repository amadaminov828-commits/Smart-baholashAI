import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
load_dotenv('backend/.env')
api_key = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)

with open('models_list_v2.txt', 'w', encoding='utf-8') as f:
    f.write(f"Listing models with API key present: {bool(api_key)}\n")
    try:
        for model in client.models.list():
            f.write(f"Model: {model.name}, DisplayName: {model.display_name}\n")
    except Exception as e:
        f.write(f"Error: {e}\n")
print("Done listing models")
