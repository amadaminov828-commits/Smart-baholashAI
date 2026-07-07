import os
import sys
import django
from PIL import Image

sys.path.append(os.path.abspath('backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from vehicles.ocr import extract_vehicle_info

def test_ai():
    print("Testing AI parsing with dummy image...")
    # Create dummy image
    img = Image.new('RGB', (100, 100), color='red')
    img.save('dummy.jpg')
    
    try:
        data = extract_vehicle_info('dummy.jpg')
        print("--- RESULT ---")
        for k, v in data.items():
            if str(v) != "Noma'lum":
                print(f"{k}: {v}")
    except Exception as e:
        import traceback
        print("--- EXCEPTION ---")
        print(traceback.format_exc())
    finally:
        if os.path.exists('dummy.jpg'):
            os.remove('dummy.jpg')

if __name__ == "__main__":
    test_ai()
