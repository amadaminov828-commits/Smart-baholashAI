from django.contrib.auth.models import AbstractUser
from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=255, verbose_name="Firma nomi")
    stir = models.CharField(max_length=20, verbose_name="STIR raqami (INN)")
    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True, verbose_name="Firma Logotipi")
    seal = models.ImageField(upload_to="company_seals/", blank=True, null=True, verbose_name="Firma Muhri (Pechat)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Firma'
        verbose_name_plural = 'Firmalar'


class User(AbstractUser):
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin (Egasi)'),
        ('admin', 'Yordamchi Admin'),
        ('user', 'Foydalanuvchi'),
    )
    
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='users',
        verbose_name="Qaysi firmaga tegishli"
    )
    full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="FISH")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon raqam")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    license_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Sertifikat/Litsenziya raqami")
    pinfl = models.CharField(max_length=20, blank=True, null=True, verbose_name="PINFL")
    signature = models.ImageField(upload_to="user_signatures/", blank=True, null=True, verbose_name="Foydalanuvchi Imzosi")
    
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='created_users',
        verbose_name="Kim tomonidan yaratilgan"
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'
