import os
import django
import socket

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportDocument, QRCode

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

log_file = 'diag_results.txt'

with open(log_file, 'w', encoding='utf-8') as f:
    f.write(f"Diagnostic Run: {get_local_ip()}\n")
    f.write("="*30 + "\n")
    
    reports = ReportDocument.objects.all().order_by('-created_at')[:10]
    f.write(f"Last 10 Reports:\n")
    for r in reports:
        qr = QRCode.objects.filter(report=r).first()
        f.write(f"ID: {r.id}\n")
        f.write(f"  Object: {r.object_type} (ID: {r.object_id})\n")
        f.write(f"  Status: {r.status}\n")
        f.write(f"  File: {r.file.name if r.file else 'EMPTY'}\n")
        f.write(f"  QR: {qr.code_image.name if qr and qr.code_image else 'NONE'}\n")
        # Try to find what exactly is in the QR code if possible (though we'd need to decode it)
        f.write("-" * 10 + "\n")

print(f"Diagnostics written to {log_file}")
