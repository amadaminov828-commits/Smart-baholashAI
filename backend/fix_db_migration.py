import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from django.db import connection

def fix_db():
    queries = [
        "ALTER TABLE real_estate_realestatevaluation ADD COLUMN confirmed_fields TEXT DEFAULT '{}'",
        "ALTER TABLE real_estate_realestatevaluation ADD COLUMN calculation_data TEXT DEFAULT '{}'",
        "ALTER TABLE real_estate_realestatevaluation ADD COLUMN status VARCHAR(20) DEFAULT 'draft'",
    ]
    
    with connection.cursor() as cursor:
        # Check current columns first to avoid "duplicate column" errors
        cursor.execute("PRAGMA table_info(real_estate_realestatevaluation)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        for q in queries:
            col_name = q.split('ADD COLUMN ')[1].split(' ')[0]
            if col_name not in existing_columns:
                try:
                    print(f"Executing: {q}")
                    cursor.execute(q)
                    print(f"  -> SUCCESS")
                except Exception as e:
                    print(f"  -> ERROR: {e}")
            else:
                print(f"Column '{col_name}' already exists.")

if __name__ == "__main__":
    fix_db()
