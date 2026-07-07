import os
import django
import docx

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportTemplate

def analyze_template_content():
    templates = ReportTemplate.objects.all().order_by('-created_at')[:1]
    with open('template_dump3.txt', 'w', encoding='utf-8') as f:
        f.write("Analyzing the latest template (middle section)...\n\n")
        
        for template in templates:
            try:
                doc = docx.Document(template.file.path)
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                
                f.write("=== PARAGRAPHS 80 TO 150 ===\n")
                preview = "\n".join(paragraphs[80:150])
                f.write(preview + "\n")
                
            except Exception as e:
                f.write(f"Error reading docx: {e}\n")

if __name__ == '__main__':
    analyze_template_content()
