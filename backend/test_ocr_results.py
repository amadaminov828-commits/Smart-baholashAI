import os
import sys
import json
from vehicles.ocr import extract_vehicle_info

# Mocking log_ocr to print to stdout
import vehicles.ocr
def mock_log(msg): print(f"[LOG] {msg}")
vehicles.ocr.log_ocr = mock_log

test_file = 'c:/Users/Asus/Desktop/antigravity/backend/media/photo_2026-02-02_11-12-52.jpg'

print(f"Testing OCR on: {test_file}")
if not os.path.exists(test_file):
    print("File not found!")
    sys.exit(1)

result = extract_vehicle_info(test_file)
print("\n--- FINAL RESULT ---")
print(json.dumps(result, indent=4, ensure_ascii=False))
