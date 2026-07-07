import subprocess
import os
import time

backend_dir = r"c:\Users\Asus\Desktop\antigravity\backend"
python_exe = os.path.join(backend_dir, "venv", "Scripts", "python.exe")
manage_py = os.path.join(backend_dir, "manage.py")

print(f"Starting server from {backend_dir}...")
try:
    # Use Popen to start in background. We don't wait for it.
    proc = subprocess.Popen([python_exe, manage_py, "runserver", "0.0.0.0:8000"],
                            cwd=backend_dir,
                            stdout=open('server_stdout.log', 'w'),
                            stderr=open('server_stderr.log', 'w'))
    print(f"Process PID: {proc.pid}")
    time.sleep(2) # Give it a moment to bind to port
    if proc.poll() is None:
        print("Server process appears to be running in background.")
    else:
        print(f"Server process exited immediately with code {proc.returncode}")
except Exception as e:
    print(f"Error starting server: {e}")
