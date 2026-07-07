import os

log_path = r'c:\Users\Asus\Desktop\antigravity\backend\debug_server.log'
if os.path.exists(log_path):
    with open(log_path, 'rb') as f:
        content = f.read()
    
    try:
        # Try UTF-16LE which was the error
        text = content.decode('utf-16le')
        print("--- DEBUG LOG (UTF-16LE) ---")
        print(text[-2000:]) # Last 2000 chars
    except Exception as e:
        print(f"Failed to decode as UTF-16LE: {e}")
        try:
            print("--- DEBUG LOG (UTF-8) ---")
            print(content.decode('utf-8', errors='ignore')[-2000:])
        except:
            print("Failed to decode at all")
else:
    print("File not found")
