from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'description', 
            'file', 'cover_image', 'category', 
            'category_display', 'is_indexed', 'uploaded_at'
        ]
