import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.connect(('8.8.8.8', 80))
    IP = s.getsockname()[0]
except Exception as e:
    IP = f'127.0.0.1 (Error: {e})'
finally:
    s.close()
print("LOCAL IP IS:", IP)
