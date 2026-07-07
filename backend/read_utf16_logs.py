import sys
import os

def read_log(path):
    print(f"--- Reading {path} ---")
    try:
        with open(path, 'r', encoding='utf-16-le') as f:
            lines = f.readlines()
            for line in lines[-50:]:  # Last 50 lines
                print(line.strip())
    except Exception as e:
        print(f"Error reading with utf-16-le: {e}")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines[-50:]:
                    print(line.strip())
        except Exception as e2:
            print(f"Also failed with utf-8: {e2}")

if __name__ == "__main__":
    read_log('c:/Users/Asus/Desktop/antigravity/backend/server_log.txt')
    read_log('c:/Users/Asus/Desktop/antigravity/backend/debug_server.log')
    read_log('c:/Users/Asus/Desktop/antigravity/backend/critical_error.log')
