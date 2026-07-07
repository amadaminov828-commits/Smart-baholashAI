import os
from google import genai
from dotenv import load_dotenv

load_dotenv('backend/.env')
api_key = os.getenv('GEMINI_API_KEY')

def list_sdk_models():
    client = genai.Client(api_key=api_key)
    print("--- Available SDK Models ---")
    try:
        for model in client.models.list():
            print(f"Name: {model.name}, Display: {model.display_name}, Methods: {model.supported_generation_methods}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_sdk_models()
