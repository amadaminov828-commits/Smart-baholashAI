import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportDocument

def cleanup_135():
    print("Checking ReportDocuments for valuation 135...")
    reports = ReportDocument.objects.filter(object_id=135, object_type='vehicle').order_by('created_at')
    if not reports.exists():
        print("No reports found for 135.")
        return
        
    for r in reports:
        has_file = bool(r.file and r.file.name)
        exists = False
        if has_file:
            try:
                exists = os.path.exists(r.file.path)
            except: pass
            
        print(f"ID: {r.id}, Created: {r.created_at}, HasFile: {has_file}, ExistsOnDisk: {exists}")
        if not has_file or not exists:
            print(f"  -> Deleting broken/empty record {r.id}")
            r.delete()

cleanup_135()
cleanup_138() # Also check 138
def cleanup_138():
    reports = ReportDocument.objects.filter(object_id=138, object_type='vehicle').order_by('created_at')
    for r in reports:
        if not r.file or not os.path.exists(r.file.path):
            r.delete()
cleanup_138()
print("Cleanup done.")
