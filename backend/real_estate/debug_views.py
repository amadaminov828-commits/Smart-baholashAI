from django.http import HttpResponse
from django.db import connection

def raw_sql_fix(request):
    queries = [
        "ALTER TABLE real_estate_realestatevaluation ADD COLUMN confirmed_fields TEXT DEFAULT '{}'",
        "ALTER TABLE real_estate_realestatevaluation ADD COLUMN calculation_data TEXT DEFAULT '{}'",
        "ALTER TABLE real_estate_realestatevaluation ADD COLUMN status VARCHAR(20) DEFAULT 'draft'",
    ]
    results = []
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            all_tables = [row[0] for row in cursor.fetchall()]
            
            target = "real_estate_realestatevaluation"
            if target not in all_tables:
                return HttpResponse(f"ERROR: Table {target} not found among {all_tables}")

            cursor.execute(f"PRAGMA table_info({target})")
            cols = [row[1] for row in cursor.fetchall()]
            
            # Re-implementing correctly
            for q in queries:
                col = q.split('ADD COLUMN ')[1].split(' ')[0]
                if col not in cols:
                    try:
                        cursor.execute(q)
                        results.append(f"ADDED: {col}")
                    except Exception as e:
                        results.append(f"ERROR {col}: {str(e)}")
                else:
                    results.append(f"EXISTS: {col}")
    except Exception as e:
        return HttpResponse(f"CRITICAL ERROR: {str(e)}")

    return HttpResponse(f"RESULTS: {', '.join(results)}")
