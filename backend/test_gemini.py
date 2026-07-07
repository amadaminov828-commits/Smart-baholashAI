import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY') or os.getenv('OPENAI_API_KEY')
print(f"Key loaded: {api_key[:10]}...")

try:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Test message, reply with OK'
    )
    print("Response:", response.text)
except Exception as e:
    print("ERROR:", e)
