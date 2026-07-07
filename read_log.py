import os

log_path = 'backend/server.log'
if not os.path.exists(log_path):
    log_path = 'backend/server_output.log'

def read_log_robust(path):
    try:
        with open(path, 'rb') as f:
            raw = f.read()
        
        # Try UTF-16LE first as it seems to be the primary encoding
        try:
            content = raw.decode('utf-16le')
        except:
            content = raw.decode('utf-8', errors='replace')
            
        # Clean up null bytes and fragments
        lines = content.splitlines()
        clean_lines = []
        for line in lines:
            line = line.replace('\x00', '').strip()
            if line:
                clean_lines.append(line)
        return clean_lines
    except Exception as e:
        return [f"Error reading: {e}"]

if os.path.exists(log_path):
    print(f"--- READING {log_path} (Last 200 clean lines) ---")
    all_lines = read_log_robust(log_path)
    for line in all_lines[-200:]:
        print(line)
else:
    print("Log file not found.")
