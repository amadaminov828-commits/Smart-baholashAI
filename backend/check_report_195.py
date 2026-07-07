import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportDocument
try:
    report = ReportDocument.objects.filter(object_id=195, object_type='vehicle').order_by('-created_at').first()
    if not report:
        print("Report not found for id 195!")
    else:
        print("Report ID:", report.id)
        if report.file:
            print("File:", report.file.name)
            try:
                print("URL:", report.file.url)
            except Exception as e:
                print("File URL Error:", e)
        else:
            print("No file attached.")
            
        from reports.models import QRCode
        qr_model = QRCode.objects.filter(report=report).first()
        if qr_model and qr_model.code_image:
            try:
                print("QR URL:", qr_model.code_image.url)
            except Exception as e:
                print("QR URL Error:", e)
        else:
            print("No QR attached.")
except Exception as e:
    print("General Error:", e)
