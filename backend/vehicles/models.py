from django.db import models
from django.conf import settings

class VehicleValuation(models.Model):
    METHOD_CHOICES = (
        ('qiyosiy', 'Qiyosiy yondashuv'),
        ('xarajat', 'Xarajat yondashuvi'),
        ('daromad', 'Daromad yondashuvi'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehicle_valuations')
    
    # OCR dan olinadigan ma'lumotlar - Pasport
    owner_name = models.CharField(max_length=255, verbose_name="F.I.Sh", blank=True, null=True)
    passport_serial = models.CharField(max_length=20, verbose_name="Pasport seriya va raqami", blank=True, null=True)
    passport_type = models.CharField(max_length=100, verbose_name="Hujjat turi", default="O'zbekiston Respublikasi Fuqarosining ID-kartasi", blank=True, null=True)
    passport_given_date = models.CharField(max_length=50, verbose_name="Berilgan sanasi", blank=True, null=True)
    passport_birth_date = models.CharField(max_length=50, verbose_name="Tug'ilgan sanasi", blank=True, null=True)
    passport_given_by = models.CharField(max_length=255, verbose_name="Kim tomonidan berilgan", blank=True, null=True)
    passport_jshshir = models.CharField(max_length=50, verbose_name="JShShIR", blank=True, null=True)
    region = models.CharField(max_length=100, verbose_name="Viloyat", blank=True, null=True)
    district = models.CharField(max_length=100, verbose_name="Tuman", blank=True, null=True)

    # OCR dan olinadigan ma'lumotlar - Texpasport
    car_model = models.CharField(max_length=100, verbose_name="Avtomobil rusumi", blank=True, null=True)
    plate_number = models.CharField(max_length=20, verbose_name="Davlat raqami", blank=True, null=True)
    year = models.IntegerField(verbose_name="Ishlab chiqarilgan yili", blank=True, null=True)
    vin_code = models.CharField(max_length=50, verbose_name="VIN kod", blank=True, null=True)
    engine_capacity = models.CharField(max_length=50, verbose_name="Dvigatel hajmi", blank=True, null=True)
    tech_passport_owner = models.CharField(max_length=255, verbose_name="Tex-pasport egasi", blank=True, null=True)
    
    # Yangi qo'shilgan Texpasport maydonlari
    engine_number = models.CharField(max_length=100, verbose_name="Dvigatel raqami", blank=True, null=True)
    body_number = models.CharField(max_length=100, verbose_name="Kuzov asosi raqami", blank=True, null=True)
    color = models.CharField(max_length=50, verbose_name="Rangi", blank=True, null=True)
    vehicle_type = models.CharField(max_length=100, verbose_name="Transport turi", blank=True, null=True)
    full_weight = models.CharField(max_length=50, verbose_name="To'la vazni", blank=True, null=True)
    empty_weight = models.CharField(max_length=50, verbose_name="Yuksiz vazni", blank=True, null=True)
    fuel_type = models.CharField(max_length=50, verbose_name="Yoqilg'i turi", blank=True, null=True)
    seats_count = models.CharField(max_length=50, verbose_name="O'rindiqlar soni", blank=True, null=True)
    tech_passport_serial = models.CharField(max_length=50, verbose_name="Guvohnoma seriyasi va raqami", blank=True, null=True)
    
    # Jiddiy bo'lmagan nuqsonlar (9-band)
    has_faded_paint = models.BooleanField(default=False, verbose_name="Rang hiralashishi")
    has_stains = models.BooleanField(default=False, verbose_name="Dog'lar")
    has_corrosion = models.BooleanField(default=False, verbose_name="Kuzovda korroziya")
    
    # Foydalanish sharoitlari (10-band)
    has_creaking = models.BooleanField(default=False, verbose_name="Eshiklar/kapot g'irchillashi")
    has_insulation_issue = models.BooleanField(default=False, verbose_name="Izolyasiya buzilishi")
    
    # Kelishuv va baholash sanalari
    valuation_date = models.DateField(verbose_name="Baholash sanasi", blank=True, null=True)
    agreement_date = models.DateField(verbose_name="Shartnoma sanasi", blank=True, null=True)
    agreement_number = models.CharField(max_length=50, verbose_name="Shartnoma raqami", blank=True, null=True)
    report_number = models.CharField(max_length=50, verbose_name="Hisobot raqami", blank=True, null=True)
    
    # Yangi texnik va moliyaviy ma'lumotlar (VIII bo'lim)
    technical_condition = models.CharField(max_length=50, verbose_name="Texnik holati", default="Qoniqarli", blank=True, null=True)
    initial_balance_value = models.CharField(max_length=100, verbose_name="Dastlabki balans qiymati", blank=True, null=True)
    residual_balance_value = models.CharField(max_length=100, verbose_name="Balans qoldiq qiymati", blank=True, null=True)
    transmission_type = models.CharField(max_length=50, verbose_name="Yurish qutisi (KPP)", blank=True, null=True)
    top_speed = models.CharField(max_length=50, verbose_name="Maksimal tezlik", blank=True, null=True)
    engine_horsepower = models.CharField(max_length=50, verbose_name="Dvigatel quvvati (ot kuchi)", blank=True, null=True)
    mileage = models.CharField(max_length=50, verbose_name="Bosib o'tgan masofasi", blank=True, null=True)
    registration_number = models.CharField(max_length=100, verbose_name="Ro'yxatdan o'tkazish raqami", blank=True, null=True)
    
    # Client / Buyurtmachi fields
    client_type = models.CharField(max_length=20, default='physical', choices=(('physical', 'Jismoniy shaxs'), ('legal', 'Yuridik shaxs')), verbose_name="Buyurtmachi turi")
    client_company_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Kompaniya nomi")
    client_company_account = models.CharField(max_length=100, blank=True, null=True, verbose_name="Hisob raqami")
    client_company_inn = models.CharField(max_length=50, blank=True, null=True, verbose_name="INN")
    client_company_oked = models.CharField(max_length=50, blank=True, null=True, verbose_name="OKED")
    client_company_mfo = models.CharField(max_length=50, blank=True, null=True, verbose_name="MFO")
    client_company_bank = models.CharField(max_length=255, blank=True, null=True, verbose_name="Bank nomi")
    client_company_address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Kompaniya manzili")
    mulk_egasi_bir_xil = models.BooleanField(default=True, verbose_name="Mulk egasi buyurtmachi bilan bir xilmi")

    # Xarajat yondashuvi (Cost Approach) uchun maydonlar
    replacement_cost_usd = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Tiklanish qiymati (USD)", blank=True, null=True)
    act_wear_percent = models.FloatField(default=0.0, verbose_name="Dalolatnoma bo'yicha eskirish (%)")
    scale_wear_percent = models.FloatField(default=0.0, verbose_name="Shkala bo'yicha eskirish (%)")
    formula_wear_percent = models.FloatField(default=0.0, verbose_name="Formula bo'yicha eskirish (%)")
    aggregate_wear_percent = models.FloatField(default=0.0, verbose_name="Jamlangan eskirish (%)")
    
    STATUS_CHOICES = (
        ('draft', 'Qoralama'),
        ('payment_pending', 'To`lov kutilmoqda'),
        ('verifying', 'To`lov tekshirilmoqda'),
        ('approved', 'Tasdiqlangan'),
        ('rejected', 'Rad etilgan'),
    )
    
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Payment Fields
    payment_receipt = models.ImageField(upload_to="receipts/vehicles/", blank=True, null=True, verbose_name="To'lov cheki")
    price_amount = models.DecimalField(max_digits=12, decimal_places=2, default=100000.00, verbose_name="Baholash narxi")
    paid_at = models.DateTimeField(null=True, blank=True)
    
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_valuations', verbose_name="Biriktirilgan Baholovchi")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.car_model} - {self.plate_number}"

    class Meta:
        verbose_name = "Avtomobil baholash"
        verbose_name_plural = "Avtomobil baholashlari"


class VehicleAnalog(models.Model):
    valuation = models.ForeignKey(VehicleValuation, on_delete=models.CASCADE, related_name='analogs')
    source = models.CharField(max_length=50, default='OLX')
    model_name = models.CharField(max_length=100)
    year = models.IntegerField()
    engine_capacity = models.CharField(max_length=50)
    mileage = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    price_string = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(max_length=500, blank=True, null=True)
    date_posted = models.CharField(max_length=100, blank=True, null=True)
    
    # Yangi texnik maydonlar jadval uchun
    body_type = models.CharField(max_length=50, default="Sedan", blank=True, null=True)
    color = models.CharField(max_length=50, default="Oq", blank=True, null=True)
    transmission = models.CharField(max_length=50, default="Mexanika", blank=True, null=True)
    has_faded_paint = models.CharField(max_length=20, default="mavjud", blank=True, null=True)
    has_stains = models.CharField(max_length=20, default="mavjud", blank=True, null=True)
    has_corrosion = models.CharField(max_length=20, default="mavjud", blank=True, null=True)
    has_creaking = models.CharField(max_length=20, default="ma’lumot yo‘q", blank=True, null=True)
    has_insulation_issue = models.CharField(max_length=20, default="ma’lumot yo‘q", blank=True, null=True)

    # Professional tuzatishlar (Math Engine natijalari)
    wear_percent = models.FloatField(blank=True, null=True, verbose_name="Jismoniy eskirish %")
    wear_adjustment = models.FloatField(blank=True, null=True, verbose_name="Eskirishga tuzatish")
    weight = models.FloatField(blank=True, null=True, verbose_name="Vazni (Koeffisiyent)")
    adjusted_price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.model_name} - {self.price_string or self.price}"

    class Meta:
        verbose_name = "Avtomobil analogi"
        verbose_name_plural = "Avtomobil analoglari"


class PaymeTransaction(models.Model):
    transaction_id = models.CharField(max_length=255, unique=True)
    valuation = models.ForeignKey(VehicleValuation, on_delete=models.CASCADE, related_name='payme_transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    state = models.IntegerField(default=1) # 1: Created, 2: Performed, -1: Canceled after perform, -2: Canceled before perform
    create_time = models.BigIntegerField()
    perform_time = models.BigIntegerField(null=True, blank=True)
    cancel_time = models.BigIntegerField(null=True, blank=True)
    reason = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Payme Trans {self.transaction_id} - State {self.state}"

    class Meta:
        verbose_name = "Payme tranzaksiyasi"
        verbose_name_plural = "Payme tranzaksiyalari"


class GlobalAnalog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='saved_analogs')
    source = models.CharField(max_length=50, default='OLX')
    model_name = models.CharField(max_length=100)
    year = models.IntegerField()
    engine_capacity = models.CharField(max_length=50)
    mileage = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    price_string = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[Global] {self.model_name} ({self.year}) - {self.price_string or self.price}"

    class Meta:
        verbose_name = "Global analog"
        verbose_name_plural = "Global analoglar"


_CACHED_SETTINGS = {}

class SystemSetting(models.Model):
    key = models.CharField(max_length=100, unique=True, verbose_name="Sozlama kaliti")
    value = models.TextField(verbose_name="Sozlama qiymati")
    description = models.TextField(blank=True, null=True, verbose_name="Tavsif")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Tahrirlangan sana")

    def __str__(self):
        return f"{self.key} = {self.value[:30]}..."

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        global _CACHED_SETTINGS
        _CACHED_SETTINGS[self.key] = self.value.strip()

    def delete(self, *args, **kwargs):
        key = self.key
        super().delete(*args, **kwargs)
        global _CACHED_SETTINGS
        if key in _CACHED_SETTINGS:
            del _CACHED_SETTINGS[key]

    class Meta:
        verbose_name = "Tizim sozlamasi"
        verbose_name_plural = "Tizim sozlamalari"

def get_gemini_api_key():
    global _CACHED_SETTINGS
    if 'GEMINI_API_KEY' in _CACHED_SETTINGS:
        return _CACHED_SETTINGS['GEMINI_API_KEY']
    try:
        setting = SystemSetting.objects.filter(key='GEMINI_API_KEY').first()
        if setting and setting.value.strip():
            val = setting.value.strip()
            _CACHED_SETTINGS['GEMINI_API_KEY'] = val
            return val
    except Exception:
        pass
    import os
    env_key = os.getenv('GEMINI_API_KEY')
    if env_key:
        env_key = env_key.strip('"\' ')
        _CACHED_SETTINGS['GEMINI_API_KEY'] = env_key
        return env_key
    return None


