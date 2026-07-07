import os
import sys
import django

sys.path.append('c:/Users/Asus/Desktop/antigravity/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from vehicles.models import VehicleValuation
from reports.models import ReportDocument
from django.contrib.auth import get_user_model

User = get_user_model()
appraiser = User.objects.filter(role='appraiser').first()

if appraiser:
    # 1. Fix VehicleValuations
    orphaned_vals = VehicleValuation.objects.filter(status__in=['approved', 'rejected'], assigned_to__isnull=True)
    count1 = orphaned_vals.count()
    orphaned_vals.update(assigned_to=appraiser)
    
    # 2. Fix ReportDocuments
    orphaned_reps = ReportDocument.objects.filter(status__in=['approved', 'rejected'], assigned_to__isnull=True)
    count2 = orphaned_reps.count()
    orphaned_reps.update(assigned_to=appraiser)
    
    # Also sync ReportDocument status with Valuation status just in case they went out of sync
    for val in VehicleValuation.objects.exclude(status='draft'):
        rep = ReportDocument.objects.filter(object_id=val.id, object_type='vehicle').first()
        if rep and rep.status != val.status:
            rep.status = val.status
            rep.assigned_to = val.assigned_to
            rep.save()

    with open('c:/Users/Asus/Desktop/antigravity/backend/sync_result.txt', 'w') as f:
        f.write(f"Fixed {count1} valuations and {count2} reports. Assigned to {appraiser.username}")
else:
    with open('c:/Users/Asus/Desktop/antigravity/backend/sync_result.txt', 'w') as f:
        f.write("No appraiser found!")
