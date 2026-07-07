import os
from django.core.management.base import BaseCommand
from django.conf import settings
import chromadb
from pathlib import Path

# Try to import document loaders
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    import docx
except ImportError:
    docx = None

class Command(BaseCommand):
    help = 'Knowledge base hujjatlarini Chroma DB ga indekslaydi'

    def handle(self, *args, **options):
        kb_path = Path(settings.BASE_DIR) / 'knowledge_base'
        if not kb_path.exists():
            os.makedirs(kb_path)
            self.stdout.write(self.style.WARNING(f"'{kb_path}' papkasi yaratildi. Iltimos, unga hujjatlarni joylang."))
            return

        db_path = str(Path(settings.BASE_DIR) / 'chroma_db')
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_or_create_collection(name="evaluation_books")

        files = list(kb_path.glob('*.pdf')) + list(kb_path.glob('*.docx')) + list(kb_path.glob('*.txt'))
        
        if not files:
            self.stdout.write(self.style.WARNING("Hujjatlar topilmadi (.pdf, .docx, .txt)"))
            return

        for file_path in files:
            self.stdout.write(f"Ishlanmoqda: {file_path.name}...")
            content = self.extract_text(file_path)
            
            if not content:
                self.stdout.write(self.style.ERROR(f"Matnni o'qib bo'lmadi: {file_path.name}"))
                continue

            # Split text into chunks (e.g., ~1000 chars)
            chunks = [content[i:i+1000] for i in range(0, len(content), 800)]
            
            ids = [f"{file_path.name}_{i}" for i in range(len(chunks))]
            metadatas = [{"source": file_path.name} for _ in range(len(chunks))]
            
            collection.add(
                documents=chunks,
                ids=ids,
                metadatas=metadatas
            )
            self.stdout.write(self.style.SUCCESS(f"Muvaffaqiyatli indekslandi: {file_path.name} ({len(chunks)} ta bo'lak)"))

    def extract_text(self, file_path):
        ext = file_path.suffix.lower()
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif ext == '.pdf':
            if PdfReader is None:
                self.stdout.write(self.style.ERROR("pypdf o'rnatilmagan!"))
                return None
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        elif ext == '.docx':
            if docx is None:
                self.stdout.write(self.style.ERROR("python-docx o'rnatilmagan!"))
                return None
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        return None
