import os
import sys

# Add backend to path
sys.path.append(os.getcwd())

from vehicles.ocr import extract_vehicle_info

img_path = os.path.join("media", "photo_2026-02-13_09-45-25.jpg")
print(f"Testing OCR with image: {img_path}")

if os.path.exists(img_path):
    data = extract_vehicle_info(img_path)
    print("FINAL DATA:")
    import json
    print(json.dumps(data, indent=2))
else:
    print(f"Image not found: {img_path}")
