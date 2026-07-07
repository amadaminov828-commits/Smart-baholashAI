from rest_framework import serializers
from .models import RealEstateValuation, RealEstateAnalog
from reports.models import ReportDocument


class RealEstateAnalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealEstateAnalog
        fields = '__all__'
        read_only_fields = ['valuation']

class RealEstateValuationSerializer(serializers.ModelSerializer):
    analogs = RealEstateAnalogSerializer(many=True, read_only=True)
    report_data = serializers.SerializerMethodField()

    def get_report_data(self, obj):
        report = ReportDocument.objects.filter(object_id=obj.id, object_type='real_estate').order_by('-created_at').first()
        if report and report.file:
            return {
                'id': report.id,
                'file_url': report.file.url,
                'status': report.status,
                'docx_url': f"/media/reports/docx/report_{report.id}.docx" if report.status == 'approved' else None
            }
        return None


    class Meta:
        model = RealEstateValuation
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']


class RealEstateOCRUploadSerializer(serializers.Serializer):
    documents = serializers.ListField(
        child=serializers.FileField(),
        required=True
    )
    images = serializers.ListField(
        child=serializers.ImageField(), required=False, max_length=6
    )
