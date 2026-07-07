import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from django.db import connection
tables = connection.introspection.table_names()
print(f"Books table exists: {'books_book' in tables}")
print(f"All tables: {tables}")
