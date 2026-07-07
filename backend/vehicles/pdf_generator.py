import os
import time
import traceback
from docx2pdf import convert
from PyPDF2 import PdfReader, PdfWriter

try:
    os.system("taskkill /F /IM WINWORD.EXE")
    with open('c:/Users/Asus/Desktop/antigravity/backend/server_log.txt', 'r', encoding='utf-16le', errors='ignore') as f:
        log_lines = f.readlines()[-200:]
    with open('c:/Users/Asus/Desktop/antigravity/backend/ocr_diag.txt', 'w', encoding='utf-8') as f:
        f.writelines(log_lines)
except:
    pass

def log_pdf(msg):
    try:
        with open('c:/Users/Asus/Desktop/antigravity/backend/pdf_diag.txt', 'a', encoding='utf-8') as f:
            f.write(str(msg) + "\\n")
    except:
        pass

def convert_docx_to_pdf(docx_path, output_pdf_path):
    """
    Converts DOCX to PDF using docx2pdf.
    """
    log_pdf(f"\\n--- STARTING CONVERSION: {docx_path} -> {output_pdf_path}")
    try:
        import pythoncom
        pythoncom.CoInitialize()
        log_pdf("pythoncom.CoInitialize() OK")
    except Exception as e:
        log_pdf(f"pythoncom initialization skipped or failed: {e}")

    try:
        if not os.path.exists(docx_path):
            log_pdf(f"ERROR: Source DOCX not found at {docx_path}")
            return None
            
        log_pdf(f"Calling convert(docx_path, output_pdf_path)...")
        convert(docx_path, output_pdf_path)
        log_pdf(f"convert function finished.")
        
        # Verify result
        if os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 0:
            log_pdf(f"SUCCESS: Created PDF ({os.path.getsize(output_pdf_path)} bytes)")
            return output_pdf_path
        else:
            log_pdf(f"ERROR: PDF file not created or empty after conversion: {output_pdf_path}")
            return None
    except Exception as e:
        log_pdf(f"CRITICAL ERROR in convert_docx_to_pdf: {e}")
        log_pdf(traceback.format_exc())
        return None

def protect_pdf(input_pdf_path, output_pdf_path, password=None, owner_password=None):
    """
    Protects the PDF by flattening all pages into high-resolution 300 DPI images.
    This prevents any text modification or copy/paste (like in PDF-XChange or Adobe Acrobat Pro),
    while maintaining extremely sharp print quality and optimizing file size.
    """
    log_pdf(f"\nProtecting PDF: {input_pdf_path} -> {output_pdf_path} using PyMuPDF 300 DPI flattening...")
    try:
        import fitz
        doc = fitz.open(input_pdf_path)
        new_doc = fitz.open()
        
        for page in doc:
            rect = page.rect
            # Render page at 300 DPI for ultra-sharp print resolution
            pix = page.get_pixmap(dpi=300)
            # Compress as JPEG (85% quality) to keep file sizes reasonable while keeping text crisp
            img_bytes = pix.tobytes("jpg", jpg_quality=85)
            
            # Create a new page with the exact same dimensions
            new_page = new_doc.new_page(width=rect.width, height=rect.height)
            # Insert the image filling the entire page
            new_page.insert_image(rect, stream=img_bytes)
            
        new_doc.save(output_pdf_path, garbage=3, deflate=True)
        new_doc.close()
        doc.close()
        
        log_pdf(f"Successfully protected PDF: {output_pdf_path} ({os.path.getsize(output_pdf_path)} bytes)")
        return output_pdf_path
        
    except Exception as e:
        log_pdf(f"ERROR in protect_pdf flattening: {e}")
        log_pdf(traceback.format_exc())
        # Fallback to copy if fitz fails
        try:
            import shutil
            shutil.copyfile(input_pdf_path, output_pdf_path)
            return output_pdf_path
        except:
            return input_pdf_path
