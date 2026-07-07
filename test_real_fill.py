"""
Test fill_docx_template with the actual full context from a recent report valuation.
This mimics what the view does when generating a report.
"""
import os, sys

BACKEND_DIR = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, BACKEND_DIR)
os.chdir(BACKEND_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')

import django
django.setup()

from vehicles.models import VehicleValuation
from reports.models import ReportTemplate
from vehicles.views import VehicleValuationViewSet

# Get latest report
report = VehicleValuation.objects.order_by('-created_at').first()
if not report:
    print("No report found"); sys.exit(1)

template = ReportTemplate.objects.filter(object_type='vehicle').order_by('-created_at').first()
if not template:
    print("No active template found"); sys.exit(1)

print(f"Report: {report.id}, status: {report.status}")
print(f"Template: {template.id}, file: {template.file.path if template.file else None}")

# Build context using the same method as in views.py
vs = VehicleValuationViewSet()
try:
    context = vs._build_report_context(report, template)
    print(f"Context keys: {list(context.keys())[:10]}...")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Failed to build context: {e}")
    sys.exit(1)

# Now call fill_docx_template with this context
from vehicles.docx_generator import fill_docx_template
import tempfile, comtypes.client

out_dir = os.path.join(BACKEND_DIR, 'debug_stages')
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'test_real_output.docx')

print(f"\nCalling fill_docx_template...")
try:
    result = fill_docx_template(template.file.path, out_path, context, qr_code_path=None)
    print(f"fill_docx_template returned: {result}")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"fill_docx_template FAILED: {e}")
    sys.exit(1)

if not os.path.exists(out_path):
    print(f"Output file not created: {out_path}"); sys.exit(1)

print(f"\nTesting output with Word...")
word = comtypes.client.CreateObject('Word.Application')
word.Visible = False
pdf_out = out_path.replace('.docx', '_test.pdf')
try:
    doc = word.Documents.Open(os.path.abspath(out_path))
    doc.SaveAs(os.path.abspath(pdf_out), FileFormat=17)
    doc.Close()
    word.Quit()
    print(f"SUCCESS: PDF saved to {pdf_out}")
except Exception as e:
    try: word.Quit()
    except: pass
    print(f"FAILED: {e}")
    
    # Now bisect: try without the a:p processing (DrawingML)
    print("\n--- Bisect: Checking if DrawingML a:p processing causes corruption ---")
    print("Check backend/vehicles/docx_generator.py line 769: process_xml_paragraph(ap, 'a')")
    print("This processes 'a:p' elements which are in shapes/diagrams/charts.")
    print("These could get corrupted when OxmlElement('a:r') is inserted wrongly.")
