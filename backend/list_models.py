import os
import requests
from dotenv import load_dotenv

load_dotenv()
load_dotenv('backend/.env')
api_key = os.getenv('GEMINI_API_KEY')

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
try:
    r = requests.get(url)
    print(f"Status Code: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")
