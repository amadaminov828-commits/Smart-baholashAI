from django.contrib import admin
from .models import RealEstateValuation, RealEstateAnalog

class RealEstateAnalogInline(admin.TabularInline):
    model = RealEstateAnalog
    extra = 1

class RealEstateValuationAdmin(admin.ModelAdmin):
    list_display = ('cadastre_number', 'owner_name', 'purpose', 'status', 'created_at')
    list_filter = ('status', 'purpose')
    search_fields = ('cadastre_number', 'owner_name', 'location')
    inlines = [RealEstateAnalogInline]

admin.site.register(RealEstateValuation, RealEstateValuationAdmin)
admin.site.register(RealEstateAnalog)
