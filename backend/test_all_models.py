import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)

print("Listing and testing every model ...")
for model in client.models.list():
    name = model.name
    id = name.replace("models/", "")
    print(f"Testing: {id} (Full Name: {name})")
    try:
        res = client.models.generate_content(model=id, contents=["Hi"])
        print(f"  SUCCESS: {id} -> {res.text.strip()}")
    except Exception as e:
        print(f"  FAILED: {id} -> {e}")
