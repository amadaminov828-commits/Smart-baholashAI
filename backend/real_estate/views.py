import os
import re
import datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import RealEstateValuation, RealEstateAnalog
from reports.models import ReportDocument, QRCode
from .serializers import RealEstateValuationSerializer, RealEstateOCRUploadSerializer
from .ocr import extract_real_estate_info
from .scraper import search_real_estate_analogs
from django.core.files.storage import default_storage
from django.core.files import File
from vehicles.docx_generator import fill_docx_template
from vehicles.pdf_generator import convert_docx_to_pdf, protect_pdf
from reports.qr_generator import generate_qr_for_report

class RealEstateValuationViewSet(viewsets.ModelViewSet):
    serializer_class = RealEstateValuationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return RealEstateValuation.objects.none()
        
        if user.role == 'appraiser':
            # Appraisers see valuations assigned to them OR their own drafts
            from django.db.models import Q
            return RealEstateValuation.objects.filter(Q(assigned_to=user) | Q(user=user))
        
        return RealEstateValuation.objects.filter(user=user)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # LOGGING FOR DEBUG
        log_file = 'c:/Users/Asus/Desktop/antigravity/backend/ocr_live.log'
        def log_u(m):
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - PAYMENT_DEBUG: {m}\n")

        log_u(f"Update call for ID {instance.id}. Files: {list(request.FILES.keys())}. Data: {list(request.data.keys())}")

        # Check if a payment receipt is being uploaded
        receipt_uploaded = 'payment_receipt' in request.FILES
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # AUTO-APPROVAL for testing/development
        if receipt_uploaded:
            instance.refresh_from_db()
            if instance.payment_receipt:
                instance.status = 'approved'
                instance.paid_at = datetime.datetime.now()
                instance.save()
                log_u(f"AUTO-APPROVED Valuation {instance.id}")
                
                # Sync with ReportDocument
                try:
                    # Generate the final report if it doesn't exist or needs update
                    self._generate_re_report(request, instance)
                    
                    report = ReportDocument.objects.filter(object_id=instance.id, object_type='real_estate').order_by('-created_at').first()
                    if report:
                        report.status = 'approved'
                        report.save()
                        log_u(f"Synced ReportDocument {report.id} to APPROVED")
                except Exception as e:
                    log_u(f"Sync/Report Gen Error: {e}")
        
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        # Auto-healing: Ensure DB columns exist before saving
        from django.db import connection
        log_file = 'c:/Users/Asus/Desktop/antigravity/backend/ocr_live.log'
        def log_q(m):
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"DB_FIX: {m}\n")
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA table_info(real_estate_realestatevaluation)")
                cols = [row[1] for row in cursor.fetchall()]
                log_q(f"Current columns: {cols}")
                
                to_add = [
                    ("confirmed_fields", "TEXT DEFAULT '{}'"),
                    ("calculation_data", "TEXT DEFAULT '{}'"),
                    ("status", "VARCHAR(20) DEFAULT 'draft'"),
                    ("updated_at", "DATETIME DEFAULT '2024-01-01 00:00:00'"),
                ]
                for col_name, col_def in to_add:
                    if col_name not in cols:
                        log_q(f"Attempting to add: {col_name}")
                        cursor.execute(f"ALTER TABLE real_estate_realestatevaluation ADD COLUMN {col_name} {col_def}")
                        log_q(f"  -> Successfully added {col_name}")
        except Exception as e:
            log_q(f"Auto-migration error: {e}")
        
        try:
            serializer.save(user=self.request.user)
            log_q("Save successful")
        except Exception as e:
            log_q(f"Save FAILED: {e}")
            import traceback
            log_q(traceback.format_exc())
            raise e

    @action(detail=False, methods=['post'], url_path='ocr-upload')
    def ocr_upload(self, request):
        documents = request.FILES.getlist('documents')
        if not documents:
            return Response({"error": "No files provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        saved_paths = []
        try:
            # First, save all files to temporary storage
            for doc in documents:
                path = default_storage.save(doc.name, doc)
                full_path = default_storage.path(path)
                saved_paths.append((path, full_path))
            
            # Call OCR once with all files for better accuracy and context
            all_full_paths = [p[1] for p in saved_paths]
            extracted_data = extract_real_estate_info(all_full_paths)
            
        except Exception as e:
            import traceback
            print(f"OCR ERROR: {traceback.format_exc()}")
            return Response({"error": f"OCR failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            # Clean up all temporary files
            for path, full_path in saved_paths:
                if os.path.exists(full_path):
                    default_storage.delete(path)

        return Response({"extracted_data": extracted_data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='find-analogs')
    def find_analogs(self, request, pk=None):
        valuation = self.get_object()
        valuation.analogs.all().delete()

        try:
            analogs_data = search_real_estate_analogs(valuation.purpose, valuation.location)
            for data in analogs_data:
                # Ensure price is numeric
                if 'price' in data:
                    try:
                        data['price'] = float(data['price'])
                    except (ValueError, TypeError):
                        data['price'] = 0
                RealEstateAnalog.objects.create(valuation=valuation, **data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": f"Analoglarni qidirishda xato: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response({"message": f"{len(analogs_data)} analogs topildi"}, status=status.HTTP_200_OK)

    def _generate_re_report(self, request, valuation):
        import uuid
        import os
        import shutil
        import traceback
        from django.conf import settings
        from django.core.files import File
        from vehicles.docx_generator import fill_docx_template
        from vehicles.pdf_generator import convert_docx_to_pdf, protect_pdf
        from reports.models import ReportDocument, QRCode, ReportTemplate
        from reports.qr_generator import generate_qr_for_report
        from check_ip import get_local_ip

        template_id = request.data.get('template_id')
        template = None
        
        if template_id:
            try:
                template = ReportTemplate.objects.filter(id=template_id, object_type='real_estate').first()
            except (ValueError, TypeError):
                pass
                
        if not template:
            # Fallback to default or first available Real Estate template
            template = ReportTemplate.objects.filter(object_type='real_estate', is_default=True).first()
            if not template:
                template = ReportTemplate.objects.filter(object_type='real_estate').first()
                
        if not template:
            raise Exception("Real Estate shabloni topilmadi. Iltimos, shablon yuklang.")
            
        template_path = template.file.path
        temp_id = str(uuid.uuid4())[:8]
        request_dir = os.path.join(settings.MEDIA_ROOT, 'tmp', temp_id)
        os.makedirs(request_dir, exist_ok=True)
        
        import datetime
        now = valuation.created_at or datetime.datetime.now()
        months_uz = {
            1: "yanvar", 2: "fevral", 3: "mart", 4: "aprel", 5: "may", 6: "iyun",
            7: "iyul", 8: "avgust", 9: "sentabr", 10: "oktabr", 11: "noyabr", 12: "dekabr"
        }
        
        # Get calculations if they exist
        calc_data = valuation.calculation_data or {}
        ai_res = valuation.calculation_data.get('ai_results') if isinstance(valuation.calculation_data, dict) else None
        
        # Approaches values for the template
        cost_val = 0
        inc_val = 0
        comp_val = 0
        
        if ai_res:
            cost_val = ai_res.get('cost', {}).get('final_value', 0)
            inc_val = ai_res.get('income', {}).get('final_value', 0)
            comp_val = ai_res.get('comparative', {}).get('final_value', 0)
        
        # Determine final value based on selected method
        method = valuation.calculation_data.get('method', 'qiyosiy')
        final_value = comp_val
        if method == 'xarajat': final_value = cost_val
        elif method == 'daromad': final_value = inc_val
        
        from vehicles.views import number_to_uzbek_words
        final_value_words = (number_to_uzbek_words(int(final_value)) + " so'm").capitalize()

        def fmt(v):
            try: return f"{float(v):,.0f}".replace(',', ' ')
            except: return "0"

        context = {
            'FISH': valuation.owner_name or '',
            'KADASTR': valuation.cadastre_number or '',
            'AREA': valuation.total_area or '',
            'YEAR': valuation.built_year or '',
            'PURPOSE': valuation.get_purpose_display() or '',
            'LOCATION': valuation.location or '',
            'YIL': now.year,
            'OY': months_uz.get(now.month, ""),
            'KUN': now.day,
            'ID': valuation.id,
            'MANZIL': valuation.location or '',
            'NOMI': "Yakka tartibdagi turarjoy",
            'MAYDON': valuation.total_area or '',
            'PASPORT': valuation.passport_serial or '',
            'JSHSHIR': valuation.passport_jshshir or '',
            'BERILDI': valuation.passport_given_by or '',
            'SHARTNOMA': valuation.agreement_number or '',
            'SANA': valuation.agreement_date or '',
            'VILOYAT': valuation.region or '',
            'TUMAN': valuation.district or '',
            'valuation_date': now.strftime('%d.%m.%Y'),
            
            # Formatted Approaches for Template
            '{cost_final_val}': fmt(cost_val),
            '{inc_final_val}': fmt(inc_val),
            '{comp_final_val}': fmt(comp_val),
            '{final_market_value}': fmt(final_value),
            '{final_value_words}': final_value_words,
            
            # AI Details
            '{cost_repro}': fmt(ai_res.get('cost', {}).get('reproduction_cost', 0)) if ai_res else "0",
            '{cost_wear}': f"{ai_res.get('cost', {}).get('physical_wear_percent', 0):.1f}%" if ai_res else "0%",
            '{inc_noi}': fmt(ai_res.get('income', {}).get('noi', 0)) if ai_res else "0",
            
            'is_garov': valuation.purpose == 'garov',
            'is_nizom': valuation.purpose == 'nizom_fond',
            'is_invest': valuation.purpose == 'investitsion',
            'is_snos': valuation.purpose == 'snos',
            'is_approved': valuation.status == 'approved',
            'approver_name': valuation.assigned_to.get_full_name() if valuation.assigned_to else '',
            'show_seal': valuation.status == 'approved',
            'logo_path': r"c:\Users\Asus\Desktop\antigravity\frontend\public\logo.png",
            'signature_path': r"C:\Users\Asus\.gemini\antigravity\brain\7a9037ad-f581-46d1-a1a1-110f0a8bb8b9\ceo_signature_uzb_1774339172956.png" if valuation.status == 'approved' else None,
            'seal_path': r"C:\Users\Asus\.gemini\antigravity\brain\7a9037ad-f581-46d1-a1a1-110f0a8bb8b9\blue_seal_uzb_1774339159137.png" if valuation.status == 'approved' else None,
            
            # Legacy tags support
            '{{FISH}}': valuation.owner_name or '',
            '{{PASPORT}}': valuation.passport_serial or '',
            '{{JSHSHIR}}': valuation.passport_jshshir or '',
        }
        
        final_docx_path = os.path.join(request_dir, f're_report_{valuation.id}.docx')
        final_pdf_path = os.path.join(request_dir, f're_report_{valuation.id}.pdf')

        web_host = request.get_host()
        local_ip = get_local_ip()
        if 'localhost' in web_host or '127.0.0.1' in web_host:
            web_host = web_host.replace('localhost', local_ip).replace('127.0.0.1', local_ip)
        
        # Resolve protocol and host for verification QR code
        frontend_url = getattr(settings, 'FRONTEND_URL', '')
        site_url = getattr(settings, 'SITE_URL', '')
        
        if frontend_url:
            protocol = 'https' if frontend_url.startswith('https') else 'http'
            qr_host = frontend_url.replace('http://', '').replace('https://', '').rstrip('/')
        elif site_url:
            protocol = 'https' if site_url.startswith('https') else 'http'
            qr_host = site_url.replace('http://', '').replace('https://', '').rstrip('/')
        elif 'smartbaholash.uz' in web_host:
            protocol = 'https'
            qr_host = 'smartbaholash.uz'
        elif 'loca.lt' in web_host:
            protocol = 'https'
            qr_host = web_host
        else:
            protocol = 'http'
            qr_host = f"{local_ip}:3000"
            
        report = ReportDocument.objects.filter(object_id=valuation.id, object_type='real_estate').order_by('-created_at').first()
        if not report:
            report = ReportDocument.objects.create(
                object_id=valuation.id, object_type='real_estate',
                user=valuation.user, assigned_to=valuation.assigned_to
            )
        
        report.market_value = f"{final_value:,.0f} so'm".replace(',', ' ')
        report.save()
        
        verify_absolute_url = f"{protocol}://{qr_host}/verify/{report.id}"
        qr_file = generate_qr_for_report(report.id, verify_url=verify_absolute_url)
        qr_obj, _ = QRCode.objects.update_or_create(report=report, defaults={'code_image': qr_file})

        context['report_id_str'] = str(report.id)
        fill_docx_template(template_path, final_docx_path, context, qr_code_path=qr_obj.code_image.path)
        
        convert_docx_to_pdf(final_docx_path, final_pdf_path)
        protected_pdf = os.path.join(request_dir, f're_report_{valuation.id}_protected.pdf')
        protect_pdf(final_pdf_path, protected_pdf, password="admin")
        
        with open(protected_pdf if os.path.exists(protected_pdf) else final_pdf_path, 'rb') as f:
            report.file.save(f're_report_{report.id}_{temp_id}.pdf', File(f))
        
        try:
            docx_persist_dir = os.path.join(settings.MEDIA_ROOT, 'reports', 'docx')
            os.makedirs(docx_persist_dir, exist_ok=True)
            shutil.copy2(final_docx_path, os.path.join(docx_persist_dir, f'report_{report.id}.docx'))
        except Exception as e:
            print(f"DEBUG RE: Failed to persist DOCX: {e}")

        report.status = valuation.status # Mirror valuation status
        report.save()
        return report, qr_obj, web_host

    def pending(self, request):
        if request.user.role not in ['admin', 'appraiser']:
            return Response({'error': 'Ruxsat yo\'q'}, status=status.HTTP_403_FORBIDDEN)
            
        if request.user.role == 'admin':
            queryset = self.queryset.filter(status='pending')
        else:
            queryset = self.queryset.filter(status='pending', assigned_to=request.user)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='smart-stats')
    def get_smart_stats(self, request, pk=None):
        valuation = self.get_object()
        data = {
            "exchange_rates": {"USD": 12850.00, "EUR": 13920.00, "date": valuation.created_at.strftime('%d.%m.%Y')},
            "macro_stats": {"region": valuation.location or "Toshkent", "gdp_growth": "6.2%", "investment_growth": "12.4%", "inflation": "8.5%"}
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='search-analogs')
    def search_analogs(self, request, pk=None):
        from .scraper import search_real_estate_analogs
        valuation = self.get_object()
        
        # 1. Cadaster-based Region Mapping (The most accurate way)
        cad_map = {
            "10:01": "Toshkent shahri", "10:02": "Toshkent shahri", "10:03": "Toshkent shahri",
            "11:01": "Toshkent viloyati", "11:02": "Angren", "11:03": "Olmaliq", "11:04": "Chirchiq",
            "15:01": "Farg'ona", "15:02": "Marg'ilon", "15:03": "Quvasoy", "15:16": "Qo'qon",
            "15:15": "Uchko'prik", "15:12": "Farg'ona tumani",
            "16:01": "Namangan", "16:02": "Namangan",
            "14:01": "Andijon", "14:02": "Andijon",
            "13:01": "Samarqand", "13:02": "Samarqand",
            "17:01": "Buxoro", "17:02": "Kogon",
            "18:01": "Navoiy", "18:02": "Zarafshon",
            "19:01": "Qashqadaryo", "19:02": "Qarshi",
            "20:01": "Surxondaryo", "20:02": "Termiz",
            "21:01": "Jizzax", "22:01": "Sirdaryo", "23:01": "Xorazm", "24:01": "Nukus"
        }
        
        cad_num = valuation.cadastre_number or ""
        location_query = None
        
        # Extract prefix: e.g. "15:16:03..." -> "15:16"
        prefix_match = re.match(r'^(\d{2}:\d{2})', cad_num)
        if prefix_match:
            prefix = prefix_match.group(1)
            location_query = cad_map.get(prefix)
            
        # 2. Fallback to address extraction if cadaster is missing or not mapped
        if not location_query:
            full_loc = valuation.location or "Toshkent"
            # Cyrillic to Latin mapping for common city/region names
            cyr_map = {
                'тошкент': 'Toshkent', 'кукон': 'Qo\'qon', 'qoqon': 'Qo\'qon', 'андижон': 'Andijon',
                'наманган': 'Namangan', 'фаргона': 'Farg\'ona', 'бухоро': 'Buxoro', 'самарканд': 'Samarqand',
                'навоий': 'Navoiy', 'термиз': 'Termiz', 'карши': 'Qarshi', 'гулистон': 'Guliston',
                'жиззах': 'Jizzax', 'урganch': 'Urganch', 'нукус': 'Nukus'
            }
            # Remove common suffixes cleanly (both Latin and Cyrillic)
            clean_loc = re.sub(r'(?i)\b(?:viloyati|shahri|shahar|tumani|respublikasi|o\'zbekiston|вилояти|шахри|шахар|тумани|республикаси|узбекистон|MFY|qx)\b', '', full_loc)
            # Find the first city/region name (Cyrillic or Latin)
            parts = [p.strip() for p in clean_loc.split(',') if len(p.strip()) > 2]
            
            if parts:
                location_query = parts[0]
                # Check for Cyrillic match in transliteration map
                for cyr, lat in cyr_map.items():
                    if cyr in location_query.lower():
                        location_query = lat
                        break
                if len(parts) > 1 and location_query.lower() in ["ozbekiston", "respublikasi", "узбекистон", "республикаси"]:
                    location_query = parts[1]
                # If we have "Fargona" and "Qoqon", it's better to pick "Qoqon"
                if len(parts) >= 2 and location_query.lower() != "toshkent":
                    location_query = parts[1]
            else:
                location_query = "Toshkent"

        # 3. Check for existing saved analogs if we want to avoid re-scraping
        existing_analogs = valuation.analogs.all()
        if existing_analogs.exists() and not request.GET.get('refresh'):
            data = [{
                'rooms': a.rooms, 'area': a.area, 'price': a.price,
                'condition': a.condition, 'location': a.location,
                'url': a.url, 'date_posted': a.date_posted, 'source': a.source
            } for a in existing_analogs]
            return Response(data)

        try:
            # Query enhanced scraper (OLX + E-Auksion)
            analogs_data = search_real_estate_analogs(valuation.purpose, location_query)
            
            # Last resort: if nothing found even with cadaster, try "Toshkent"
            if not analogs_data and location_query != "Toshkent":
                analogs_data = search_real_estate_analogs(valuation.purpose, "Toshkent")

            if not analogs_data:
                return Response({
                    "error": f"Ushbu hudud ({location_query}) va uning yaqin atrofidan analoglar topilmadi.",
                    "analogs": []
                }, status=status.HTTP_404_NOT_FOUND)
                
            # Persistence: save analogs for future use
            from .models import RealEstateAnalog
            # Delete old analogs for this valuation
            valuation.analogs.all().delete()
            for a in analogs_data:
                RealEstateAnalog.objects.create(
                    valuation=valuation,
                    rooms=a.get('rooms', 3),
                    area=str(a.get('area', '')),
                    price=a.get('price', 0),
                    condition=a.get('condition', ''),
                    location=a.get('location', ''),
                    url=a.get('url', ''),
                    date_posted=a.get('date_posted', ''),
                    source=a.get('source', 'OLX')
                )
                
            return Response(analogs_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Analoglarni qidirishda xato: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='generate-report')
    def generate_report(self, request, pk=None):
        try:
            valuation = self.get_object()
            report, qr_obj, web_host = self._generate_re_report(request, valuation)
            
            scheme = request.scheme
            pdf_url = f"{scheme}://{web_host}{report.file.url}"
            
            return Response({
                "message": "Hisobot shakllandi", 
                "report_id": report.id,
                "status": valuation.status,
                "file_url": pdf_url, 
                "qr_image_url": request.build_absolute_uri(qr_obj.code_image.url)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='ai-calculate-approaches')
    def ai_calculate_approaches(self, request, pk=None):
        log_file = 'c:/Users/Asus/Desktop/antigravity/backend/ocr_live.log'
        def log_calc(m):
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - CALC_DEBUG: {m}\n")
        
        try:
            from .math_engine import RealEstateMathEngine
            import datetime
            valuation = self.get_object()
            log_calc(f"Starting calculation for ID {valuation.id}")
            
            # --- 1. Cost Approach (Xarajat) ---
            base_cost = float(request.data.get('base_cost', 4500000)) 
            area_vol = float(valuation.total_area or 100.0)
            indexation = float(request.data.get('indexation', 1.15)) 
            
            repro_cost = RealEstateMathEngine.calculate_reproduction_cost(base_cost, area_vol, indexation)
            
            try:
                const_year = int(valuation.built_year or 2010)
                actual_age = datetime.date.today().year - const_year
            except:
                actual_age = 10
            
            normative_life = float(request.data.get('normative_life', 100)) 
            physical_wear = RealEstateMathEngine.calculate_physical_wear(actual_age, normative_life)
            
            depreciated_cost = repro_cost * (1 - physical_wear/100.0)
            profit_rate = float(request.data.get('profit_rate', 0.15))
            final_cost_val = depreciated_cost * (1 + profit_rate) + float(request.data.get('land_value', 80000000))

            # --- 2. Income Approach (Daromad) ---
            unit_rent = float(request.data.get('unit_rent', 60000)) 
            inc_res = RealEstateMathEngine.calculate_income_value(
                unit_rent, area_vol, 
                vacancy_rate=float(request.data.get('vacancy_rate', 0.07)),
                opex_rate=float(request.data.get('opex_rate', 0.15)),
                cap_rate=float(request.data.get('cap_rate', 0.12))
            )

            # --- 3. Comparative Approach (Qiyosiy) ---
            base_price_m2 = float(request.data.get('base_price_m2', 8500000))
            adj_price = RealEstateMathEngine.calculate_comparative_adjustment(
                base_price_m2,
                location_adj=float(request.data.get('location_adj', 1.0)),
                repair_adj=float(request.data.get('repair_adj', 1.0)),
                floor_adj=float(request.data.get('floor_adj', 1.0))
            )

            results = {
                "cost": {
                    "reproduction_cost": repro_cost,
                    "physical_wear_percent": physical_wear,
                    "depreciated_cost": depreciated_cost,
                    "entrepreneurial_profit": depreciated_cost * profit_rate,
                    "final_value": final_cost_val,
                    "steps": [
                        f"Tiklanish qiymati: {repro_cost:,.0f} so'm",
                        f"Fizik eskirish ({actual_age} yil): {physical_wear:.1f}%",
                        f"Tadbirkorlik foydasi: {(depreciated_cost * profit_rate):,.0f} so'm",
                        f"Yakuniy qiymat: {final_cost_val:,.0f} so'm"
                    ]
                },
                "income": {
                    "pgi": inc_res['pgi'],
                    "egi": inc_res['egi'],
                    "noi": inc_res['noi'],
                    "final_value": inc_res['value'],
                    "steps": [
                        f"PGI (Yalpi): {inc_res['pgi']:,.0f} so'm",
                        f"NOI (Sof): {inc_res['noi']:,.0f} so'm",
                        f"Bozor qiymati: {inc_res['value']:,.0f} so'm"
                    ]
                },
                "comparative": {
                    "base_price_m2": base_price_m2,
                    "adjusted_price_m2": adj_price,
                    "final_value": adj_price * area_vol,
                    "steps": [
                        f"Baza m2: {base_price_m2:,.0f} so'm",
                        f"Tuzatishli m2: {adj_price:,.0f} so'm",
                        f"Jami qiymat: {(adj_price * area_vol):,.0f} so'm"
                    ]
                }
            }
            
            # Persistence
            valuation.calculation_data = results
            valuation.save()
            
            log_calc(f"Finished calculation for ID {valuation.id}")
            return Response(results, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            log_calc(f"Calculation error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        valuation = self.get_object()
        if not request.user.is_authenticated or (request.user.role not in ['super_admin', 'admin', 'appraiser']):
            return Response({'error': 'Faqat adminlar yoki baholovchilar tasdiqlashi mumkin'}, status=status.HTTP_403_FORBIDDEN)
            
        valuation.status = 'approved'
        import datetime
        valuation.paid_at = datetime.datetime.now()
        valuation.save()
        
        try:
            # Generate the final sealed report
            self._generate_re_report(request, valuation)
        except Exception as e:
            return Response({"error": f"Hisobotni yakunlashda xato: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response({'status': 'approved', 'message': 'Hisobot muvaffaqiyatli tasdiqlandi va muhrlandi'}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'], url_path='confirm-field')
    def confirm_field(self, request, pk=None):
        valuation = self.get_object()
        field_name = request.data.get('field_name')
        if not field_name: return Response({'error': 'Field name is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not valuation.confirmed_fields: valuation.confirmed_fields = {}
        valuation.confirmed_fields[field_name] = True
        valuation.save()
        return Response({'confirmed_fields': valuation.confirmed_fields}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='send-to-appraiser')
    def send_to_appraiser(self, request, pk=None):
        try:
            valuation = self.get_object()
            if not request.user.is_authenticated:
                return Response({'error': 'Avtorizatsiyadan o\'ting'}, status=status.HTTP_401_UNAUTHORIZED)
            
            if request.user.role != 'assistant':
                return Response({'error': 'Faqat yordamchilar jo\'natishi mumkin'}, status=status.HTTP_403_FORBIDDEN)
            
            if not request.user.assigned_appraiser:
                return Response({'error': 'Sizga rahbar biriktirilmagan'}, status=status.HTTP_400_BAD_REQUEST)
                
            valuation.status = 'pending'
            valuation.assigned_to = request.user.assigned_appraiser
            valuation.save()
            
            # Generate draft report
            self._generate_re_report(request, valuation)
            return Response({'message': 'Muvaffaqiyatli jo\'natildi'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def verify(self, request, pk=None):
        try:
            valuation = self.get_object()
            report = ReportDocument.objects.filter(object_id=valuation.id, object_type='real_estate').exclude(file='').order_by('-created_at').first()
            
            import datetime
            val_date = valuation.created_at.date()
            
            return Response({
                "status": "valid",
                "object": {
                    "cadastre": valuation.cadastre_number,
                    "location": valuation.location,
                    "owner": valuation.owner_name,
                },
                "valuation": {
                    "date": val_date.strftime('%d.%m.%Y'),
                    "id": valuation.id,
                    "report_id": report.id if report else None,
                },
                "verifier": "Smart Baholash Platformasi (AI-Powered)",
                "timestamp": datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Certificate not found or invalid"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='qr-pdf', permission_classes=[AllowAny])
    def qr_pdf(self, request, pk=None):
        from django.http import HttpResponseRedirect
        try:
            valuation = self.get_object()
            report = ReportDocument.objects.filter(object_id=valuation.id, object_type='real_estate').exclude(file='').order_by('-created_at').first()
            if not report or not report.file:
                return Response({"error": "PDF hisobot hozircha mavjud emas yoki ishlab chiqilmoqda."}, status=status.HTTP_404_NOT_FOUND)
            
            pdf_url = request.build_absolute_uri(report.file.url)
            return HttpResponseRedirect(pdf_url)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
