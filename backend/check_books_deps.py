try:
    import chromadb
    print("chromadb is installed")
except ImportError:
    print("chromadb is MISSING")

try:
    import docx
    print("python-docx is installed")
except ImportError:
    print("python-docx is MISSING")

try:
    from pypdf import PdfReader
    print("pypdf is installed")
except ImportError:
    print("pypdf is MISSING")
