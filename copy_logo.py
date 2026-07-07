import shutil
import os

# New source path from browser subagent result
src = r"C:\Users\Asus\.gemini\antigravity\brain\4206e7e4-0164-4dfb-9ea6-e2617abc0b23\official_logo_from_url_1772320338796.png"
dst = r"c:\Users\Asus\Desktop\antigravity\frontend\public\logo.png"

try:
    if os.path.exists(src):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print(f"Successfully copied {src} to {dst}")
    else:
        print(f"Source file not found: {src}")
except Exception as e:
    print(f"Error copying file: {e}")
