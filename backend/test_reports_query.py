import os
import sys
import django
import traceback

sys.path.append('c:/Users/Asus/Desktop/antigravity/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from vehicles.models import VehicleValuation
from reports.models import ReportDocument
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()
try:
    user = User.objects.filter(role='appraiser').first()
    
    if user:
        # Appraiser queryset logic
        processed_ids = VehicleValuation.objects.filter(
            Q(assigned_to=user) | 
            Q(status__in=['approved', 'rejected'])
        ).values_list('id', flat=True)
        
        queryset = ReportDocument.objects.all().order_by('-created_at')
        
        # EXACT get_queryset logic
        qs = queryset.filter(
            Q(user=user) | 
            Q(assigned_to=user) |
            Q(status__in=['approved', 'rejected']) |
            Q(object_id__in=list(processed_ids), object_type='vehicle')
        )
        
        print(f"Total reports found for {user.username}: {qs.count()}")
        print(f"Processed IDs: {list(processed_ids)}")
        
        # EXACT list logic
        for r in qs:
            print(f"Report ID: {r.id}, Type: {r.object_type}, Status: {r.status}")
        
    else:
        print("No appraiser found.")
except Exception as e:
    with open('c:/Users/Asus/Desktop/antigravity/backend/test_error.txt', 'w') as f:
        f.write(traceback.format_exc())
    print("Error caught and written to test_error.txt")
