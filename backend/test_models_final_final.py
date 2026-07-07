import os
from google import genai
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)

img_path = os.path.join("media", "photo_2026-02-13_09-45-25.jpg")

with open("multimodal_results_utf8.log", "w", encoding="utf-8") as f:
    f.write("Listing and testing models with Image...\n")
    try:
        models = client.models.list()
        for m in models:
            if "flash" in m.name or "pro" in m.name:
                id = m.name.replace("models/", "")
                f.write(f"Testing: {id}\n")
                try:
                    img = Image.open(img_path)
                    res = client.models.generate_content(model=id, contents=["Hi", img])
                    f.write(f"  SUCCESS: {id} -> {res.text[:50]}\n")
                except Exception as e:
                    f.write(f"  FAILED: {id} -> {str(e)[:100]}\n")
    except Exception as e:
        f.write(f"List models error: {e}\n")
    f.write("Done.\n")
