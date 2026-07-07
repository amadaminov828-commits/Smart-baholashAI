import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
load_dotenv('backend/.env')

api_key = os.getenv('GEMINI_API_KEY') or os.getenv('OPENAI_API_KEY')
print(f"Testing with key: {api_key[:10]}...")

try:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say 'Hello connectivity test success'"
    )
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Connectivity Error: {e}")
