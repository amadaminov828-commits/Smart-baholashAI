from django.urls import path
from .views import VehicleStatsView, RealEstateStatsView, GeneralStatsView

urlpatterns = [
    path('vehicles/', VehicleStatsView.as_view(), name='vehicle-stats'),
    path('real-estate/', RealEstateStatsView.as_view(), name='real-estate-stats'),
    path('general/', GeneralStatsView.as_view(), name='general-stats'),
]
