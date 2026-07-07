import os
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.files import File
from .models import Book
from .serializers import BookSerializer
from .utils import index_book_in_chroma


def convert_docx_to_pdf_local(docx_path):
    """Convert a .docx file to PDF using docx2pdf and return the new PDF path."""
    try:
        from docx2pdf import convert
        pdf_path = docx_path.replace('.docx', '.pdf').replace('.DOCX', '.pdf')
        convert(docx_path, pdf_path)
        if os.path.exists(pdf_path):
            return pdf_path
    except Exception as e:
        print(f"docx2pdf conversion failed: {e}")
    return None


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def perform_create(self, serializer):
        book = serializer.save()

        # Convert .docx to PDF for browser viewing
        if book.file and book.file.name.lower().endswith('.docx'):
            try:
                docx_path = book.file.path
                pdf_path = convert_docx_to_pdf_local(docx_path)
                if pdf_path:
                    rel_path = os.path.relpath(pdf_path, start=os.path.dirname(os.path.dirname(book.file.path)))
                    # Save the PDF as the book's file
                    with open(pdf_path, 'rb') as pf:
                        pdf_filename = os.path.basename(pdf_path)
                        book.file.save(pdf_filename, File(pf), save=True)
                    print(f"[Books] Converted docx -> pdf: {pdf_filename}")
            except Exception as e:
                print(f"[Books] docx->pdf conversion error for book {book.id}: {e}")

        # Automatically index in ChromaDB after upload
        try:
            result = index_book_in_chroma(book)
            print(f"[Books] Indexing result for book {book.id}: {result}")
        except Exception as e:
            print(f"[Books] Indexing failed for book {book.id}: {e}")

    @action(detail=True, methods=['post'])
    def reindex(self, request, pk=None):
        book = self.get_object()
        success = index_book_in_chroma(book)
        if success:
            return Response({"status": "Kitob muvaffaqiyatli indekslandi"})
        else:
            return Response({"error": "Indekslashda xatolik yuz berdi"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='reindex-all')
    def reindex_all(self, request):
        """Reindex all books into ChromaDB."""
        results = []
        for book in Book.objects.all():
            try:
                ok = index_book_in_chroma(book)
                results.append({"id": book.id, "title": book.title, "indexed": ok})
            except Exception as e:
                results.append({"id": book.id, "title": book.title, "error": str(e)})
        return Response({"results": results})
