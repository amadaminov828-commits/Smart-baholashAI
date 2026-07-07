import sqlite3
import os

db_path = 'backend/db.sqlite3'
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
    exit()

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("--- USERS ---")
c.execute("SELECT id, username, role FROM users_user")
users = {row['id']: dict(row) for row in c.fetchall()}
for uid, u in users.items():
    print(f"ID: {uid}, User: {u['username']}, Role: {u['role']}")

print("\n--- VEHICLE VALUATIONS ---")
c.execute("SELECT id, car_model, plate_number, status, user_id, assigned_to_id FROM vehicles_vehiclevaluation")
for row in c.fetchall():
    user = users.get(row['user_id'], {}).get('username', 'Unknown')
    assigned = users.get(row['assigned_to_id'], {}).get('username', 'None')
    print(f"ID: {row['id']}, Model: {row['car_model']}, Status: {row['status']}, Creator: {user}, Assigned: {assigned}")

print("\n--- REPORT DOCUMENTS ---")
c.execute("SELECT id, object_id, object_type, status, user_id, assigned_to_id FROM reports_reportdocument")
for row in c.fetchall():
    user = users.get(row['user_id'], {}).get('username', 'Unknown')
    assigned = users.get(row['assigned_to_id'], {}).get('username', 'None')
    print(f"ID: {row['id']}, ObjID: {row['object_id']}, Type: {row['object_type']}, Status: {row['status']}, Owner: {user}, Appraiser: {assigned}")

conn.close()
