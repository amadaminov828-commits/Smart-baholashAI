import os
import sys

# Add backend to path
sys.path.append(os.getcwd())

from vehicles.ocr import extract_vehicle_info, client
from google.genai import types

print(f"Client status: {client}")
if client:
    print("Gemini Client found, attempting a simple text generation...")
    try:
        res = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=["Soliq ruxsatnomasi tahlilini tekshiruv test. Faqat 'OK' deb javob ber."]
        )
        print(f"AI Connectivity Response: {res.text}")
    except Exception as e:
        print(f"AI Connectivity ERROR: {e}")

# If you have a test image in media, you can test it here
# For now, just test if it can parse empty input without crashing
print("Testing extract_vehicle_info with empty path (should return defaults):")
data = extract_vehicle_info("non_existent_file.jpg")
print(f"Extracted data: {data}")
