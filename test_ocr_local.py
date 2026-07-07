import os
import sys
import django
from pprint import pprint

# Setup Django environment
sys.path.append(os.path.abspath('backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from vehicles.ocr import extract_vehicle_info

def test_local():
    print("Starting direct OCR test...")
    # Get a file from media/ if possible, or just force the function to trigger API
    test_file = "C:/Users/Asus/Desktop/antigravity/Professional_shablon.docx" # Invalid file just to see if it even reaches API key check
    
    try:
        data = extract_vehicle_info(test_file)
        print("--- EXTRACTED DATA ---")
        pprint(data)
    except Exception as e:
        print(f"FAILED WITH EXCEPTION: {e}")

if __name__ == "__main__":
    test_local()
