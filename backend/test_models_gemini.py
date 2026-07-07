import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)

models_to_test = ["gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro", "gemini-2.0-flash"]

for m in models_to_test:
    print(f"Testing model: {m} ...")
    try:
        res = client.models.generate_content(model=m, contents=["Hi"])
        print(f"  SUCCESS: {m}, Response: {res.text.strip()}")
    except Exception as e:
        print(f"  FAILED: {m}, Error: {e}")
