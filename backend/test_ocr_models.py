import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
load_dotenv('backend/.env')
api_key = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)

models_to_test = [
    'gemini-1.5-flash',
    'gemini-1.5-flash-8b',
    'gemini-1.5-pro',
    'gemini-2.0-flash-exp'
]

with open('ocr_test_results.txt', 'w', encoding='utf-8') as f:
    f.write(f"Testing models with API Key: {bool(api_key)}\n")
    for model_id in models_to_test:
        f.write(f"\n--- Testing {model_id} ---\n")
        try:
            response = client.models.generate_content(
                model=model_id,
                contents="Hi, respond with exactly 'OK' to test connectivity."
            )
            f.write(f"SUCCESS: {response.text}\n")
        except Exception as e:
            f.write(f"FAILED: {str(e)}\n")
print("Done testing models")
