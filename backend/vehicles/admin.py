from django.contrib import admin
from .models import VehicleValuation, VehicleAnalog, PaymeTransaction, SystemSetting

class VehicleAnalogInline(admin.TabularInline):
    model = VehicleAnalog
    extra = 1

class VehicleValuationAdmin(admin.ModelAdmin):
    list_display = ('car_model', 'plate_number', 'owner_name', 'status', 'created_at')
    list_filter = ('status', 'method')
    search_fields = ('car_model', 'plate_number', 'owner_name')
    inlines = [VehicleAnalogInline]

admin.site.register(VehicleValuation, VehicleValuationAdmin)
admin.site.register(VehicleAnalog)
admin.site.register(PaymeTransaction)
admin.site.register(SystemSetting)

