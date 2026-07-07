from django.db import models
import os

class Book(models.Model):
    CATEGORY_CHOICES = [
        ('real_estate', 'Ko\'chmas mulk'),
        ('vehicles', 'Transport vositalari'),
        ('legal', 'Qonunchilik'),
        ('methodology', 'Metodologiya'),
        ('other', 'Boshqa'),
    ]

    title = models.CharField(max_length=255, verbose_name="Kitob nomi")
    author = models.CharField(max_length=255, blank=True, null=True, verbose_name="Muallif")
    description = models.TextField(blank=True, null=True, verbose_name="Tavsif")
    file = models.FileField(upload_to='books/files/', verbose_name="Fayl (PDF/Docx)")
    cover_image = models.ImageField(upload_to='books/covers/', blank=True, null=True, verbose_name="Muqova rasmi")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other', verbose_name="Kategoriya")
    is_indexed = models.BooleanField(default=False, verbose_name="Indekslangan")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Kitob"
        verbose_name_plural = "Kitoblar"
        ordering = ['-uploaded_at']
