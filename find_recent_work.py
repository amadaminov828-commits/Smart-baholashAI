import os
import time

def find_recent_files(root_dir, limit=30):
    files_with_time = []
    exclude_dirs = {'.git', '.next', 'node_modules', 'venv', '__pycache__', '.system_generated', '.vscode'}
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Modifying dirnames in-place to skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        
        for f in filenames:
            fullpath = os.path.join(dirpath, f)
            try:
                mtime = os.path.getmtime(fullpath)
                files_with_time.append((fullpath, mtime))
            except Exception:
                pass
                
    # Sort by mtime descending
    files_with_time.sort(key=lambda x: x[1], reverse=True)
    
    print("Most recently modified files:")
    for path, mtime in files_with_time[:limit]:
        mtime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
        print(f"{mtime_str} - {os.path.relpath(path, root_dir)}")

if __name__ == '__main__':
    find_recent_files(r'c:\Users\Asus\Desktop\antigravity')
