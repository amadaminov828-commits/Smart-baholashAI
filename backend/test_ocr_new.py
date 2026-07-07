from vehicles.ocr import extract_vehicle_info
import os

def test_ocr():
    # Test with a dummy path or a real image if exists
    # For now, just see if it fails on initialization or call
    print("Testing OCR...")
    data = extract_vehicle_info("non_existent.jpg")
    print(f"Data: {data}")

if __name__ == "__main__":
    test_ocr()
