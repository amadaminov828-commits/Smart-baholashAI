import os
import sys
from PIL import Image
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.getcwd())

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key: {api_key[:10]}...")

from google import genai
from google.genai import types

client = genai.Client(api_key=api_key)

img_path = os.path.join("media", "photo_2026-02-13_09-45-25.jpg")
print(f"Loading image: {img_path}")
img = Image.open(img_path).convert('RGB')

prompt = "Analyze this image and return a JSON object with: {'is_vehicle_doc': true/false}. Return ONLY raw JSON."

print("Sending request using google-genai SDK...")
try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[img, prompt],
        config=types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json"
        )
    )
    print("SUCCESS!")
    print("Response text:")
    print(response.text)
except Exception as e:
    print("ERROR:", e)
