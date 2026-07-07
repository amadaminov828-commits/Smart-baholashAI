from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RealEstateValuationViewSet

router = DefaultRouter()
router.register(r'valuations', RealEstateValuationViewSet, basename='real-estate-valuation')

urlpatterns = [
    path('', include(router.urls)),
]
