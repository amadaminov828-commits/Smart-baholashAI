import os
import sys

def tail(filepath, lines=100):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            all_lines = f.readlines()
            print(''.join(all_lines[-lines:]))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    tail(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 100)
