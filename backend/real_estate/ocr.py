"""
Real Estate OCR Module — Reliable Edition
==========================================
Strategy:
  - Split files by type: PDF (kadastr doc) vs Images (ID card photos)
  - Call 1: Dedicated cadastre extraction using ONLY kadastr images
  - Call 2: Main fields extraction using ALL images
  - Robust retry: 503 → exponential backoff → model rotation
  - Region-based cadastre prefix validation as safety net
"""
import os
import time
try:
    import fitz
except ImportError:
    fitz = None
import json
import re
import base64
import numpy as np
import cv2
from pyzbar import pyzbar as pyzbar_lib
from PIL import Image, ImageEnhance
import requests
from io import BytesIO
from dotenv import load_dotenv

load_dotenv(r'c:\Users\Asus\Desktop\antigravity\backend\.env')
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    api_key = api_key.strip('"\'  ')

# O'zbekiston viloyat kodlari → Kadastr prefiksi
REGION_CODES = {
    'toshkent shahri': '10', 'toshkent sh.': '10',
    'toshkent viloyati': '11',
    'sirdaryo': '12',
    'jizzax': '13',
    'andijon': '14',
    "farg'ona": '15', 'fargona': '15',
    'namangan': '16',
    'buxoro': '17',
    'navoiy': '18',
    'qashqadaryo': '19',
    'surxondaryo': '20',
    'xorazm': '21',
    "qoraqalpog'iston": '22',
    'samarqand': '23',
}

# Models to try in order (fallback chain)
MODELS = [
    ('gemini-2.5-flash', 'v1'),
    ('gemini-2.5-pro',   'v1'),
    ('gemini-1.5-flash', 'v1beta'),
]


def log_ocr(msg):
    log_path = 'c:/Users/Asus/Desktop/antigravity/backend/ocr_live.log'
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - RE OCR: {msg}\n")
    except:
        pass
    try:
        print(f"RE OCR: {msg}", flush=True)
    except Exception:
        pass


def _read_qr_from_image(pil_img: Image.Image) -> list:
    """Read all QR codes from a PIL image using pyzbar. Returns list of decoded strings."""
    try:
        # Try multiple preprocessing levels for better QR detection
        results = []
        for scale in [1.0, 1.5, 2.0]:
            w, h = pil_img.size
            if scale != 1.0:
                img_resized = pil_img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
            else:
                img_resized = pil_img

            # Convert to grayscale numpy array for pyzbar
            img_gray = img_resized.convert('L')
            arr = np.array(img_gray)
            decoded = pyzbar_lib.decode(arr)
            for d in decoded:
                text = d.data.decode('utf-8', errors='ignore').strip()
                if text and text not in results:
                    results.append(text)
            if results:
                break  # Found QR codes, no need to try larger scale
        return results
    except Exception as e:
        log_ocr(f"QR read error: {e}")
        return []


def _extract_cadastre_from_qr(qr_texts: list) -> str:
    """Try to extract cadastre number from QR code content."""
    pattern = re.compile(r'\b(\d{2}:\d{2}:\d{2}:\d{2}:\d{2}:\d{3,})\b')
    for text in qr_texts:
        log_ocr(f"  QR content: {text[:120]}")
        m = pattern.search(text)
        if m:
            return m.group(1)
        # Also try URL params like ?kadastr=15:11:...
        url_m = re.search(r'kadastr[=:]([0-9:]+)', text, re.IGNORECASE)
        if url_m:
            cad = url_m.group(1)
            if re.match(r'\d{2}:\d{2}:\d{2}:\d{2}:\d{2}:\d+', cad):
                return cad
    return ""


def _scan_qr_from_files(file_paths: list) -> str:
    """Scan all uploaded files for QR codes and extract cadastre number."""
    for file_path in file_paths:
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == '.pdf':
                if fitz is None:
                    log_ocr("  Skipping QR scan for PDF, fitz is not loaded.")
                    continue
                doc = fitz.open(file_path)
                for i in range(min(len(doc), 4)):
                    pix = doc[i].get_pixmap(dpi=200)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    qr_texts = _read_qr_from_image(img)
                    if qr_texts:
                        cad = _extract_cadastre_from_qr(qr_texts)
                        if cad:
                            log_ocr(f"  QR → Cadastre: {cad} (from PDF page {i+1})")
                            return cad
                doc.close()
            else:
                img = Image.open(file_path).convert('RGB')
                qr_texts = _read_qr_from_image(img)
                if qr_texts:
                    cad = _extract_cadastre_from_qr(qr_texts)
                    if cad:
                        log_ocr(f"  QR → Cadastre: {cad} (from {os.path.basename(file_path)})")
                        return cad
        except Exception as e:
            log_ocr(f"  QR scan error ({os.path.basename(file_path)}): {e}")
    return ""


def _gemini_call(img_b64_list, prompt_text):
    """
    Reliable Gemini API call.
    - Tries multiple models in order
    - On 503: waits with exponential backoff, then retries same model
    - On 404: immediately tries next model
    """
    from vehicles.models import get_gemini_api_key
    current_api_key = get_gemini_api_key()
    if not current_api_key:
        log_ocr("No API key configured.")
        return None

    for model, api_ver in MODELS:
        url = (f"https://generativelanguage.googleapis.com/"
               f"{api_ver}/models/{model}:generateContent?key={current_api_key}")
        img_parts = [{"inlineData": {"mimeType": "image/jpeg", "data": b64}} for b64 in img_b64_list]
        payload = {
            "contents": [{"parts": img_parts + [{"text": prompt_text}]}],
            "generationConfig": {"temperature": 0.0, "maxOutputTokens": 4096, "topP": 0.1},
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
        }

        for attempt in range(3):  # 3 retries per model
            try:
                log_ocr(f"  Trying {model} (attempt {attempt + 1}/3)")
                resp = requests.post(url, json=payload, timeout=120)

                if resp.status_code == 503:
                    wait = 8 * (attempt + 1)  # 8s, 16s, 24s
                    log_ocr(f"  503 busy — waiting {wait}s...")
                    time.sleep(wait)
                    continue  # retry same model

                if resp.status_code == 404:
                    log_ocr(f"  404 model not found — trying next model")
                    break  # try next model immediately

                if resp.status_code != 200:
                    log_ocr(f"  HTTP {resp.status_code}: {resp.text[:150]}")
                    break

                rj = resp.json()
                candidates = rj.get("candidates", [])
                if not candidates:
                    log_ocr(f"  No candidates in response")
                    break

                parts = candidates[0].get("content", {}).get("parts", [])
                text = parts[0].get("text", "") if parts else ""
                if text:
                    log_ocr(f"  SUCCESS with {model}")
                    return text

            except Exception as e:
                log_ocr(f"  Exception: {e}")
                if attempt < 2:
                    time.sleep(3)

    log_ocr("  All models exhausted — returning None")
    return None


def _img_to_b64(img: Image.Image, quality=75) -> str:
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _enhance(img: Image.Image) -> Image.Image:
    img = ImageEnhance.Contrast(img).enhance(1.4)
    img = ImageEnhance.Sharpness(img).enhance(1.8)
    return img


def _pdf_to_images(file_path, max_pages=4) -> list:
    """Convert PDF pages to enhanced base64 images + 90° rotated + Cropped Quadrants."""
    images = []
    if fitz is None:
        log_ocr("  Skipping PDF to image conversion, fitz is not loaded.")
        return images
    try:
        doc = fitz.open(file_path)
        for i in range(min(len(doc), max_pages)):
            pix = doc[i].get_pixmap(dpi=150)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            if img.width > 1200:
                img.thumbnail((1200, 1200), Image.Resampling.BILINEAR)
            img = _enhance(img)
            
            # 1. Original
            images.append(_img_to_b64(img, quality=75))
            
            # 2. Rotated (for vertical text)
            images.append(_img_to_b64(img.rotate(90, expand=True), quality=70))
            
            # 3. "Digital Zoom" - Crop important areas (quadrants)
            w, h = img.size
            quads = [
                (0, 0, w//2, h//2),      # Top-left
                (w//2, 0, w, h//2),      # Top-right
                (0, h//2, w//2, h),      # Bottom-left
                (w//2, h//2, w, h)       # Bottom-right
            ]
            for q in quads:
                crop = img.crop(q)
                images.append(_img_to_b64(crop, quality=70))
                
        doc.close()
    except Exception as e:
        log_ocr(f"PDF error: {e}")
    return images


def _image_to_images(file_path) -> list:
    """Convert image file to enhanced base64 + 90° rotated + Cropped Quadrants."""
    images = []
    try:
        img = Image.open(file_path).convert('RGB')
        if img.width > 1200:
            img.thumbnail((1200, 1200), Image.Resampling.BILINEAR)
        img = _enhance(img)
        
        # 1. Original
        images.append(_img_to_b64(img, quality=75))
        
        # 2. Rotated
        images.append(_img_to_b64(img.rotate(90, expand=True), quality=70))
        
        # 3. Cropped Quadrants (Zoom)
        w, h = img.size
        quads = [
            (0, 0, w//2, h//2),
            (w//2, 0, w, h//2),
            (0, h//2, w//2, h),
            (w//2, h//2, w, h)
        ]
        for q in quads:
            crop = img.crop(q)
            images.append(_img_to_b64(crop, quality=70))
            
    except Exception as e:
        log_ocr(f"Image error: {e}")
    return images


def _parse_json(text: str) -> dict | None:
    """Extract JSON from model response text."""
    if not text:
        return None
    # Try direct JSON
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if not m:
        # Try code block JSON
        block = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if block:
            m = re.search(r'\{.*\}', block.group(1), re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except:
            pass
    return None


def _fix_cadastre_prefix(cadastre: str, region: str, location: str) -> str:
    """Auto-fix first 2 digits of cadastre number based on region name."""
    if not cadastre:
        return cadastre
    region_text = (region + ' ' + location).lower()
    for region_name, code in REGION_CODES.items():
        if region_name in region_text:
            parts = cadastre.split(':')
            if len(parts) >= 1 and parts[0] != code:
                old = cadastre
                parts[0] = code
                cadastre = ':'.join(parts)
                log_ocr(f"  Cadastre prefix corrected: {old} → {cadastre} ({region_name})")
            break
    return cadastre


def extract_real_estate_info(file_paths):
    """
    Main entry point.
    Splits files into kadastr (PDF) and ID-card (images),
    then runs two focused AI calls.
    """
    if isinstance(file_paths, str):
        file_paths = [file_paths]

    log_ocr(f"=== Starting RE OCR for {len(file_paths)} file(s) ===")
    from vehicles.models import get_gemini_api_key
    current_api_key = get_gemini_api_key()

    # ── Stage 0: QR Code scan (100% accurate if found) ──
    log_ocr("--- Stage 0: QR Code scan ---")
    qr_cadastre = _scan_qr_from_files(file_paths)
    if qr_cadastre:
        log_ocr(f"  ✅ QR cadastre found: {qr_cadastre}")
    else:
        log_ocr("  QR not found — will use AI OCR for cadastre")

    data = {
        'owner_name': '',
        'cadastre_number': '',
        'total_area': 0.0,
        'location': '',
        'built_year': 0,
        'passport_serial': '',
        'passport_jshshir': '',
        'passport_given_by': '',
        'region': '',
        'district': '',
    }

    if not current_api_key:
        log_ocr("No API key.")
        return data

    # ── Separate files: PDFs (kadastr docs) vs Images (ID cards) ──
    pdf_images = []   # kadastr document images
    id_images = []    # ID card photos

    for fp in file_paths:
        ext = os.path.splitext(fp)[1].lower()
        if ext == '.pdf':
            imgs = _pdf_to_images(fp)
            pdf_images.extend(imgs)
            log_ocr(f"  PDF → {len(imgs)} image variants: {os.path.basename(fp)}")
        else:
            imgs = _image_to_images(fp)
            id_images.extend(imgs)
            log_ocr(f"  IMG → {len(imgs)} image variants: {os.path.basename(fp)}")

    all_images = pdf_images + id_images
    log_ocr(f"  Total variants: {len(all_images)} (kadastr: {len(pdf_images)}, id: {len(id_images)})")

    if not all_images:
        log_ocr("No images prepared.")
        return data

    # ── CALL 1: Dedicated cadastre extraction (only if QR didn't find it) ──
    if qr_cadastre:
        data['cadastre_number'] = qr_cadastre
        log_ocr(f"--- Call 1: Skipped (QR already found: {qr_cadastre}) ---")
    else:
        cadastre_images = pdf_images if pdf_images else all_images
        cadastre_prompt = """Bu O'zbekiston Davlat Kadastr Palatasi tomonidan berilgan hujjat.

FAQAT BITTA NARSA: Kadastr raqamini toping.

Format: XX:XX:XX:XX:XX:XXXX (masalan: 16:11:41:01:01:1259)
Hujjatda "Kadastr raqami" degan qator yonida yozilgan.
Raqam vertikal yozilgan bo'lishi mumkin.

Faqat JSON:
{"cadastre_number": "..."}"""

        log_ocr("--- Call 1: Cadastre (AI) ---")
        cad_text = _gemini_call(cadastre_images, cadastre_prompt)
        cad_parsed = _parse_json(cad_text)
        if cad_parsed:
            cad = str(cad_parsed.get('cadastre_number', '')).strip()
            if re.match(r'\d{2}:\d{2}:\d{2}:\d{2}:\d{2}:\d+', cad):
                data['cadastre_number'] = cad
                log_ocr(f"  Cadastre extracted: {cad}")
        else:
            log_ocr(f"  Cadastre invalid format: {cad!r}")

    # ── CALL 2: All other fields (use only original images to save bandwidth) ──
    # Using only the first variant (original) of each file to avoid timeouts
    main_call_images = []
    for fp in file_paths:
        ext = os.path.splitext(fp)[1].lower()
        if ext == '.pdf':
            # For PDF, just take first page original
            if fitz is None:
                log_ocr("  Skipping main fields PDF extract, fitz is not loaded.")
                continue
            try:
                doc = fitz.open(fp)
                if len(doc) > 0:
                    pix = doc[0].get_pixmap(dpi=200)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    main_call_images.append(_img_to_b64(img))
                doc.close()
            except: pass
        else:
            try:
                img = Image.open(fp).convert('RGB')
                if img.width > 2000: img.thumbnail((2000, 2000))
                main_call_images.append(_img_to_b64(img))
            except: pass

    if not main_call_images:
        main_call_images = all_images[:len(file_paths)]

    main_prompt = """Siz O'zbekiston ko'chmas mulk hujjatlari va ID-kartalarni tahlil qiluvchi mutaxassissiz.

Quyidagi ma'lumotlarni oling:

1. owner_name — To'liq F.I.Sh.
2. total_area — "Yer maydoni, (kv.m)" qatoridagi raqam (masalan: 794 yoki 1700.00)
3. location — "I. Manzil haqida ma'lumotlar" jadvalidagi to'liq manzil
4. built_year — Binoning qurilgan yili (aniq bo'lmasa: 0)
5. passport_serial — ID-kartaning "Karta raqami / Card number" (masalan: AE3928307)
6. passport_jshshir — ID-kartaning "Shaxsiy raqami / Personal number" — 14 ta raqam. MRZ satridan (<<< bor) olishga urinmang!
7. passport_given_by — "Berilgan joyi / Place of issue"
8. region — Mulk joylashgan viloyat
9. district — Mulk joylashgan tuman

QOIDALAR:
- FAQAT JSON qaytaring
- Taxmin qilmang — faqat rasmda ko'ringan narsani yozing

JSON:
{
  "owner_name": "",
  "total_area": 0.0,
  "location": "",
  "built_year": 0,
  "passport_serial": "",
  "passport_jshshir": "",
  "passport_given_by": "",
  "region": "",
  "district": ""
}"""

    log_ocr("--- Call 2: Main fields ---")
    main_text = _gemini_call(all_images, main_prompt)
    main_parsed = _parse_json(main_text)

    if main_parsed:
        for k in data.keys():
            if k == 'cadastre_number':
                continue  # already handled
            val = main_parsed.get(k)
            if val is None:
                continue
            if k == 'total_area':
                try:
                    val = float(re.sub(r'[^\d\.,]', '', str(val)).replace(',', '.'))
                except:
                    val = 0.0
            elif k == 'built_year':
                try:
                    val = int(float(str(val)))
                except:
                    val = 0
            data[k] = val

    # ── Auto-fix cadastre region prefix ──
    data['cadastre_number'] = _fix_cadastre_prefix(
        data['cadastre_number'],
        data.get('region', ''),
        data.get('location', '')
    )

    log_ocr(f"=== Final: {data} ===")
    return data
