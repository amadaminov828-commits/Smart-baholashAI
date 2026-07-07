import codecs
import os

path = r'c:\Users\Asus\Desktop\antigravity\backend\debug_server.log'
if os.path.exists(path):
    with codecs.open(path, 'r', 'utf-16le', errors='replace') as f:
        content = f.read()
        lines = content.splitlines()
        # Get last 150 lines
        last_lines = lines[-150:]
        for line in last_lines:
            try:
                print(line)
            except:
                pass
else:
    print("File not found")
