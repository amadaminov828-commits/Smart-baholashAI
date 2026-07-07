import os
import django
import sys
import docx

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valuation_platform.settings')
django.setup()

from reports.models import ReportTemplate

def analyze_template_content():
    templates = ReportTemplate.objects.all().order_by('-created_at')[:1]
    with open('template_dump2.txt', 'w', encoding='utf-8') as f:
        f.write("Analyzing the latest template...\n\n")
        
        for template in templates:
            f.write(f"--- Template: {template.name} (ID: {template.id}) ---\n")
            f.write(f"Path: {template.file.path}\n\n")
            
            try:
                doc = docx.Document(template.file.path)
                
                f.write("=== FIRST 2000 CHARACTERS ===\n")
                preview = "\n".join([p.text for p in doc.paragraphs if p.text.strip()][:50])
                f.write(preview[:2000] + "\n")
                
            except Exception as e:
                f.write(f"Error reading docx: {e}\n")
            f.write("\n")

if __name__ == '__main__':
    analyze_template_content()
