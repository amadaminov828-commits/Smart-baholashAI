import sqlite3
import os

db_path = 'c:/Users/Asus/Desktop/antigravity/backend/db.sqlite3'
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Add column if not exists
        try:
            cursor.execute("ALTER TABLE vehicles_vehiclevaluation ADD COLUMN report_number VARCHAR(50)")
            print("Successfully added report_number column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("Column already exists")
            else:
                print(f"Error: {e}")
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Fatal error: {e}")
else:
    print("Database file not found at " + db_path)
