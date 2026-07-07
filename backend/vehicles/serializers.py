from rest_framework import serializers
from .models import VehicleValuation, VehicleAnalog, GlobalAnalog

class GlobalAnalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalAnalog
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

class VehicleAnalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleAnalog
        fields = '__all__'
        read_only_fields = ['valuation']

class VehicleValuationSerializer(serializers.ModelSerializer):
    analogs = VehicleAnalogSerializer(many=True, read_only=True)
    report_file_pdf = serializers.SerializerMethodField()
    report_file_docx = serializers.SerializerMethodField()
    qr_url = serializers.SerializerMethodField()

    class Meta:
        model = VehicleValuation
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

    def get_report_file_pdf(self, obj):
        import os, glob
        from django.conf import settings
        from reports.models import ReportDocument
        report = ReportDocument.objects.filter(object_id=obj.id, object_type='vehicle').exclude(file='').order_by('-created_at').first()
        if report and report.file:
            return report.file.url
            
        # Fallback searching on disk
        search_pattern = os.path.join(settings.MEDIA_ROOT, 'tmp', '*', f'report_{obj.id}_protected.pdf')
        matches = glob.glob(search_pattern)
        if not matches:
            search_pattern = os.path.join(settings.MEDIA_ROOT, 'tmp', '*', f'report_{obj.id}.pdf')
            matches = glob.glob(search_pattern)
            
        if matches:
            newest_file = max(matches, key=os.path.getmtime)
            rel_path = os.path.relpath(newest_file, settings.MEDIA_ROOT).replace('\\', '/')
            return f"{settings.MEDIA_URL}{rel_path}"
            
        return None

    def get_report_file_docx(self, obj):
        import os, glob
        from django.conf import settings
        from reports.models import ReportDocument
        report = ReportDocument.objects.filter(object_id=obj.id, object_type='vehicle').order_by('-created_at').first()
        
        # First try the normal way if report.file exists
        if report and report.file:
            try:
                base_dir = os.path.dirname(report.file.url)
                docx_name = f"report_{obj.id}.docx"
                return f"{base_dir}/{docx_name}"
            except Exception:
                pass
                
        # If report.file failed (e.g., PDF error), find the docx using glob in media/tmp
        search_pattern = os.path.join(settings.MEDIA_ROOT, 'tmp', '*', f'report_{obj.id}.docx')
        matches = glob.glob(search_pattern)
        if matches:
            # Sort by modification time to get the newest
            newest_file = max(matches, key=os.path.getmtime)
            rel_path = os.path.relpath(newest_file, settings.MEDIA_ROOT).replace('\\', '/')
            return f"{settings.MEDIA_URL}{rel_path}"
            
        return None

    def get_qr_url(self, obj):
        import os, glob
        from django.conf import settings
        from reports.models import ReportDocument, QRCode
        
        # PRIORITIZE report with a file and approved status
        report = ReportDocument.objects.filter(
            object_id=obj.id, 
            object_type='vehicle',
            status='approved'
        ).exclude(file='').exclude(file__isnull=True).order_by('-created_at').first()
        
        # If no approved, try any with a file
        if not report:
            report = ReportDocument.objects.filter(
                object_id=obj.id, 
                object_type='vehicle'
            ).exclude(file='').exclude(file__isnull=True).order_by('-created_at').first()
            
        # Last resort fallback to the very latest
        if not report:
            report = ReportDocument.objects.filter(
                object_id=obj.id, 
                object_type='vehicle'
            ).order_by('-created_at').first()

        if report:
            qr = QRCode.objects.filter(report=report).first()
            if qr and qr.code_image:
                return qr.code_image.url
                
            # Fallback searching on disk
            search_pattern = os.path.join(settings.MEDIA_ROOT, 'qrcodes', f'qr_{report.id}.png')
            matches = glob.glob(search_pattern)
            if not matches:
                 search_pattern = os.path.join(settings.MEDIA_ROOT, 'qrcodes', f'*{report.id}*.png')
                 matches = glob.glob(search_pattern)
                 
            if matches:
                 newest_file = max(matches, key=os.path.getmtime)
                 rel_path = os.path.relpath(newest_file, settings.MEDIA_ROOT).replace('\\', '/')
                 return f"{settings.MEDIA_URL}{rel_path}"
                 
        return None

class OCRDocumentUploadSerializer(serializers.Serializer):
    documents = serializers.ListField(
        child=serializers.FileField(),
        required=True
    )
