import sqlite3
import os

db_path = 'c:/Users/Asus/Desktop/antigravity/backend/db.sqlite3'
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Try to add passport_birth_date
    try:
        cursor.execute("ALTER TABLE vehicles_vehiclevaluation ADD COLUMN passport_birth_date varchar(50) NULL;")
        print("Successfully added passport_birth_date column.")
    except Exception as e:
        print(f"Error or column already exists: {e}")

    conn.commit()
    conn.close()
except Exception as e:
    print(f"Connection error: {e}")
