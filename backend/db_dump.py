import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportDocument, QRCode

print("DATABASE INTEGRITY CHECK:")
print("="*30)
reports = ReportDocument.objects.all().order_by('-created_at')[:10]
if not reports.exists():
    print("NO REPORTS FOUND IN DATABASE!")
else:
    for r in reports:
        qr = QRCode.objects.filter(report=r).first()
        print(f"Report ID (UUID): |{r.id}|")
        print(f"  Object: {r.object_id} ({r.object_type})")
        print(f"  Status: {r.status}")
        print(f"  File: {r.file.name if r.file else 'EMPTY'}")
        if qr:
            print(f"  QR Found: {qr.code_image.name}")
        else:
            print(f"  !! NO QR RECORD !!")
        print("-" * 20)

import socket
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

print(f"\nSERVER LOCAL IP: {get_local_ip()}")
