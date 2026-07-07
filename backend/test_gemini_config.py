import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)

prompt = "Faqat 'OK' deb javob ber."
config = types.GenerateContentConfig(
    system_instruction="Sen yordamchisan.",
    response_mime_type="application/json",
)

model = "gemini-1.5-flash"
print(f"Testing model: {model} with system_instruction and JSON...")
try:
    res = client.models.generate_content(
        model=model, 
        contents=[prompt],
        config=config
    )
    print(f"  SUCCESS: {res.text}")
except Exception as e:
    print(f"  FAILED: {e}")
