import os
import requests

file_path = 'C:\\Users\\Asus\\Desktop\\antigravity\\backend\\manage.py' # Just sending any file to see the first error it hits
files = {'documents': open(file_path, 'rb')}
try:
    res = requests.post('http://127.0.0.1:8000/api/v1/vehicles/valuations/ocr-upload/', files=files)
    print("STATUS", res.status_code)
    print("RESPONSE", res.text)
except Exception as e:
    print(e)
