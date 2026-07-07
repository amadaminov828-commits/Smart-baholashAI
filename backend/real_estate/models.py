from django.db import models
from django.conf import settings

class RealEstateValuation(models.Model):
    PURPOSE_CHOICES = (
        ('garov', 'Garov qiymati'),
        ('soliq', 'Soliq qiymati'),
        ('nizom_fond', 'Nizom fond qiymati'),
        ('investitsion', 'Investitsion qiymati'),
        ('snos', 'Snos va yetkazilgan zarar'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='real_estate_valuations')
    
    # OCR dan olinadigan ma'lumotlar
    owner_name = models.CharField(max_length=255, verbose_name="Mulk egasi", blank=True, null=True)
    cadastre_number = models.CharField(max_length=50, verbose_name="Kadastr raqami", blank=True, null=True)
    total_area = models.CharField(max_length=50, verbose_name="Umumiy maydon", blank=True, null=True)
    location = models.CharField(max_length=255, verbose_name="Joylashuv", blank=True, null=True)
    built_year = models.IntegerField(verbose_name="Qurilgan yili", blank=True, null=True)

    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, blank=True, null=True)
    STATUS_CHOICES = (
        ('draft', 'Qoralama'),
        ('payment_pending', 'To`lov kutilmoqda'),
        ('verifying', 'To`lov tekshirilmoqda'),
        ('approved', 'Tasdiqlangan'),
        ('rejected', 'Rad etilgan'),
    )

    # Identity fields
    passport_type = models.CharField(max_length=100, null=True, blank=True)
    passport_serial = models.CharField(max_length=20, null=True, blank=True)
    passport_jshshir = models.CharField(max_length=14, null=True, blank=True)
    passport_given_date = models.CharField(max_length=50, null=True, blank=True)
    passport_given_by = models.TextField(null=True, blank=True)
    
    # Regional data
    region = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    
    # Agreement fields
    agreement_number = models.CharField(max_length=100, null=True, blank=True)
    agreement_date = models.CharField(max_length=50, null=True, blank=True)

    # Status and Payment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Payment Fields
    payment_receipt = models.ImageField(upload_to="receipts/real_estate/", blank=True, null=True, verbose_name="To'lov cheki")
    price_amount = models.DecimalField(max_digits=12, decimal_places=2, default=150000.00, verbose_name="Baholash narxi")
    paid_at = models.DateTimeField(null=True, blank=True)

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_real_estate_valuations'
    )
    
    # Validation & Metadata
    confirmed_fields = models.JSONField(default=dict, blank=True) # {'owner_name': True, ...}
    calculation_data = models.JSONField(default=dict, blank=True) # {indices, multipliers, etc.}
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.cadastre_number} - {self.owner_name}"

    class Meta:
        verbose_name = "Ko'chmas mulk baholash"
        verbose_name_plural = "Ko'chmas mulk baholashlari"

class RealEstateAnalog(models.Model):
    valuation = models.ForeignKey(RealEstateValuation, on_delete=models.CASCADE, related_name='analogs')
    source = models.CharField(max_length=50, default='OLX')
    rooms = models.IntegerField(verbose_name="Xona soni")
    area = models.CharField(max_length=50, verbose_name="Maydon")
    condition = models.CharField(max_length=50, verbose_name="Holati", blank=True, null=True)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    location = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(max_length=500, blank=True, null=True)
    date_posted = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.rooms} xona - {self.price}"

    class Meta:
        verbose_name = "Ko'chmas mulk analogi"
        verbose_name_plural = "Ko'chmas mulk analoglari"
