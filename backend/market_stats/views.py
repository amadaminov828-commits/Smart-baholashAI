from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import traceback
import logging

logger = logging.getLogger(__name__)


class VehicleStatsView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        region = request.query_params.get('region')
        lang = request.query_params.get('lang', 'uz')
        try:
            from .scraper_utils import get_vehicle_stats
            data = get_vehicle_stats(region, lang=lang)
            return Response(data)
        except Exception as e:
            logger.error(f"Vehicle stats error: {traceback.format_exc()}")
            return Response({
                'categories': ["Yengil avtomobillar", "Yuk mashinalari", "Maxsus texnika", "Mototransport"],
                'top_models': [],
                'avg_price': 0,
                'new_listings': 0,
                'new_listings_details': [],
                'demand_index': 0,
                'regions': [],
                'archive_data': [],
                'last_updated': '',
                'data_source': 'Xatolik yuz berdi',
                'error': str(e),
            })


class RealEstateStatsView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        region = request.query_params.get('region')
        lang = request.query_params.get('lang', 'uz')
        try:
            from .scraper_utils import get_real_estate_stats
            data = get_real_estate_stats(region, lang=lang)
            return Response(data)
        except Exception as e:
            logger.error(f"RE stats error: {traceback.format_exc()}")
            return Response({
                'categories': ["Kvartiralar", "Hovli / Uy", "Yer uchastkalari", "Tijorat binolari"],
                'top_types': [],
                'avg_price_m2': 0,
                'new_listings': 0,
                'new_listings_details': [],
                'demand_index': 0,
                'regions': [],
                'archive_data': [],
                'last_updated': '',
                'data_source': 'Xatolik yuz berdi',
                'error': str(e),
            })


class GeneralStatsView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        lang = request.query_params.get('lang', 'uz')
        try:
            from .scraper_utils import get_vehicle_stats, get_real_estate_stats
            v_data = get_vehicle_stats(lang=lang)
            re_data = get_real_estate_stats(lang=lang)
            return Response({
                "vehicles": v_data,
                "real_estate": re_data,
            })
        except Exception as e:
            logger.error(f"General stats error: {traceback.format_exc()}")
            return Response({
                "error": str(e),
                "vehicles": {
                    'top_models': [], 'avg_price': 0, 'new_listings': 0,
                    'demand_index': 0, 'regions': [], 'archive_data': [],
                    'categories': [], 'category_details': {}, 'data_source': 'Xatolik',
                },
                "real_estate": {
                    'top_types': [], 'avg_price_m2': 0, 'new_listings': 0,
                    'demand_index': 0, 'regions': [], 'archive_data': [],
                    'categories': [], 'category_details': {}, 'data_source': 'Xatolik',
                },
            }, status=200)  # Always 200, never 500
