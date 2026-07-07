"""
report_540.docx ni qaysi bosqich buzishini aniqlash uchun test.
Har bir bosqichdan keyin Word bilan ochib tekshiramiz.
"""
import os, sys, shutil, comtypes.client

sys.path.insert(0, 'backend')
os.environ['DJANGO_SETTINGS_MODULE'] = 'valuation_platform.settings'
import django
django.setup()

from docxtpl import DocxTemplate, InlineImage
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import RGBColor
from docx.oxml.shared import OxmlElement
from docx.oxml.ns import qn
import datetime

STAGES_DIR = 'backend/debug_stages/bisect540'
os.makedirs(STAGES_DIR, exist_ok=True)

# Shablon va context
from reports.models import ReportTemplate
from vehicles.models import VehicleValuation

valuation = VehicleValuation.objects.get(id=540)
template = ReportTemplate.objects.get(id=234)
template_path = template.file.path
print(f"Shablon: {template_path}")
print(f"Valuation: {valuation.id}, model: {valuation.car_model}")

# Views dan context olish
from vehicles.views import VehicleValuationViewSet
import importlib, inspect

# views.py dagi context qurilish kodini topamiz
views_mod = importlib.import_module('vehicles.views')
vs_class = views_mod.VehicleValuationViewSet

def word_test(path, label):
    word = comtypes.client.CreateObject('Word.Application')
    word.Visible = False
    try:
        doc = word.Documents.Open(os.path.abspath(path))
        doc.Close()
        word.Quit()
        print(f"  ✓ {label}: YAXSHI")
        return True
    except Exception as e:
        try: word.Quit()
        except: pass
        print(f"  ✗ {label}: BUZILGAN - {e}")
        return False

# Haqiqiy context ni to'g'ridan-to'g'ri views.py generate_report dan olamiz
# Lekin avval fill_docx_template ni step-by-step chaqiramiz

# fill_docx_template kodini ko'rib chiqamiz:
from vehicles.docx_generator import fill_docx_template
import vehicles.docx_generator as dg
import inspect

# Haqiqiy kontekstni olish uchun views kodini ishga tushiramiz 
# (lekin fayl saqlash qismini bloklagan holda)
from unittest.mock import patch, MagicMock
import json

# Valuation uchun context ni qurish
# Bu kodni views.py > generate_report dan ko'chiramiz
from django.conf import settings
from vehicles.models import VehicleValuationReport
import concurrent.futures, time, traceback

# Haqiqiy report_540 docx fayl
existing_docx = 'backend/media/tmp/49ad23d00427/report_540.docx'

# 1. Avval existing docxni test qilamiz
print("\n=== 0. Mavjud report_540.docx ===")
word_test(existing_docx, "Mavjud DOCX")

# 2. Sof shablon faylini jinja render
print("\n=== 1. Sof jinja render (minimal context) ===")
stage1 = f"{STAGES_DIR}/s1_jinja.docx"
minimal_ctx = {
    'hisobot_sanasi': datetime.date.today().strftime('%d.%m.%Y'),
    'report_id_str': 'TEST-540',
    'report_status': 'approved'
}
try:
    tpl = DocxTemplate(template_path)
    tpl.render(minimal_ctx, autoescape=True)
    tpl.save(stage1)
    word_test(stage1, "Stage 1 jinja minimal")
except Exception as e:
    print(f"  XATO: {e}")
    import traceback; traceback.print_exc()

# 3. fill_docx_template ni HAQIQIY context bilan chaqiramiz
# Context ni views.py dan olish uchun
print("\n=== 2. fill_docx_template (haqiqiy context) ===")
stage2 = f"{STAGES_DIR}/s2_fill_real.docx"

# Views kodini ishlatib context quramiz
# (biz faqat context kerak, PDF/save kerak emas)
try:
    # Views.py generate_report funksiyasiga o'xshash context quramiz
    from vehicles.views import VehicleValuationViewSet
    
    # Oddiyroq: generate_report method kodidagi context build qismini nusxalaymiz
    # valuation 540 uchun
    v = valuation
    
    # Analog va narxlarni olish
    analogs = list(v.analogs.all()[:3]) if hasattr(v, 'analogs') else []
    print(f"  Analoglar soni: {len(analogs)}")
    
    # Haqiqiy generate_report endpoint ni chaqiramiz lekin faqat docx yasash
    # Buning uchun HTTP so'rov qilamiz
    import requests
    
    # Token olish
    token_res = requests.post('http://127.0.0.1:8000/api/v1/users/login/', json={
        'username': 'admin', 'password': 'admin123'
    })
    if token_res.status_code == 200:
        token = token_res.json().get('access') or token_res.json().get('token')
        print(f"  Token olindi: {bool(token)}")
    else:
        print(f"  Login xato: {token_res.status_code}, {token_res.text[:100]}")
        token = None
except Exception as e:
    print(f"  XATO: {e}")
    import traceback; traceback.print_exc()
    token = None

print("\nXulosa: fill_docx_template haqiqiy context bilan ishlasini tekshirish uchun")
print("Server logidan ko'rish kerak. test_docx_corruption.py ishga tushirildi.")
