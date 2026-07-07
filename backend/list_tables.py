import sqlite3
import os

db_path = 'db.sqlite3'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in DB:")
    for t in tables:
        print(f"  - {t[0]}")
    
    # Check specifically for real_estate tables
    re_tables = [t[0] for t in tables if 'real_estate' in t[0]]
    print("\nReal Estate tables:")
    for t in re_tables:
        cursor.execute(f"PRAGMA table_info({t});")
        cols = cursor.fetchall()
        print(f"  Table {t}:")
        for c in cols:
            print(f"    - {c[1]} ({c[2]})")
    conn.close()
else:
    print("db.sqlite3 not found")
