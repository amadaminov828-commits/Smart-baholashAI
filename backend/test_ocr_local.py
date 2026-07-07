import os
import sys
import django
sys.path.append(os.path.abspath('c:/Users/Asus/Desktop/antigravity/backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from vehicles.ocr import extract_vehicle_info
# Find all recent images in the media directory to test against
base_dir = r"C:\Users\Asus\Desktop\antigravity\backend\media"
files = [f for f in os.listdir(base_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

if not files:
    print("No images found in media.")
else:
    test_file = os.path.join(base_dir, files[-1])
    print("Testing with file:", test_file)
    data = extract_vehicle_info(test_file)
    import json
    print(json.dumps(data, indent=2))
