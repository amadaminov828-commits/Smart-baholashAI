import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)

# Put instructions in the main prompt
prompt = """Sen professional hujjat tahlilchisisan.
Quyidagi qoidalar asosida javob ber: Faqat 'OK' deb qaytar. Javobni JSON formatida qaytar: {"status": "OK"}"""

model = "gemini-1.5-flash"
print(f"Testing model: {model} with instructions in Prompt (No Config)...")
try:
    res = client.models.generate_content(
        model=model, 
        contents=[prompt]
    )
    print(f"  SUCCESS: {res.text}")
except Exception as e:
    print(f"  FAILED: {e}")
