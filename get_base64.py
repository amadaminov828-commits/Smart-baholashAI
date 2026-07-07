import base64
import os

path = r"C:\Users\Asus\.gemini\antigravity\brain\4206e7e4-0164-4dfb-9ea6-e2617abc0b23\official_logo_from_url_1772320338796.png"

try:
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        # Print only the first and last few characters to avoid huge logs if I'm not careful, 
        # but I actually need the WHOLE string. 
        # Wait, I'll just write it to a .txt file so I can read it with view_file.
        with open(r"c:\Users\Asus\Desktop\antigravity\logo_base64.txt", "w") as out:
            out.write(encoded_string)
        print(f"Successfully wrote base64 to logo_base64.txt. Length: {len(encoded_string)}")
except Exception as e:
    print(f"Error: {e}")
