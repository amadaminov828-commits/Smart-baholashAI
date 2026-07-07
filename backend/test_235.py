import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from vehicles.models import VehicleValuation
from reports.models import ReportDocument, QRCode
from django.conf import settings
import glob

val_id = 235
print(f"Checking ID {val_id}...")

reports = ReportDocument.objects.filter(object_id=val_id, object_type='vehicle')
print(f"Reports in DB for {val_id}: {reports.count()}")

qr_pattern = os.path.join(settings.MEDIA_ROOT, 'qrcodes', f'*{val_id}*')
qr_files = glob.glob(qr_pattern) + glob.glob(os.path.join(settings.MEDIA_ROOT, 'qrcodes', '*'))
print(f"Total QR files in media/qrcodes: {len(glob.glob(os.path.join(settings.MEDIA_ROOT, 'qrcodes', '*')))}")

pdf_pattern = os.path.join(settings.MEDIA_ROOT, 'tmp', '*', f'report_{val_id}.pdf')
pdf_files = glob.glob(pdf_pattern)
print(f"Found PDF files on disk: {pdf_files}")

docx_pattern = os.path.join(settings.MEDIA_ROOT, 'tmp', '*', f'report_{val_id}.docx')
docx_files = glob.glob(docx_pattern)
print(f"Found DOCX files on disk: {docx_files}")

