import urllib.request
import json
import uuid

# Fetch the last created report from DB directly
import os
import sqlite3

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'db.sqlite3')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute("SELECT id, object_id, created_at FROM reports_reportdocument ORDER BY created_at DESC LIMIT 1")
row = c.fetchone()
conn.close()

if row:
    # the UUID is stored as bytes object in sqlite usually for Django UUIDField without hyphens
    # Let's just try to hit the endpoint via HTTP
    try:
        report_id_str = str(uuid.UUID(bytes=row['id']))
    except ValueError:
        report_id_str = row['id'].hex() if isinstance(row['id'], bytes) else row['id']
    
    print(f"Latest Report ID in DB: {report_id_str}")
    
    url = f"http://127.0.0.1:8000/api/v1/reports/{report_id_str}/verify/"
    print(f"Testing URL: {url}")
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print("Response:", json.dumps(data, indent=2))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No reports found in DB")
