import time
import os

LOG_FILES = [
    'c:/Users/Asus/Desktop/antigravity/backend/server_log.txt',
    'c:/Users/Asus/Desktop/antigravity/backend/debug_server.log',
    'c:/Users/Asus/Desktop/antigravity/backend/critical_error.log'
]

def check_for_hits():
    print("Searching for 'DEBUG: ocr_upload hit!' or '2026-03-02'...")
    for log_path in LOG_FILES:
        if not os.path.exists(log_path):
            continue
        print(f"\n--- Checking {log_path} ---")
        try:
            # Try various encodings
            found = False
            for enc in ['utf-16-le', 'utf-8', 'cp1251']:
                try:
                    with open(log_path, 'r', encoding=enc) as f:
                        content = f.read()
                        if "ocr_upload hit" in content.lower() or "2026-03-02" in content:
                            print(f"FOUND MATCH in {log_path} ({enc})")
                            lines = content.splitlines()
                            for line in lines[-20:]:
                                print(line)
                            found = True
                            break
                except:
                    continue
            if not found:
                print("No matches found in this file.")
        except Exception as e:
            print(f"Error checking {log_path}: {e}")

if __name__ == "__main__":
    check_for_hits()
