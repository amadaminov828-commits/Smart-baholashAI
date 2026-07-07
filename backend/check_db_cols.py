import sqlite3
import os

db_path = 'c:/Users/Asus/Desktop/antigravity/backend/db.sqlite3'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(vehicles_vehiclevaluation)")
    cols = cursor.fetchall()
    for col in cols:
        print(col)
    conn.close()
else:
    print("DB not found")
