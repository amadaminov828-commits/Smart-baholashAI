import os
from google import genai
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)

img_path = os.path.join("media", "photo_2026-02-13_09-45-25.jpg")
model = "gemini-2.0-flash-exp"

print(f"Testing model: {model} with image...")
try:
    img = Image.open(img_path)
    res = client.models.generate_content(
        model=model, 
        contents=["Hujjatda nimalarni ko'ryapsan?", img]
    )
    print(f"  SUCCESS: {res.text[:200]}")
except Exception as e:
    print(f"  FAILED: {e}")
