import os
from google import genai
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)

print("Listing and testing models with Image...")
for m in client.models.list():
    if "flash" in m.name:
        id = m.name.replace("models/", "")
        print(f"Testing: {id}")
        try:
            img = Image.open(os.path.join("media", "photo_2026-02-13_09-45-25.jpg"))
            res = client.models.generate_content(model=id, contents=["Hi", img])
            print(f"  SUCCESS: {id} -> {res.text[:50]}...")
        except Exception as e:
            print(f"  FAILED: {id} -> {e}")
