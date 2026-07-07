import os
from pathlib import Path
from django.conf import settings
from chat.services import ChatService

# Try to import document loaders
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    import docx
except ImportError:
    docx = None

def extract_text_from_file(file_path):
    path = Path(file_path)
    ext = path.suffix.lower()
    
    if ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif ext == '.pdf':
        if PdfReader is None: return None
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
        return text
    elif ext == '.docx':
        if docx is None: return None
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    return None

def index_book_in_chroma(book):
    """Extracts text from book and adds it to ChromaDB collection."""
    if not book.file:
        return False

    file_path = book.file.path
    content = extract_text_from_file(file_path)
    
    if not content:
        return False

    # Initialize Chroma
    try:
        import chromadb
        db_path = str(Path(settings.BASE_DIR) / 'chroma_db')
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_or_create_collection(name="evaluation_books")
    except Exception as e:
        print(f"CRITICAL: Could not load ChromaDB in books.utils: {e}")
        return False

    # Split text into chunks
    chunks = [content[i:i+1000] for i in range(0, len(content), 800)]
    
    ids = [f"book_{book.id}_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "book_id": book.id, 
            "title": book.title, 
            "source": os.path.basename(file_path),
            "category": book.category
        } for _ in range(len(chunks))
    ]
    
    collection.add(
        documents=chunks,
        ids=ids,
        metadatas=metadatas
    )
    
    book.is_indexed = True
    book.save()
    return True
