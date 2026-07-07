import os

with open('c:/Users/Asus/Desktop/antigravity/backend/server_log.txt', 'r', encoding='utf-16') as f:
    lines = f.readlines()

with open('c:/Users/Asus/Desktop/antigravity/backend/server_log_utf8.txt', 'w', encoding='utf-8') as f:
    f.writelines(lines[-100:])
