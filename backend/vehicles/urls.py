from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehicleValuationViewSet, VehicleAnalogViewSet, GlobalAnalogViewSet

router = DefaultRouter()
router.register(r'valuations', VehicleValuationViewSet, basename='vehicle-valuation')
router.register(r'analogs', VehicleAnalogViewSet, basename='vehicle-analog')
router.register(r'global-analogs', GlobalAnalogViewSet, basename='global-analog')

urlpatterns = [
    path('', include(router.urls)),
]

