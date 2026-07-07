import sqlite3
import os

db_path = 'c:/Users/Asus/Desktop/antigravity/backend/db.sqlite3'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(real_estate_realestatevaluation)")
        cols = cursor.fetchall()
        print("Columns in real_estate_realestatevaluation:")
        for col in cols:
            print(f"  {col[1]} ({col[2]})")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
else:
    print("DB not found")
