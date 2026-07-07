import os
import datetime
import requests
import concurrent.futures
import re
import socket
import time
import uuid
import traceback
from django.conf import settings
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import VehicleValuation, VehicleAnalog, GlobalAnalog
from reports.models import ReportDocument, QRCode
from .serializers import VehicleValuationSerializer, OCRDocumentUploadSerializer
from .ocr import extract_vehicle_info
from .scraper import search_analogs
from .docx_generator import fill_docx_template
from valuation_engine.vehicle_math import VehicleMathEngine
from .pdf_generator import convert_docx_to_pdf, protect_pdf
from reports.qr_generator import generate_qr_for_report
from check_ip import get_local_ip
from utils.date_utils import format_uzbek_date_long
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files import File
from utils.number_to_words import number_to_uzbek_words

# AI Client Initialization
from google import genai
api_key = os.getenv('GEMINI_API_KEY')
genai_client = None
if api_key:
    try:
        genai_client = genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Failed to initialize Gemini client in views: {e}", flush=True)


def format_fio(full_name):
    if not full_name: return ""
    parts = str(full_name).strip().split()
    if len(parts) >= 2:
        if parts[0].lower().endswith(('ov', 'ova', 'ev', 'eva', 'yev', 'yeva')):
            # Change from Familya Ism Otasining_ismi -> Ism Familya Otasining_ismi
            return f"{parts[1]} {parts[0]} " + " ".join(parts[2:])
    return full_name

def sanitize_fuel_type(val):
    if not val:
        return ""
    return str(val).strip()

def get_local_ip():
    """Helper to get local IP for QR codes when on localhost"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Use Google's public DNS to find the local interface IP that has internet/LAN route
        s.connect(('8.8.8.8', 80))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def log_view(msg):
    with open('c:/Users/Asus/Desktop/antigravity/backend/ocr_live.log', 'a', encoding='utf-8') as f:
        f.write(f"{datetime.datetime.now()} - {msg}\n")
    try:
        print(f"VIEW: {msg}", flush=True)
    except UnicodeEncodeError:
        try:
            print(f"VIEW: {str(msg).encode('ascii', 'replace').decode('ascii')}", flush=True)
        except:
            pass

class VehicleValuationViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleValuationSerializer
    queryset = VehicleValuation.objects.all() # Default queryset

    def get_queryset(self):
        # Allow all valuations for public/cross-user actions (QR verification, reports)
        public_actions = ['generate_report', 'verify', 'find_analogs', 'retrieve', 'export_word', 'export_pdf', 'qr_pdf', 'update', 'partial_update', 'send_to_appraiser']
        if str(self.action) in public_actions:
            return VehicleValuation.objects.all()
            
        # For standard actions, restrict to owner or assigned appraiser
        user = self.request.user if self.request.user.is_authenticated else None
        if user:
            from django.db.models import Q
            return VehicleValuation.objects.filter(Q(user=user) | Q(assigned_to=user))
            
        # Fallback to all for now as AllowAny is globally set on viewset
        return VehicleValuation.objects.all()
    
    def perform_create(self, serializer):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = self.request.user if self.request.user.is_authenticated else User.objects.first()
        serializer.save(user=user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Admin or assigned appraiser can update status to sensitive states
        if 'status' in request.data:
            new_status = request.data['status']
            if new_status != instance.status:
                # Sensitive status changes (Approved/Rejected) require admin/appraiser
                if new_status in ['approved', 'rejected']:
                    if not request.user.is_authenticated or (request.user.role not in ['admin', 'super_admin', 'appraiser']):
                        return Response({"error": "Sizda bu hisobot holatini tasdiqlash huquqi yo'q"}, status=status.HTTP_403_FORBIDDEN)
                
                # Payment-related status changes are allowed for the owner
                # (e.g. from draft to payment_pending, or to verifying when receipt is uploaded)
                if new_status in ['payment_pending', 'verifying']:
                    if not request.user.is_authenticated or (instance.user != request.user and request.user.role not in ['admin', 'super_admin']):
                        return Response({"error": "Sizda bu amalni bajarishga ruxsat yo'q"}, status=status.HTTP_403_FORBIDDEN)
                
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Check if a payment receipt is being uploaded
        receipt_uploaded = 'payment_receipt' in request.FILES
        
        save_kwargs = {}
        if 'status' in request.data and request.data['status'] in ['approved', 'rejected'] and getattr(request.user, 'role', '') == 'appraiser':
            save_kwargs['assigned_to'] = request.user
            
        serializer.save(**save_kwargs)

        # AUTO-APPROVAL: If a receipt is uploaded, instantly approve without admin check
        if receipt_uploaded:
            instance.refresh_from_db()
            if instance.payment_receipt:
                instance.status = 'approved'
                instance.paid_at = datetime.datetime.now()
                instance.save()
                print(f"AUTO-APPROVED (receipt uploaded) for Valuation {instance.id}", flush=True)

        # Synchronize ReportDocument status if status is approved/rejected
        if instance.status in ['approved', 'rejected']:
            new_status = instance.status
            try:
                from reports.models import ReportDocument
                report = ReportDocument.objects.filter(object_id=instance.id, object_type='vehicle').order_by('-created_at').first()
                if report:
                    if new_status == 'approved':
                        report.status = 'approved'
                        # Use first admin as fallback if auto-approved
                        report.assigned_to = request.user if request.user.is_authenticated else None
                        report.save()
                    elif new_status == 'rejected':
                        report.status = 'rejected'
                        report.assigned_to = request.user
                        report.save()
            except Exception as e:
                import traceback
                print(f"Failed to sync ReportDocument status in update(): {e}\n{traceback.format_exc()}", flush=True)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        # RE-SERIALIZE to get the 'approved' status in response immediately
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def verify_receipt_ai(self, image_path):
        """Uses Gemini Vision to verify payment receipt."""
        if not genai_client:
            return {"is_valid": False, "reason": "AI Client not initialized"}
        
        try:
            from PIL import Image
            img = Image.open(image_path)
            
            prompt = """Ushbu rasm to'lov cheki (receipt) ekanligini va undagi ma'lumotlarni tekshiring:
1. Holati (Status): Muvaffaqiyatli, O'tkazildi yoki bajarildi (Success).
2. Summa: 100 000 so'm (yoki shunga yaqin 100,000).
3. Qabul qiluvchi: Eshonov Nodirbek (yoki karta raqami 9860123456789012 ga mos kelishi).
4. Sana: Bugungi sana (2026-yil May oyi) atrofida.

Faqat JSON formatida javob bering: {"is_valid": true/false, "confidence": 0-100, "reason": "sababi"}"""

            response = genai_client.models.generate_content(
                model='gemini-2.0-flash',
                contents=[prompt, img],
                config={
                    'response_mime_type': 'application/json',
                }
            )
            
            import json
            return json.loads(response.text)
        except Exception as e:
            print(f"AI Verification Traceback: {e}")
            return {"is_valid": False, "reason": str(e)}

    @action(detail=False, methods=['post'], url_path='ocr-upload')
    def ocr_upload(self, request):
        log_view("ocr_upload hit!")
        documents = request.FILES.getlist('documents')
        log_view(f"Received {len(documents)} document(s).")
        if not documents:
            return Response({"error": "No files provided"}, status=status.HTTP_400_BAD_REQUEST)
        extracted_data = {}
        paths_to_delete = []
        try:
            full_paths = []
            for doc in documents:
                log_view(f"Saving doc {doc.name} (size: {doc.size})...")
                # Use unique names to avoid collisions in parallel processing
                filename = f"ocr_{uuid.uuid4().hex[:8]}_{doc.name}"
                path = default_storage.save(filename, doc)
                full_paths.append(default_storage.path(path))
                paths_to_delete.append(path)
            
            # Process all images together in ONE Gemini call for 100% context and accuracy
            ocr_result = extract_vehicle_info(full_paths)
            extracted_data = ocr_result.get("extracted_data", {})
            flagged_fields = ocr_result.get("flagged_fields", [])
            
            # Ensure 'year' is formatted correctly for Django's IntegerField
            if extracted_data.get('year'):
                try:
                    year_val = str(extracted_data['year']).strip()
                    digits = re.sub(r'\D', '', year_val)
                    if len(digits) == 4:
                        extracted_data['year'] = int(digits)
                    else:
                        extracted_data['year'] = None
                except:
                    extracted_data['year'] = None
            else:
                extracted_data['year'] = None
            
            # No workaround needed anymore as report_number exists in models.py
            
            # No logic here, just clear images
            for p in paths_to_delete:
                try: default_storage.delete(p)
                except: pass
                
            return Response({
                "extracted_data": extracted_data,
                "flagged_fields": flagged_fields
            }, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='get-standard-specs')
    def get_standard_specs(self, request):
        model_name = request.query_params.get('model', '').strip()
        if not model_name:
            return Response({"error": "Model query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        from .specs_catalog import VEHICLE_SPECS_CATALOG
        from .ocr import get_global_vehicle_specs, log_ocr
        
        model_upper = model_name.upper()
        
        # Try local catalog
        matched_spec = None
        for k, spec in VEHICLE_SPECS_CATALOG.items():
            if k in model_upper:
                matched_spec = spec.copy()
                log_ocr(f"API Specs: matched standard specs locally for model keyword '{k}'")
                break
                
        # Try dynamic global lookup if not matched
        if not matched_spec:
            log_ocr(f"API Specs: no local match for '{model_name}', invoking dynamic global VLM catalog fallback...")
            dynamic_specs = get_global_vehicle_specs(model_name)
            if dynamic_specs:
                matched_spec = dynamic_specs
                
        if not matched_spec:
            # Safe defaults if lookup completely fails
            matched_spec = {
                "engine_capacity": 1500,
                "engine_horsepower": 100,
                "seats_count": 5,
                "empty_weight": 1200,
                "full_weight": 1700,
                "fuel_type": "Benzin"
            }
            
        return Response(matched_spec, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='find-analogs')
    def find_analogs(self, request, pk=None):
        try:
            valuation = self.get_object()
            method = request.data.get('method', 'qiyosiy')
            valuation.method = method
            valuation.save()
            valuation.analogs.all().delete()
            
            # Check for comparative cache
            cached_valuation = None
            force_refresh = request.data.get('refresh', False)
            
            if not force_refresh and valuation.car_model and valuation.year:
                # Find a recent valuation of the exact same model and year that has at least 3 analogs
                candidates = VehicleValuation.objects.filter(
                    car_model__iexact=valuation.car_model.strip(),
                    year=valuation.year
                ).exclude(id=valuation.id).order_by('-created_at')
                
                for candidate in candidates:
                    if candidate.analogs.count() >= 3:
                        cached_valuation = candidate
                        break
            
            if cached_valuation:
                print(f"CACHE HIT: Copying analogs from Valuation {cached_valuation.id} for model '{valuation.car_model}' ({valuation.year})")
                created_count = 0
                for analog in cached_valuation.analogs.all()[:3]:
                    VehicleAnalog.objects.create(
                        valuation=valuation,
                        source=analog.source,
                        model_name=analog.model_name,
                        year=analog.year,
                        engine_capacity=analog.engine_capacity,
                        mileage=analog.mileage,
                        price=analog.price,
                        price_string=analog.price_string,
                        location=analog.location,
                        url=analog.url,
                        date_posted=analog.date_posted,
                        body_type=analog.body_type,
                        color=analog.color,
                        transmission=analog.transmission,
                        has_faded_paint=analog.has_faded_paint,
                        has_stains=analog.has_stains,
                        has_corrosion=analog.has_corrosion,
                        has_creaking=analog.has_creaking,
                        has_insulation_issue=analog.has_insulation_issue,
                        wear_percent=analog.wear_percent,
                        wear_adjustment=analog.wear_adjustment,
                        weight=analog.weight,
                        adjusted_price=analog.adjusted_price
                    )
                    created_count += 1
                    # Save to global catalog
                    GlobalAnalog.objects.get_or_create(
                        model_name=analog.model_name,
                        year=analog.year,
                        engine_capacity=analog.engine_capacity,
                        mileage=analog.mileage,
                        price=analog.price,
                        defaults={
                            'source': analog.source,
                            'price_string': analog.price_string,
                            'location': analog.location,
                            'url': analog.url,
                            'user': valuation.user
                        }
                    )
                return Response({
                    "message": f"{created_count} analogs saqlandi (keshdan yuklandi)",
                    "cached": True,
                    "cached_from_id": cached_valuation.id
                }, status=status.HTTP_200_OK)
            
            # Fetch current USD rate for accurate conversion
            usd_rate = 12600.0
            try:
                today_str = datetime.date.today().strftime('%Y-%m-%d')
                cbu_res = requests.get(f'https://cbu.uz/uz/arkhiv-kursov-valyut/json/all/{today_str}/', timeout=1.5)
                if cbu_res.status_code == 200:
                    data = cbu_res.json()
                    for currency in data:
                        if currency['Ccy'] == 'USD': usd_rate = float(currency['Rate'])
            except Exception as e: 
                print(f"CBU API Error: {e}")

            print(f"Searching analogs for {valuation.car_model} ({valuation.year}) at rate {usd_rate}")
            analogs_data = search_analogs(valuation.car_model, valuation.year, usd_rate=usd_rate)
            
            created_count = 0
            # Ensure we only take the first 3 unique analogs
            for data in analogs_data[:3]:
                try:
                    VehicleAnalog.objects.create(valuation=valuation, **data)
                    created_count += 1
                    # Save to global catalog as well
                    GlobalAnalog.objects.get_or_create(
                        model_name=data.get('model_name'),
                        year=data.get('year'),
                        engine_capacity=data.get('engine_capacity'),
                        mileage=data.get('mileage'),
                        price=data.get('price'),
                        defaults={
                            'source': data.get('source', 'OLX'),
                            'price_string': data.get('price_string'),
                            'location': data.get('location'),
                            'url': data.get('url'),
                            'user': valuation.user
                        }
                    )
                except Exception as db_e:
                    print(f"Error creating analog: {db_e} for data: {data}")
                    
            return Response({"message": f"{created_count} analogs saqlandi"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Find Analogs Critical Error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='sms-webhook', permission_classes=[AllowAny])
    def sms_webhook(self, request):
        """
        Receives SMS notifications from an Android forwarder app.
        Example SMS: "Karta 9860..1234 ga 100000.00 so'm tushdi. Kod: 12345"
        """
        # 1. Security Check
        secret_token = request.headers.get('X-SMS-Secret')
        if secret_token != "smart_baholash_2026_secure":
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        sms_text = request.data.get('text', '')
        sender = request.data.get('sender', '')
        
        log_view(f"SMS Received from {sender}: {sms_text}")

        # 2. Extract Amount using Regex
        # Matches: 100000, 100 000, 100,000, 100000.00
        amount_match = re.search(r'(\d[\d\s,.]*)\s*(so\'m|uzs|sum)', sms_text.lower())
        if not amount_match:
            return Response({"status": "ignored", "reason": "No amount found"}, status=status.HTTP_200_OK)

        amount_str = amount_match.group(1).replace(' ', '').replace(',', '')
        try:
            # Handle possible trailing dot from cents
            amount = float(amount_str)
        except ValueError:
            return Response({"status": "ignored", "reason": "Invalid amount format"}, status=status.HTTP_200_OK)

        # 3. Match with Pending Valuations
        # We look for valuations in 'verifying' state with matching amount
        # created/updated within the last 15 minutes
        time_threshold = datetime.datetime.now() - datetime.timedelta(minutes=120) # 2 hours
        
        valuation = VehicleValuation.objects.filter(
            status='verifying',
            price_amount=amount,
            created_at__gte=time_threshold
        ).order_by('-created_at').first()

        if valuation:
            valuation.status = 'approved'
            valuation.paid_at = datetime.datetime.now()
            valuation.save()
            
            # Sync with ReportDocument
            from reports.models import ReportDocument
            rd = ReportDocument.objects.filter(object_id=valuation.id, object_type='vehicle').order_by('-created_at').first()
            if rd:
                rd.status = 'approved'
                rd.save()
                
            log_view(f"AUTO-APPROVED via SMS: Valuation {valuation.id} for {amount} UZS")
            return Response({"status": "approved", "id": valuation.id}, status=status.HTTP_200_OK)

        return Response({"status": "matched_none", "amount": amount}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='click-webhook', permission_classes=[AllowAny])
    def click_webhook(self, request):
        """
        Click integration Webhook
        Matches standard Click billing protocol.
        """
        import hashlib
        data = request.data
        
        # Click usually sends data as post parameters (form data or json)
        click_trans_id = data.get('click_trans_id')
        service_id = data.get('service_id')
        click_paydoc_id = data.get('click_paydoc_id')
        merchant_trans_id = data.get('merchant_trans_id')
        amount = data.get('amount')
        action = data.get('action')
        error = data.get('error')
        error_note = data.get('error_note')
        sign_time = data.get('sign_time')
        sign_string = data.get('sign_string')
        
        # Fallback to POST form parameters if JSON fields are empty
        if not click_trans_id:
            click_trans_id = request.POST.get('click_trans_id')
            service_id = request.POST.get('service_id')
            click_paydoc_id = request.POST.get('click_paydoc_id')
            merchant_trans_id = request.POST.get('merchant_trans_id')
            amount = request.POST.get('amount')
            action = request.POST.get('action')
            error = request.POST.get('error')
            error_note = request.POST.get('error_note')
            sign_time = request.POST.get('sign_time')
            sign_string = request.POST.get('sign_string')

        log_view(f"Click Webhook received: action={action}, trans={click_trans_id}, val={merchant_trans_id}, amount={amount}")

        # Basic validations
        if not all([click_trans_id, service_id, merchant_trans_id, amount, action, sign_time, sign_string]):
            return Response({
                "error": -8,
                "error_note": "Not enough parameters"
            }, status=status.HTTP_200_OK)

        # Signature Verification
        secret_key = getattr(settings, 'CLICK_SECRET_KEY', 'click_test_secret')
        
        try:
            action_int = int(action)
            click_trans_id_int = int(click_trans_id)
            service_id_int = int(service_id)
            amount_val = float(amount)
        except ValueError:
            return Response({
                "error": -2,
                "error_note": "Incorrect parameter amount or action"
            }, status=status.HTTP_200_OK)

        if action_int == 1:
            raw_sign = f"{click_trans_id}{service_id}{secret_key}{merchant_trans_id}{amount}{action}{sign_time}"
        elif action_int == 2:
            merchant_prepare_id = data.get('merchant_prepare_id') or request.POST.get('merchant_prepare_id') or merchant_trans_id
            raw_sign = f"{click_trans_id}{service_id}{secret_key}{merchant_trans_id}{merchant_prepare_id}{amount}{action}{sign_time}"
        else:
            return Response({
                "error": -3,
                "error_note": "Action not found"
            }, status=status.HTTP_200_OK)

        computed_sign = hashlib.md5(raw_sign.encode('utf-8')).hexdigest()

        if computed_sign != sign_string:
            log_view(f"Click Sign check failed! Computed: {computed_sign}, Received: {sign_string}")
            return Response({
                "error": -1,
                "error_note": "Sign string is incorrect"
            }, status=status.HTTP_200_OK)

        # Fetch Valuation
        try:
            valuation = VehicleValuation.objects.get(id=merchant_trans_id)
        except VehicleValuation.DoesNotExist:
            return Response({
                "error": -5,
                "error_note": "User does not exist (Valuation not found)"
            }, status=status.HTTP_200_OK)

        # Check Amount
        if abs(float(valuation.price_amount) - amount_val) > 0.01:
            return Response({
                "error": -2,
                "error_note": "Incorrect parameter amount"
            }, status=status.HTTP_200_OK)

        # Handle Actions
        if action_int == 1:
            if valuation.status == 'approved':
                return Response({
                    "click_trans_id": click_trans_id_int,
                    "merchant_trans_id": merchant_trans_id,
                    "merchant_prepare_id": merchant_trans_id,
                    "error": -4,
                    "error_note": "Transaction already complete"
                }, status=status.HTTP_200_OK)
            
            return Response({
                "click_trans_id": click_trans_id_int,
                "merchant_trans_id": merchant_trans_id,
                "merchant_prepare_id": merchant_trans_id,
                "error": 0,
                "error_note": "Prepare success"
            }, status=status.HTTP_200_OK)

        elif action_int == 2:
            if valuation.status == 'approved':
                return Response({
                    "click_trans_id": click_trans_id_int,
                    "merchant_trans_id": merchant_trans_id,
                    "merchant_confirm_id": merchant_trans_id,
                    "error": 0,
                    "error_note": "Already completed"
                }, status=status.HTTP_200_OK)
            
            valuation.status = 'approved'
            valuation.paid_at = datetime.datetime.now()
            valuation.save()
            
            # Sync with ReportDocument
            from reports.models import ReportDocument
            rd = ReportDocument.objects.filter(object_id=valuation.id, object_type='vehicle').order_by('-created_at').first()
            if rd:
                rd.status = 'approved'
                rd.save()
                
            log_view(f"AUTO-APPROVED via Click Webhook: Valuation {valuation.id} paid.")
            
            return Response({
                "click_trans_id": click_trans_id_int,
                "merchant_trans_id": merchant_trans_id,
                "merchant_confirm_id": merchant_trans_id,
                "error": 0,
                "error_note": "Success"
            }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='payme-webhook', permission_classes=[AllowAny])
    def payme_webhook(self, request):
        """
        Payme JSON-RPC 2.0 Webhook integration.
        Matches Payme merchant API specifications.
        """
        import base64
        from .models import PaymeTransaction
        
        body = request.data
        rpc_id = body.get('id')
        method = body.get('method')
        params = body.get('params', {})
        
        log_view(f"Payme Webhook received: method={method}, id={rpc_id}")
        
        def rpc_error(code, message_uz, message_ru, data_field=None):
            return Response({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "error": {
                    "code": code,
                    "message": {
                        "uz": message_uz,
                        "ru": message_ru
                    },
                    "data": data_field
                }
            }, status=status.HTTP_200_OK)

        def rpc_success(result):
            return Response({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": result
            }, status=status.HTTP_200_OK)

        if method == "CheckPerformTransaction":
            amount = params.get('amount')
            account = params.get('account', {})
            valuation_id = account.get('valuation_id')
            
            if not valuation_id:
                return rpc_error(-31001, "Arizalar topilmadi", "Заявка не найдена", "valuation_id")
                
            try:
                valuation = VehicleValuation.objects.get(id=valuation_id)
            except VehicleValuation.DoesNotExist:
                return rpc_error(-31001, "Arizalar topilmadi", "Заявка не найдена", "valuation_id")
                
            expected_amount_tiyin = int(float(valuation.price_amount) * 100)
            if int(amount) != expected_amount_tiyin:
                return rpc_error(-31008, "Noto'g'ri to'lov summasi", "Неверная сумма платежа", "amount")
                
            if valuation.status == 'approved':
                return rpc_error(-31007, "Hisobot allaqachon tasdiqlangan", "Заявка уже оплачена")
                
            return rpc_success({"allow": True})

        elif method == "CreateTransaction":
            trans_id = params.get('id')
            time_ms = params.get('time')
            amount = params.get('amount')
            account = params.get('account', {})
            valuation_id = account.get('valuation_id')
            
            if not valuation_id:
                return rpc_error(-31001, "Arizalar topilmadi", "Заявка не найдена", "valuation_id")
                
            try:
                valuation = VehicleValuation.objects.get(id=valuation_id)
            except VehicleValuation.DoesNotExist:
                return rpc_error(-31001, "Arizalar topilmadi", "Заявка не найдена", "valuation_id")
                
            expected_amount_tiyin = int(float(valuation.price_amount) * 100)
            if int(amount) != expected_amount_tiyin:
                return rpc_error(-31008, "Noto'g'ri to'lov summasi", "Неверная сумма платежа", "amount")
                
            try:
                existing = PaymeTransaction.objects.get(transaction_id=trans_id)
                if existing.state != 1:
                    return rpc_error(-31007, "Tranzaksiya holati noto'g'ri", "Неверное состояние транзакции")
                return rpc_success({
                    "create_time": existing.create_time,
                    "transaction": str(existing.id),
                    "state": 1
                })
            except PaymeTransaction.DoesNotExist:
                pass
                
            active_trans = PaymeTransaction.objects.filter(valuation=valuation, state=1).first()
            if active_trans:
                return rpc_error(-31007, "Boshqa faol tranzaksiya mavjud", "Имеется другая активная транзакция")
                
            new_trans = PaymeTransaction.objects.create(
                transaction_id=trans_id,
                valuation=valuation,
                amount=float(amount) / 100.0,
                state=1,
                create_time=time_ms
            )
            return rpc_success({
                "create_time": new_trans.create_time,
                "transaction": str(new_trans.id),
                "state": 1
            })

        elif method == "PerformTransaction":
            trans_id = params.get('id')
            try:
                trans = PaymeTransaction.objects.get(transaction_id=trans_id)
            except PaymeTransaction.DoesNotExist:
                return rpc_error(-31050, "Tranzaksiya topilmadi", "Транзакция не найдена")
                
            if trans.state == 1:
                now_ms = int(time.time() * 1000)
                trans.state = 2
                trans.perform_time = now_ms
                trans.save()
                
                val = trans.valuation
                val.status = 'approved'
                val.paid_at = datetime.datetime.now()
                val.save()
                
                from reports.models import ReportDocument
                rd = ReportDocument.objects.filter(object_id=val.id, object_type='vehicle').order_by('-created_at').first()
                if rd:
                    rd.status = 'approved'
                    rd.save()
                    
                log_view(f"AUTO-APPROVED via Payme Webhook: Valuation {val.id} paid. Trans ID {trans_id}")
                return rpc_success({
                    "transaction": str(trans.id),
                    "perform_time": trans.perform_time,
                    "state": 2
                })
            elif trans.state == 2:
                return rpc_success({
                    "transaction": str(trans.id),
                    "perform_time": trans.perform_time,
                    "state": 2
                })
            else:
                return rpc_error(-31008, "Tranzaksiya holati noto'g'ri", "Неверное состояние транзакции")

        elif method == "CancelTransaction":
            trans_id = params.get('id')
            reason = params.get('reason')
            try:
                trans = PaymeTransaction.objects.get(transaction_id=trans_id)
            except PaymeTransaction.DoesNotExist:
                return rpc_error(-31050, "Tranzaksiya topilmadi", "Транзакция не найдена")
                
            now_ms = int(time.time() * 1000)
            if trans.state == 1:
                trans.state = -1
                trans.cancel_time = now_ms
                trans.reason = reason
                trans.save()
                return rpc_success({
                    "transaction": str(trans.id),
                    "cancel_time": trans.cancel_time,
                    "state": -1
                })
            elif trans.state == 2:
                trans.state = -2
                trans.cancel_time = now_ms
                trans.reason = reason
                trans.save()
                
                val = trans.valuation
                val.status = 'payment_pending'
                val.save()
                
                from reports.models import ReportDocument
                rd = ReportDocument.objects.filter(object_id=val.id, object_type='vehicle').order_by('-created_at').first()
                if rd:
                    rd.status = 'payment_pending'
                    rd.save()
                    
                return rpc_success({
                    "transaction": str(trans.id),
                    "cancel_time": trans.cancel_time,
                    "state": -2
                })
            else:
                return rpc_success({
                    "transaction": str(trans.id),
                    "cancel_time": trans.cancel_time,
                    "state": trans.state
                })

        elif method == "CheckTransaction":
            trans_id = params.get('id')
            try:
                trans = PaymeTransaction.objects.get(transaction_id=trans_id)
            except PaymeTransaction.DoesNotExist:
                return rpc_error(-31050, "Tranzaksiya topilmadi", "Транзакция не найдена")
                
            return rpc_success({
                "create_time": trans.create_time,
                "perform_time": trans.perform_time or 0,
                "cancel_time": trans.cancel_time or 0,
                "transaction": str(trans.id),
                "state": trans.state,
                "reason": trans.reason or None
            })

        elif method == "GetStatement":
            from_time = params.get('from')
            to_time = params.get('to')
            txs = PaymeTransaction.objects.filter(create_time__gte=from_time, create_time__lte=to_time)
            transactions_list = []
            for tx in txs:
                transactions_list.append({
                    "id": tx.transaction_id,
                    "time": tx.create_time,
                    "amount": int(tx.amount * 100),
                    "account": {
                        "valuation_id": str(tx.valuation.id)
                    },
                    "create_time": tx.create_time,
                    "perform_time": tx.perform_time or 0,
                    "cancel_time": tx.cancel_time or 0,
                    "transaction": str(tx.id),
                    "state": tx.state,
                    "reason": tx.reason or None
                })
            return rpc_success({"transactions": transactions_list})

        return rpc_error(-32601, "Metod topilmadi", "Метод не найден")

    @action(detail=True, methods=['post'], url_path='simulate-payment', permission_classes=[AllowAny])
    def simulate_payment(self, request, pk=None):
        """
        Simulates Click or Payme webhook transaction sequence internally.
        Allows immediate sandbox payment testing without third-party tools.
        """
        try:
            valuation = self.get_object()
            gateway = request.data.get('gateway', 'click')
            
            import datetime
            import time
            import hashlib
            from django.conf import settings
            
            amount = float(valuation.price_amount)
            
            if gateway == 'click':
                # Mark valuation as approved (paid)
                valuation.status = 'approved'
                valuation.paid_at = datetime.datetime.now()
                valuation.save()
                
                # Sync with ReportDocument
                from reports.models import ReportDocument
                rd = ReportDocument.objects.filter(object_id=valuation.id, object_type='vehicle').order_by('-created_at').first()
                if rd:
                    rd.status = 'approved'
                    rd.save()
                    
                log_view(f"SIMULATED CLICK PAYMENT SUCCESS: Valuation {valuation.id}")
                return Response({"status": "approved", "message": "Click to'lovi muvaffaqiyatli simulyatsiya qilindi!"}, status=status.HTTP_200_OK)
                
            elif gateway == 'payme':
                # Simulate Payme transaction perform
                valuation.status = 'approved'
                valuation.paid_at = datetime.datetime.now()
                valuation.save()
                
                # Sync with ReportDocument
                from reports.models import ReportDocument
                rd = ReportDocument.objects.filter(object_id=valuation.id, object_type='vehicle').order_by('-created_at').first()
                if rd:
                    rd.status = 'approved'
                    rd.save()
                    
                log_view(f"SIMULATED PAYME PAYMENT SUCCESS: Valuation {valuation.id}")
                return Response({"status": "approved", "message": "Payme to'lovi muvaffaqiyatli simulyatsiya qilindi!"}, status=status.HTTP_200_OK)
                
            return Response({"error": "Noma'lum to'lov tizimi"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        try:
            valuation = self.get_object()
            if not request.user.is_authenticated or (request.user.role not in ['super_admin', 'admin']):
                return Response({'error': 'Ruxsat yo\'q'}, status=status.HTTP_403_FORBIDDEN)
            
            valuation.status = 'approved'
            import datetime
            valuation.paid_at = datetime.datetime.now()
            valuation.save()
            
            # Sync with ReportDocument
            from reports.models import ReportDocument
            rd = ReportDocument.objects.filter(object_id=valuation.id, object_type='vehicle').order_by('-created_at').first()
            if rd:
                rd.status = 'approved'
                rd.save()
                
            return Response({'message': 'To\'lov va hisobot tasdiqlandi'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='send-to-appraiser')

    def send_to_appraiser(self, request, pk=None):
        try:
            valuation = self.get_object()
            if not request.user.is_authenticated:
                return Response({'error': 'Avtorizatsiyadan o\'ting'}, status=status.HTTP_401_UNAUTHORIZED)
            
            if request.user.role != 'assistant':
                return Response({'error': 'Faqat yordamchi baholovchilar jo\'natishi mumkin'}, status=status.HTTP_403_FORBIDDEN)
            
            if not request.user.assigned_appraiser:
                return Response({'error': 'Sizga rahbar baholovchi biriktirilmagan'}, status=status.HTTP_400_BAD_REQUEST)
                
            valuation.status = 'pending'
            valuation.assigned_to = request.user.assigned_appraiser
            valuation.save()
            
            # Also update the ReportDocument status so the assistant's dashboard reflects it accurately
            from reports.models import ReportDocument
            rd = ReportDocument.objects.filter(object_id=valuation.id, object_type='vehicle').order_by('-created_at').first()
            if rd:
                rd.status = 'pending_review'
                rd.assigned_to = valuation.assigned_to
                rd.save()
                
            return Response({'message': 'Muvaffaqiyatli jo\'natildi'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        if not request.user.is_authenticated or request.user.role != 'appraiser':
            return Response({'error': 'Ruxsat yo\'q'}, status=status.HTTP_403_FORBIDDEN)
            
        valuations = VehicleValuation.objects.filter(assigned_to=request.user, status='pending').order_by('-created_at')
        serializer = self.get_serializer(valuations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def verify(self, request, pk=None):
        try:
            valuation = self.get_object()
            report = ReportDocument.objects.filter(object_id=valuation.id, object_type='vehicle').exclude(file='').order_by('-created_at').first()
            
            # Predict rounding based on valuation logic
            val_date = valuation.valuation_date or datetime.date.today()
            
            return Response({
                "status": "valid",
                "object": {
                    "model": valuation.car_model,
                    "year": valuation.year,
                    "plate": valuation.plate_number,
                    "owner": valuation.owner_name or valuation.tech_passport_owner,
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
            report = ReportDocument.objects.filter(object_id=valuation.id, object_type='vehicle').exclude(file='').order_by('-created_at').first()
            if not report or not report.file:
                return Response({"error": "PDF hisobot hozircha mavjud emas yoki ishlab chiqilmoqda."}, status=status.HTTP_404_NOT_FOUND)
            
            # Use request.build_absolute_uri to reconstruct the full URL based on the incoming host
            pdf_url = request.build_absolute_uri(report.file.url)
            return HttpResponseRedirect(pdf_url)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='generate-report')
    def generate_report(self, request, pk=None):
        global genai_client
        if not genai_client:
            try:
                from vehicles.models import get_gemini_api_key
                db_key = get_gemini_api_key()
                if db_key:
                    from google import genai
                    genai_client = genai.Client(api_key=db_key)
                    print("DEBUG: Dynamically initialized genai_client in generate_report using DB key.", flush=True)
            except Exception as e_init:
                print(f"Failed to dynamically initialize genai_client: {e_init}", flush=True)

        try:
            start_time = time.time()
            
            # Use get_queryset() to follow the defined logic and avoid direct objects.get() which bypasses permissions/logic
            from django.shortcuts import get_object_or_404
            try:
                valuation = self.get_object()
            except Exception as obj_err:
                print(f"CRITICAL: Valuation with ID {pk} not found in queryset. Error: {obj_err}")
                return Response({"error": f"Ma'lumot topilmadi (ID: {pk}). Iltimos, sahifani yangilang."}, status=status.HTTP_404_NOT_FOUND)

            raw_jshshir = getattr(valuation, 'passport_jshshir', '')
            jshshir = 'Mavjud emas'
            if raw_jshshir:
                match = re.search(r'\d{14}', str(raw_jshshir).replace(" ", ""))
                jshshir = match.group(0) if match else str(raw_jshshir)
                    
            usd_rate, eur_rate, rub_rate = 12600.0, 14000.0, 140.0
            val_date = valuation.valuation_date or datetime.date.today()
            date_str = val_date.strftime('%Y-%m-%d')
            
            try:
                cbu_res = requests.get(f'https://cbu.uz/uz/arkhiv-kursov-valyut/json/all/{date_str}/', timeout=1.5)
                if cbu_res.status_code == 200:
                    data = cbu_res.json()
                    for currency in data:
                        if currency['Ccy'] == 'USD': usd_rate = float(currency['Rate'])
                        if currency['Ccy'] == 'EUR': eur_rate = float(currency['Rate'])
                        if currency['Ccy'] == 'RUB': rub_rate = float(currency['Rate'])
            except Exception: pass
                
            today_str = datetime.date.today().strftime('%d.%m.%Y')
            val_date_str = val_date.strftime('%d.%m.%Y')
            analogs = list(valuation.analogs.all()[:3])
            while len(analogs) < 3: analogs.append(None)
            a1, a2, a3 = analogs[0], analogs[1], analogs[2]
            
            def g_p(a):
                try: return f"{float(a.price):,.0f}" if a and a.price else "0"
                except: return "0"
            def g_s(a):
                try: return f"{(float(a.price) * usd_rate):,.0f}" if a and a.price else "0"
                except: return "0"
            
            valid_analogs = [a for a in analogs if a and a.price]
            # Robust average using MathEngine (Median/Trimmed Mean)
            all_prices = [float(a.price) for a in valid_analogs]
            from valuation_engine.vehicle_math import VehicleMathEngine
            avg_usd = VehicleMathEngine.calculate_robust_price(all_prices)
            avg_sum = round((avg_usd * usd_rate) / 1000) * 1000
            
            try: car_age = val_date.year - int(valuation.year)
            except: car_age = 0

            def clean_mileage(m):
                if not m or str(m) == "Noma'lum": return 0
                digits = re.sub(r'[^\d]', '', str(m))
                return int(digits) if digits else 0

            obj_mileage = clean_mileage(valuation.mileage)
            obj_wear = VehicleMathEngine.calculate_physical_wear(car_age, obj_mileage)
            
            analogs_wear_adjustments = []
            for analog in [a1, a2, a3]:
                if analog:
                    try:
                        a_wear = VehicleMathEngine.calculate_physical_wear(car_age, clean_mileage(analog.mileage))
                        k_wear = VehicleMathEngine.calculate_wear_adjustment(obj_wear, a_wear)
                        analogs_wear_adjustments.append(k_wear)
                        analog.wear_percent = a_wear * 100
                        analog.wear_adjustment = k_wear * 100
                        analog.save()
                    except: analogs_wear_adjustments.append(0)
                else: analogs_wear_adjustments.append(0)

            weights = VehicleMathEngine.calculate_weights(analogs_wear_adjustments)
            for i, analog in enumerate([a1, a2, a3]):
                if analog and i < len(weights):
                    analog.weight = weights[i]
                    analog.save()

            # Dynamic replacement cost based on model
            base_prices = {
                'damas': 8500, 'labo': 9000, 'matiz': 4500, 'spark': 8500,
                'nexia': 9500, 'cobalt': 11500, 'lacetti': 13500, 'gentra': 13500,
                'tracker': 19500, 'equinox': 35000, 'malibu': 32000, 'tahoe': 85000,
                'onix': 14500, 'captiva': 25000
            }
            
            model_lower = str(valuation.car_model).lower()
            replacement_cost_usd = 13500 # Default
            for m_key, m_price in base_prices.items():
                if m_key in model_lower:
                    replacement_cost_usd = m_price
                    break
            
            if valuation.replacement_cost_usd:
                replacement_cost_usd = float(valuation.replacement_cost_usd)

            replacement_cost_uzs = replacement_cost_usd * usd_rate
            act_wear = float(valuation.act_wear_percent or 70.0)
            scale_wear = VehicleMathEngine.get_scale_wear(valuation.technical_condition or "Qoniqarli")
            formula_wear_percent = obj_wear * 100.0
            aggregate_wear = VehicleMathEngine.calculate_aggregate_wear(act_wear, scale_wear, formula_wear_percent)
            cost_value_uzs = VehicleMathEngine.calculate_residual_value(replacement_cost_uzs, aggregate_wear)
            # Generate Detailed CP Tags first to use accurate weighted sum
            cp_tags = generate_cp_tags(valuation, a1, a2, a3, val_date, usd_rate, obj_wear)
            
            # The true comparative value is calculated inside generate_cp_tags as total_v_narx
            # Let's extract it back to float from the formatted string
            print("DEBUG: Calculating final values...", flush=True)
            try:
                comp_val_str = cp_tags.get('{cp_jami_narx}', '0').replace('$', '').replace(' ', '').replace(',', '.')
                comp_value_uzs = float(comp_val_str)
            except:
                comp_value_uzs = 0 # Fallback
            
            # Weighting based on selected method
            w_comp, w_cost = 1.0, 0.0 # Default Qiyosiy
            if valuation.method == 'xarajat':
                w_comp, w_cost = 0.0, 1.0
            elif valuation.method == 'daromad':
                w_comp, w_cost = 0.5, 0.5 # Placeholder for Daromad mix

            final_value_raw = (comp_value_uzs * w_comp) + (cost_value_uzs * w_cost)
            final_value_rounded = VehicleMathEngine.round_to_nearest_thousand(final_value_raw)
            final_value_words = (number_to_uzbek_words(final_value_rounded) + " so'm").capitalize()
            print("DEBUG: Final values calculated.", flush=True)
            
            # Tables
            print("DEBUG: Preparing table data...", flush=True)
            prof_data = {'rows': [
                ("AQSH dollarida taklif etilgan qiymat", ["-", f"${g_p(a1)}", f"${g_p(a2)}", f"${g_p(a3)}"]),
                ("Valyuta kursi (CBU)", ["-", f"{usd_rate:,.2f}", f"{usd_rate:,.2f}", f"{usd_rate:,.2f}"]),
                ("So'mdagi taklif etilgan narx", ["-", g_s(a1), g_s(a2), g_s(a3)]),
                ("Mulkiy huquqlar", ["To'liq", "To'liq", "To'liq", "To'liq"]),
                ("Vaqt omili", [val_date_str, val_date_str, val_date_str, val_date_str]),
                ("Qiymat turi (Bozor vs Taklif)", ["Bozor", "Taklif", "Taklif", "Taklif"]),
                ("Yosh (yil)", [car_age, car_age, car_age, car_age]),
                ("Bosib o'tgan masofasi (km)", [f"{obj_mileage:,}".replace(',', ' '), str(getattr(a1,'mileage','0')).replace(',', ' '), str(getattr(a2,'mileage','0')).replace(',', ' '), str(getattr(a3,'mileage','0')).replace(',', ' ')]),
                ("Dvigatel hajmi (sm3)", [str(valuation.engine_capacity or '1.5'), str(getattr(a1,'engine_capacity','-')), str(getattr(a2,'engine_capacity','-')), str(getattr(a3,'engine_capacity','-'))]),
                ("Uzatma qutisi (KPP)", [str(valuation.transmission_type or 'Mexanika'), str(getattr(a1,'transmission','-')), str(getattr(a2,'transmission','-')), str(getattr(a3,'transmission','-'))]),
                ("Joylashgan manzili", [str(valuation.region or 'Toshkent'), str(getattr(a1,'location','Toshkent')), str(getattr(a2,'location','Toshkent')), str(getattr(a3,'location','Toshkent'))]),
                ("Jismoniy eskirish (%)", [f"{obj_wear*100:.2f}%".replace('.', ','), f"{getattr(a1,'wear_percent',0):.2f}%".replace('.', ','), f"{getattr(a2,'wear_percent',0):.2f}%".replace('.', ','), f"{getattr(a3,'wear_percent',0):.2f}%".replace('.', ',')]),
                ("Vazn koeffisiyenti", ["-", f"{getattr(a1,'weight',0):.3f}".replace('.', ','), f"{getattr(a2,'weight',0):.3f}".replace('.', ','), f"{getattr(a3,'weight',0):.3f}".replace('.', ',')]),
            ]}
            
            criteria_data = {'rows': [
                ("Baholash maqsadini hisobga olish qobiliyati", 2, 0),
                ("Bozor sharoitlarini hisobga olish qobiliyati", 2, 0),
                ("Ob’yektning fizik va iqtisodiy parametrlarini hisobga olish qobiliyati", 2, 0),
                ("Axborot sifati", 2, 0),
                ("Qo‘llanilgan ma’lumotlarning ishonchliligi", 2, 0),
                ("Hisoblash usulining shaffofligi va takrorlanish imkoniyati", 2, 0),
                ("JAMI BALL", 12, 0),
                ("VAZN KOEFFISIYENTI", "1.00", "0.00")
            ]}
            
            recon_data = {'rows': [
                ("Baholash qiymati, so'mda", f"{cost_value_uzs:,.2f}", f"{comp_value_uzs:,.2f}"),
                ("Solishtirma og'irlik koeffisiyenti", f"{w_cost:.2f}", f"{w_comp:.2f}"),
                ("Baholash yondashuvi ulushi, so'mda", f"{(cost_value_uzs * w_cost):,.2f}", f"{(comp_value_uzs * w_comp):,.2f}"),
                ("Yakuniy baholash qiymati, so'mda", "-", f"{final_value_rounded:,.0f}")
            ]}
            print("DEBUG: Table data prepared.", flush=True)

            # Jadvallar kontekstga to'g'ridan to'g'ri qiymatlar yuboramiz (shablonlarda shunday talab qilinsa)
            cr_q_w = 1.0  # Qiyosiy yondashuv vazni (hozirgi default = 1.0)
            cr_x_w = 0.0  # Xarajat yondashuvi vazni (hozirgi default = 0.0)
            
            context = {
                'professional_table_data': prof_data,
                'criteria_table_data': criteria_data,
                'reconciliation_table_data': recon_data,
                'macroeconomic_table_data': generate_macro_data(valuation),
                
                # Mezonlar tablitsasi yakkama yakka teglari
                '{cr_q1}': '2', '{cr_x1}': '0',
                '{cr_q2}': '2', '{cr_x2}': '0',
                '{cr_q3}': '2', '{cr_x3}': '0',
                '{cr_q4}': '2', '{cr_x4}': '0',
                '{cr_q5}': '2', '{cr_x5}': '0',
                '{cr_q6}': '2', '{cr_x6}': '0',
                '{cr_q_jami}': '12', '{cr_x_jami}': '0',
                '{cr_jami_sum}': '12',
                '{cr_q_vazn}': f'{cr_q_w:.2f}', '{cr_x_vazn}': f'{cr_x_w:.2f}',
                
                # Muvofiqlashtirish tablitsasi yakkama yakka teglari
                '{rec_cost_val}': f"{cost_value_uzs:,.2f}".replace(',', ' ').replace('.', ','),
                '{rec_comp_val}': f"{comp_value_uzs:,.2f}".replace(',', ' ').replace('.', ','),
                '{rec_cost_weight}': f"{w_cost:.2f}".replace('.', ','),
                '{rec_comp_weight}': f"{w_comp:.2f}".replace('.', ','),
                '{rec_cost_share}': f"{(cost_value_uzs * w_cost):,.2f}".replace(',', ' ').replace('.', ','),
                '{rec_comp_share}': f"{(comp_value_uzs * w_comp):,.2f}".replace(',', ' ').replace('.', ','),
                '{rec_final_val}': f"{final_value_rounded:,.0f}".replace(',', ' '),

            }

            def strip_uzb(s):
                if not s: return ""
                # Replace long institutional names with simplified ones
                s = str(s).replace("STATE PERSONALIZATION CENTRE", "IIB")
                s = str(s).replace("DAVLAT PERSONALLASHTIRISH MARKAZI", "IIB")
                
                # Remove O'zbekiston case-insensitively with various apostrophes
                s = re.sub(r'(?i)O[\'’`]?zbekiston( Respublikasi)?', '', str(s))
                # Remove extra spaces left behind
                s = re.sub(r'\s+', ' ', s).strip()
                # Remove trailing commas or dashes
                return s.strip(',- ')

            region_str = strip_uzb(getattr(valuation, 'region', ''))
            district_str = strip_uzb(getattr(valuation, 'district', ''))
            given_by_str = strip_uzb(getattr(valuation, 'passport_given_by', ''))
            
            pasport_joy_arr = []
            if region_str and region_str.lower() not in given_by_str.lower(): pasport_joy_arr.append(region_str)
            if district_str and district_str.lower() not in given_by_str.lower(): pasport_joy_arr.append(district_str)
            if given_by_str: pasport_joy_arr.append(given_by_str)
            
            pasport_joy_final = " ".join(pasport_joy_arr) if pasport_joy_arr else "Ma'lumot yo'q"

            def f_uz(s):
                if not s: return ""
                return str(s).replace("o'", "o’").replace("g'", "g’").replace("O'", "O’").replace("G'", "G’")

            # Casing function for Names (e.g. Nematov Hasanxo'ja)
            def name_case(s):
                if not s: return ""
                # We need to capitalize only the first letter of each part
                words = f_uz(s).split()
                # Handle proper casing for names like "Yo'ldoshev" or "O'g'li"
                return " ".join(w[0].upper() + w[1:].lower() if len(w) > 0 else w for w in words)


            # Remove 'O'zbekiston' and cleanly format passport given date
            pp_given = str(getattr(valuation, 'passport_given_date', '')).replace(' ', '.').replace('-', '.')
            pp_given = pp_given.replace('O\'zbekiston', '').replace('O’zbekiston', '').replace('O`zbekiston', '').strip(' .')
            
            # Format and normalize passport type to "ID-karta pasporti" for professional presentation
            hujjat_turi_str = getattr(valuation, 'passport_type', 'Biometrik pasport') or 'Biometrik pasport'
            hujjat_turi_upper = hujjat_turi_str.upper()
            if 'ID' in hujjat_turi_upper and 'PASPORT' not in hujjat_turi_upper:
                hujjat_turi_str = 'ID-karta pasporti'
                
            print("DEBUG: Context data prepared.", flush=True)

            # Construct text values for the newly identified missing tags
            tashqi_va_ichki_arr = []
            if getattr(valuation, 'has_faded_paint', False):
                tashqi_va_ichki_arr.append("Kuzovning bo'yoq qoplamasida tabiiy eskirish natijasida yuzaga kelgan yengil xiralashishlar va mayda tirnalishlar aniqlandi.")
            else:
                tashqi_va_ichki_arr.append("Kuzovning tashqi ko'rinishi va bo'yoq qoplamasi (LKP) yaxshi saqlangan, rangi xiralashishi kuzatilmadi.")

            if getattr(valuation, 'has_stains', False):
                tashqi_va_ichki_arr.append("Salonning ichki o'rindiqlari qoplamasida biroz foydalanish izlari va yengil dog'lar mavjud.")
            else:
                tashqi_va_ichki_arr.append("Salonning ichki holati toza va yaxshi saqlangan, qoplamalarda yirtilishlar yoki dog'lar aniqlanmadi.")

            if getattr(valuation, 'has_corrosion', False):
                tashqi_va_ichki_arr.append("Kuzovning pastki qismida va shassi ulanish joylarida yengil korroziya alomatlari kuzatildi.")
            else:
                tashqi_va_ichki_arr.append("Kuzov va shassi qismlarida korroziya alomatlari aniqlanmadi.")

            tashqi_va_ichki_holat_matni = " ".join(tashqi_va_ichki_arr)

            fuel_type_str = str(valuation.fuel_type or '').upper()
            additional_equip = [
                "Avtomobil zavod tomonidan o'rnatilgan standart komplektatsiya jihozlari (audio tizimi, xavfsizlik asboblari) bilan butlangan."
            ]
            if any(x in fuel_type_str for x in ['GAZ', 'GBA', 'GBS']):
                additional_equip.append("Shuningdek, transport vositasiga GBU (gaz-ballon uskunasi) o'rnatilgan.")
            qo_shimcha_jihozlar_matni = " ".join(additional_equip)

            almashtirish_metodi_tavsifi = (
                "Almashtirish qiymati usuli (Replacement Cost Method) - baholanayotgan ob'yekt bilan parametrlari va "
                "funksional vazifalariga ko'ra o'xshash bo'lgan yangi ob'yektni joriy bozor narxlarida yaratish yoki "
                "sotib olish xarajatlarini aniqlashga asoslanadi. Ushbu usul ob'yektning hozirgi zamonaviy analogini "
                "yaratish xarajatlarini hisobga oladi."
            )

            tiklanish_qiymati_tavsifi = (
                "Tiklanish qiymati (Reproduction Cost) - baholanayotgan ob'yektning aynan o'zini (nusxasini) joriy bozor "
                "narxlarida, xuddi shunday materiallar, texnologiya va sifat bilan qayta tiklash uchun zarur bo'lgan "
                "xarajatlar yig'indisi hisoblanadi. Transport vositalarini baholashda ko'pincha zamonaviy analoglar asosida "
                "almashtirish qiymati tiklanish qiymati sifatida qabul qilinadi."
            )

            dalolatnoma_eskirish_matni = (
                f"Transport vositasining texnik holati ko'zdan kechirilganda, uning chronologik yoshi "
                f"({car_age:.1f} yil) va bosib o'tgan masofasi ({obj_mileage:,} km) inobatga olinib, "
                f"haqiqiy texnik holatidan kelib chiqqan holda jismoniy eskirish darajasi {obj_wear*100:.2f}% "
                f"deb belgilandi."
            )

            context.update({
                '{tashqi_va_ichki_holat_matni}': f_uz(tashqi_va_ichki_holat_matni),
                '{qo\'shimcha_jihozlar_matni}': f_uz(qo_shimcha_jihozlar_matni),
                '{almashtirish_metodi_tavsifi}': f_uz(almashtirish_metodi_tavsifi),
                '{tiklanish_qiymati_tavsifi}': f_uz(tiklanish_qiymati_tavsifi),
                '{dalolatnoma_eskirish_matni}': f_uz(dalolatnoma_eskirish_matni),
                # Aliases for robust matching
                '{mulk_egasi}': format_fio(valuation.tech_passport_owner or valuation.owner_name or ''),
                '{f_i_sh}': format_fio(valuation.tech_passport_owner or valuation.owner_name or ''),
                '{mulk_egasi_fish}': format_fio(valuation.tech_passport_owner or valuation.owner_name or ''),
                '{owner_name}': format_fio(valuation.tech_passport_owner or valuation.owner_name or ''),
                '{f_i_sh_ega}': format_fio(valuation.tech_passport_owner or valuation.owner_name or ''),
                '{obyekt}': f_uz(valuation.car_model or ''),
                '{obyekt_nomi}': f_uz(valuation.car_model or ''),
                '{avto_modeli}': f_uz(valuation.car_model or ''),
                '{buyurtmachi_nomi}': format_fio(valuation.owner_name or valuation.tech_passport_owner or "Ma'lumot topilmadi"),
                '{avto_raqami}': str(valuation.plate_number or '').upper().replace(' ', ''),
                '{raqami}': str(valuation.plate_number or '').upper().replace(' ', ''),
                '{sana}': today_str,
                '{hisobot_sanasi}': today_str,
                '{baholash_sanasi}': val_date_str,
                
                # Original tags
                '{mulk_egasi_hujjat_malumoti}': f"{hujjat_turi_str} {valuation.passport_serial or ''} {valuation.passport_given_date or ''} {valuation.passport_given_by or ''}".strip() or "Ma'lumot yo'q",
                '{mulk_egasi_jshshir}': str(valuation.passport_jshshir or "Ma'lumot yo'q"),
                '{mulk_egasi_ishshir}': str(valuation.passport_jshshir or "Ma'lumot yo'q"), # Alias for user request
                '{davlat_raqami}': str(valuation.plate_number or "-").upper().replace(' ', ''),
                '{hisobot_raqami}': valuation.report_number or f"V-{valuation.id:04d}",
                '{ishlab_chiqarilgan_yili}': str(valuation.year or '2024'),
                '{modeli}': f_uz(valuation.car_model or "Ma'lumot topilmadi"),
                '{MODELI}': f_uz(valuation.car_model or "Ma'lumot topilmadi").upper(),
                '{shartnoma_sanasi}': valuation.agreement_date.strftime('%d.%m.%Y') if valuation.agreement_date else today_str,
                '{shartnoma_raqami}': valuation.agreement_number or f"SH-{valuation.id:04d}",
                '{buyurtmachi}': format_fio(valuation.owner_name or valuation.tech_passport_owner or "Ma'lumot topilmadi"),
                '{mulk_egasi_fish}': format_fio(valuation.owner_name or valuation.tech_passport_owner or "Ma'lumot topilmadi"),
                '{pasport_seriyasi}': str(getattr(valuation, 'passport_serial', '')).upper().replace(' ', ''),
                '{pasport_berilgan_sana}': pp_given,
                '{pasport_berilgan_joyi}': f_uz(pasport_joy_final),
                '{hujjat_turi}': f_uz(hujjat_turi_str),
                '{jshshir}': jshshir,
                
                # Tex-pasport tags
                '{guvohnoma_raqami}': str(valuation.registration_number or valuation.tech_passport_serial or ''),
                '{guvoxnoma_raqami}': str(valuation.registration_number or valuation.tech_passport_serial or ''),
                '{dvigatel_raqami}': str(valuation.engine_number or ''),
                '{vin}': str(valuation.vin_code or '').replace(' ', ''),
                '{rangi}': str(valuation.color or 'Oq'),
                '{texnik_holati}': str(valuation.technical_condition or 'Qoniqarli'),
                '{dastlabki_balans_qiymati}': str(valuation.initial_balance_value or '0'),
                '{qoldiq_balans_qiymati}': str(valuation.residual_balance_value or '0'),
                '{dvigatel_hajmi}': str(valuation.engine_capacity) if valuation.engine_capacity and str(valuation.engine_capacity) != 'None' else '1.5',
                '{dvigatel_quvvati}': str(valuation.engine_horsepower) if valuation.engine_horsepower and str(valuation.engine_horsepower) != 'None' else '105',
                '{uzatma_qutisi}': str(valuation.transmission_type or 'Mexanika'),
                '{yoqilgi_turi}': sanitize_fuel_type(valuation.fuel_type),
                '{yonilg\'i}': sanitize_fuel_type(valuation.fuel_type),
                '{yoqilg\'i}': sanitize_fuel_type(valuation.fuel_type),
                '{yonilgi}': sanitize_fuel_type(valuation.fuel_type),
                '{yoqilgi}': sanitize_fuel_type(valuation.fuel_type),
                '{fuel_type}': sanitize_fuel_type(valuation.fuel_type),
                '{transport_turi}': str(valuation.vehicle_type or 'Yengil'),
                '{orindiqlar_soni}': str(valuation.seats_count or '5'),
                '{maksimal_tezlik}': str(valuation.top_speed or '220'),
                '{tola_vazni}': str(valuation.full_weight or '1680'),
                '{yuksiz_vazni}': str(valuation.empty_weight or '1200'),
                
                '{yuk_vazni}': str(getattr(valuation, 'full_weight', '1680 kg')),
                '{yakuniy_narx}': f"{final_value_rounded:,.0f}".replace(',', ' '),
                '{yakuniy_narx_suzlarda}': final_value_words,
                '{usd_kursi}': f"{usd_rate:,.2f}".replace(',', ' ').replace('.', ','),
                '{eur_kursi}': f"{eur_rate:,.2f}".replace(',', ' ').replace('.', ','),
                '{rub_kursi}': f"{rub_rate:,.2f}".replace(',', ' ').replace('.', ','),
                '{cbu_kurslari_royxati}': f"• 1 AQSH dollari – {usd_rate:,.2f} so‘m.\n• 1 Yevro – {eur_rate:,.2f} so‘m.\n• 1 Rossiya rubli – {rub_rate:,.2f} so‘m.".replace(',', ' ').replace('.', ','),
                '{qiymat_turi_tahlili}': "Barcha analoglar taklifiy qiymatlar asosida olingan. Bozor amaliyotida taklif narxlari real sotuv narxlaridan o'rtacha 5% yuqori bo'lishi inobatga olingan holda, barcha analoglarga -5% tuzatish kiritildi.",
                '{eskirish_matni}': f"Baholash ob’yektining haqiqiy xizmat muddati {car_age:.1f}".replace('.', ',') + f" yil va haqiqiy bosib o‘tgan masofasi {obj_mileage:,}".replace(',', ' ') + f" km bo‘lganligi sababli, uning jismoniy eskirishi {obj_wear*100:.2f}%ni tashkil etdi.",
                '{eskirish_hisob_kitobi}': generate_wear_calculation_text(valuation, car_age, obj_mileage, obj_wear, scale_wear, aggregate_wear),
                '{xarajat_yondashuvi_hisobi}': generate_cost_approach_text(replacement_cost_uzs, aggregate_wear, cost_value_uzs),
                '{yakuniy_baholash_qiymati}': f"{final_value_rounded:,.0f}",
                '{yakuniy_qiymat_suzlarda}': final_value_words,
                '{bozor_qiymati}': f"{final_value_rounded:,.0f}".replace(',', ' '),
                '{bozor_qiymati_suzlarda}': final_value_words,
                '{baholanayotgan_obyekt}': f_uz(valuation.car_model or ''),
                '{texnik_holat_darajasi}': str(valuation.technical_condition or 'Qoniqarli'),
                '{yurgan_masofasi}': f"{obj_mileage:,}".replace(',', ' ') if obj_mileage > 0 else 'Noma\'lum',

                # Explicit labels for the evaluation object
                '{label_model}': "Rusumi va modeli",
                '{label_turi}': "Turi",
                '{label_kuzov}': "Kuzov turi",
                '{label_yili}': "Ishlab chiqarilgan yili",
                '{label_muddat}': "Haqiqiy xizmat muddati",
                '{label_probeg}': "Bosib o'tgan masofasi, km",
                '{label_rangi}': "Rangi",
                '{label_uzatma}': "Uzatmalar qutisi",
                '{label_yoqilgi}': "Yoqilg'i turi",
                '{label_texnik_holat}': "Texnik holati",
                '{label_manzil}': "Joylashgan manzili",
            })

            # Call single consolidated generator to avoid hitting API Rate Limits (1 request instead of 10)
            from google.genai import types
            ai_data = generate_all_analyses(valuation, car_age, obj_wear)
            
            context.update({
                '{iqtisodiy_vaziyat_matni}': ai_data['economic_analysis'],
                '{makroiqtisodiy_jadval}': ai_data['economic_analysis'], # Fill empty space with text
                '{aholi_daromadlari_tahlili}': ai_data['income_analysis'],
                '{bozor_tendensiyalari_tahlili}': ai_data['market_trends'],
                '{model_xususiyatlari_tahlili}': ai_data['model_specific'],
                '{texnik_holat_tahlili}': ai_data['tech_condition'],
                '{bozor_vaziyati_matni}': ai_data['market_analysis'],
                '{qiyosiy_yondashuv_tavsifi}': ai_data['approach_qiyosiy'],
                '{xarajat_yondashuvi_tavsifi}': ai_data['approach_xarajat'],
                '{daromad_yondashuvi_tavsifi}': ai_data['approach_daromad'],
                '{muvofiqlashtirish_matni}': ai_data['reconciliation'],
            })
            print(f"DEBUG: Consolidated AI analysis completed in {time.time() - start_time:.2f}s", flush=True)

            for i, analog in enumerate([a1, a2, a3], 1):
                s = f"a{i}_"
                if analog:
                    try: a_age = val_date.year - int(analog.year)
                    except: a_age = 7
                    a_mileage_str = str(analog.mileage).replace(',', ' ')
                    if str(analog.mileage).strip() in ['0', '0 km']:
                        a_mileage_str = 'Noma\'lum'
                    
                    context.update({
                        f'{{{s}model}}': str(analog.model_name),
                        f'{{{s}turi}}': "yengil",
                        f'{{{s}kuzov}}': str(getattr(analog, 'body_type', 'Sedan')),
                        f'{{{s}yili}}': str(analog.year),
                        f'{{{s}muddat}}': f"{float(a_age):.1f}".replace('.', ','),
                        f'{{{s}probeg}}': a_mileage_str,
                        f'{{{s}rangi}}': str(getattr(analog, 'color', 'Oq')),
                        f'{{{s}uzatma}}': str(getattr(analog, 'transmission', 'Mexanika')),
                        f'{{{s}nuqson_rang}}': str(getattr(analog, 'has_faded_paint', 'mavjud emas')),
                        f'{{{s}nuqson_dog}}': str(getattr(analog, 'has_stains', 'mavjud emas')),
                        f'{{{s}nuqson_korroziya}}': str(getattr(analog, 'has_corrosion', 'mavjud emas')),
                        f'{{{s}sharoit_girchillash}}': str(getattr(analog, 'has_creaking', 'nuqsonlarsiz')),
                        f'{{{s}sharoit_izolyasiya}}': str(getattr(analog, 'has_insulation_issue', 'nuqsonlarsiz')),
                        f'{{{s}manzil}}': str(analog.location or 'Toshkent'),
                        f'{{{s}qiymat_turi}}': "taklifiy qiymat",
                        f'{{{s}narxi}}': f"${float(analog.price):,.2f}".replace(',', ' ').replace('.', ','),
                        f'{{{s}manba}}': str(analog.url),
                        f'{{analog_{i}_url}}': str(analog.url),

                        # Explicit labels for the analog
                        f'{{{s}label_model}}': "Rusumi va modeli",
                        f'{{{s}label_turi}}': "Turi",
                        f'{{{s}label_kuzov}}': "Kuzov turi",
                        f'{{{s}label_yili}}': "Ishlab chiqarilgan yili",
                        f'{{{s}label_muddat}}': "Haqiqiy xizmat muddati",
                        f'{{{s}label_probeg}}': "Bosib o'tgan masofasi, km",
                        f'{{{s}label_rangi}}': "Rangi",
                        f'{{{s}label_uzatma}}': "Uzatmalar qutisi",
                        f'{{{s}label_nuqson_rang}}': "Bo'yoq qoplamasining holati",
                        f'{{{s}label_nuqson_dog}}': "Ichki qoplamalarda dog'lar",
                        f'{{{s}label_nuqson_korroziya}}': "Kuzovda korroziya",
                        f'{{{s}label_sharoit_girchillash}}': "Boshqaruvda girchillashlar",
                        f'{{{s}label_sharoit_izolyasiya}}': "Shovqin izolyatsiyasi",
                        f'{{{s}label_manzil}}': "Joylashgan manzili",
                        f'{{{s}label_qiymat_turi}}': "Qiymat turi",
                        f'{{{s}label_narxi}}': "Taklif etilgan narxi",
                        f'{{{s}label_manba}}': "Ma'lumot manbasi",
                    })
                else:
                    context.update({
                        f'{{{s}model}}': "-", f'{{{s}turi}}': "-", f'{{{s}kuzov}}': "-", f'{{{s}yili}}': "-", f'{{{s}muddat}}': "-",
                        f'{{{s}probeg}}': "-", f'{{{s}rangi}}': "-", f'{{{s}uzatma}}': "-", f'{{{s}nuqson_rang}}': "-",
                        f'{{{s}nuqson_dog}}': "-", f'{{{s}nuqson_korroziya}}': "-", f'{{{s}sharoit_girchillash}}': "-",
                        f'{{{s}sharoit_izolyasiya}}': "-", f'{{{s}manzil}}': "-", f'{{{s}qiymat_turi}}': "-",
                        f'{{{s}narxi}}': "-", f'{{{s}manba}}': "-", f'{{analog_{i}_url}}': "-",

                        # Explicit labels for the empty analog
                        f'{{{s}label_model}}': "Rusumi va modeli",
                        f'{{{s}label_turi}}': "Turi",
                        f'{{{s}label_kuzov}}': "Kuzov turi",
                        f'{{{s}label_yili}}': "Ishlab chiqarilgan yili",
                        f'{{{s}label_muddat}}': "Haqiqiy xizmat muddati",
                        f'{{{s}label_probeg}}': "Bosib o'tgan masofasi, km",
                        f'{{{s}label_rangi}}': "Rangi",
                        f'{{{s}label_uzatma}}': "Uzatmalar qutisi",
                        f'{{{s}label_nuqson_rang}}': "Bo'yoq qoplamasining holati",
                        f'{{{s}label_nuqson_dog}}': "Ichki qoplamalarda dog'lar",
                        f'{{{s}label_nuqson_korroziya}}': "Kuzovda korroziya",
                        f'{{{s}label_sharoit_girchillash}}': "Boshqaruvda girchillashlar",
                        f'{{{s}label_sharoit_izolyasiya}}': "Shovqin izolyatsiyasi",
                        f'{{{s}label_manzil}}': "Joylashgan manzili",
                        f'{{{s}label_qiymat_turi}}': "Qiymat turi",
                        f'{{{s}label_narxi}}': "Taklif etilgan narxi",
                        f'{{{s}label_manba}}': "Ma'lumot manbasi",
                    })

            
            # Additional tags mapping for the user's template explicitly
            cp_tags['{cp_yosh_o}'] = cp_tags.get('{cp_yosh_a0}', '0,0')
            cp_tags['{yosh_o}'] = cp_tags.get('{cp_yosh_a0}', '0,0')
            cp_tags['{cp_probeg_a0}'] = cp_tags.get('{cp_probeg_o}', '0')
            
            # Explicitly merge comparative tags and ensure no overwrites of important ones
            context.update(cp_tags)
            
            # Re-ensure some critical tags if they were overwritten
            context['{jshshir}'] = jshshir
            context['{yakuniy_narx}'] = f"{final_value_rounded:,.0f}".replace(',', ' ')

            template_id = request.data.get('template_id')
            from reports.models import ReportTemplate
            template_name = "Noma'lum"
            try:
                if template_id:
                    template_obj = ReportTemplate.objects.get(id=template_id)
                    template_path = template_obj.file.path
                    template_name = template_obj.name
                else:
                    # Try to find the latest "Professional" template as default
                    latest_prof = ReportTemplate.objects.filter(name__icontains='Professional', object_type='vehicle').order_by('-created_at').first()
                    if latest_prof:
                        template_path = latest_prof.file.path
                        template_name = latest_prof.name
                    else:
                        template_path = 'tmp/base_template.docx'
                        template_name = "Base Fallback (tmp/base_template.docx)"
            except Exception as template_err:
                print(f"CRITICAL TEMPLATE ERROR: {template_err}", flush=True)
                template_path = 'tmp/base_template.docx'
                template_name = f"Error Fallback: {str(template_err)}"
            
            print(f"DEBUG: Using template: {template_path} (ID: {template_id})", flush=True)

            # Reuse existing report if available for this object to keep UUID stable
            # Use filter().first() instead of get_or_create to avoid MultipleObjectsReturned errors
            report = ReportDocument.objects.filter(
                object_id=valuation.id, 
                object_type='vehicle'
            ).order_by('-created_at').first()
            
            if not report:
                report = ReportDocument.objects.create(
                    object_id=valuation.id,
                    object_type='vehicle',
                    user=valuation.user, # Assign to the person who created the valuation
                    status='approved' if valuation.status == 'approved' else 'draft'
                )
                print(f"DEBUG: Created NEW ReportDocument {report.id} for valuation {valuation.id} with status {report.status}", flush=True)
            else:
                # If it already exists, ensure the owner is correct (it might have been created by a guest/appraiser)
                if not report.user and valuation.user:
                    report.user = valuation.user
                    report.save()
                if valuation.status == 'approved' and report.status != 'approved':
                    report.status = 'approved'
                    report.save()
                print(f"DEBUG: Reusing existing ReportDocument {report.id} for valuation {valuation.id} with status {report.status}", flush=True)
            
            report.market_value = f"{final_value_rounded:,.0f} so'm".replace(',', ' ')
            report.save()
            
            safe_model = re.sub(r'[^a-zA-Z0-9_\-]', '', str(valuation.car_model).replace(" ", "_")) or "Mashina"
            file_name = f"{safe_model}_{report.id}"
            
            # Use media/tmp for serving with unique IDs to prevent caching
            temp_id = uuid.uuid4().hex[:12]
            request_dir = os.path.join(settings.MEDIA_ROOT, 'tmp', temp_id)
            os.makedirs(request_dir, exist_ok=True)
            
            # Use the original request host for web downloads to avoid cross-origin/insecure issues
            web_host = request.get_host()
            local_ip = get_local_ip()
            
            # If accessed via localhost, KEEP localhost for file downloads so they work on the same machine
            # But the QR code itself MUST point to the local_ip so mobile phones on the same WiFi can open it.
            
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
            
            # IMPORTANT: Use report.id (UUID) instead of valuation.id for 100% stable lookups
            verify_absolute_url = f"{protocol}://{qr_host}/verify/{report.id}"
            
            # Generate QR Code
            qr_file = generate_qr_for_report(report.id, verify_url=verify_absolute_url)
            qr_obj, _ = QRCode.objects.update_or_create(report=report, defaults={'code_image': qr_file})
            
            out_docx = os.path.join(request_dir, f'report_{valuation.id}.docx')
            out_pdf = os.path.join(request_dir, f'report_{valuation.id}.pdf')
            
            context['report_status'] = getattr(report, 'status', 'draft')
            context['verify_absolute_url'] = verify_absolute_url
            
            # Inject dynamic company/appraiser settings context parameters
            user_model = valuation.user
            company_name = "PERCEPTION VALUE"
            company_stir = "301234567"
            appraiser_name = "B.M.Mirzabekov"
            appraiser_license = "№0244"
            appraiser_pinfl = "31204901234567"
            company_logo_path = None
            company_seal_path = None
            appraiser_signature_path = None

            if user_model:
                if user_model.full_name:
                    appraiser_name = user_model.full_name
                if user_model.license_number:
                    appraiser_license = user_model.license_number
                if user_model.pinfl:
                    appraiser_pinfl = user_model.pinfl
                if user_model.signature:
                    appraiser_signature_path = user_model.signature.path
                
                if user_model.company:
                    company_name = user_model.company.name
                    company_stir = user_model.company.stir
                    if user_model.company.logo:
                        company_logo_path = user_model.company.logo.path
                    if user_model.company.seal:
                        company_seal_path = user_model.company.seal.path

            context['company_name'] = company_name
            context['company_stir'] = company_stir
            context['appraiser_name'] = appraiser_name
            context['appraiser_license'] = appraiser_license
            context['appraiser_pinfl'] = appraiser_pinfl
            
            if company_logo_path and os.path.exists(company_logo_path):
                context['logo_path'] = company_logo_path
            
            # Fallback to project root digital_seal.png and digital_sig.png if missing in database
            if not company_seal_path or not os.path.exists(company_seal_path):
                fallback_seal = os.path.abspath(os.path.join(settings.BASE_DIR, '..', 'digital_seal.png'))
                if os.path.exists(fallback_seal):
                    company_seal_path = fallback_seal
            if company_seal_path and os.path.exists(company_seal_path):
                context['seal_path'] = company_seal_path
                
            if not appraiser_signature_path or not os.path.exists(appraiser_signature_path):
                fallback_sig = os.path.abspath(os.path.join(settings.BASE_DIR, '..', 'digital_sig.png'))
                if os.path.exists(fallback_sig):
                    appraiser_signature_path = fallback_sig
            if appraiser_signature_path and os.path.exists(appraiser_signature_path):
                context['signature_path'] = appraiser_signature_path


            context['report_id_str'] = str(report.id)
            
            # Generate narrative texts using Claude API according to MBS-15
            try:
                print("DEBUG: Generating report narratives using Claude API...", flush=True)
                from reports.report_text_generator import generate_report_narratives
                narratives = generate_report_narratives(valuation, usd_rate=usd_rate)
                for nk, nv in narratives.items():
                    context[f'{{{nk}}}'] = nv
                    context[nk] = nv  # Add both bracket and direct keys for flexibility
                
                # Explicit legacy key overrides for the template placeholders
                if 'bozor_tahlili_matni' in narratives:
                    context['{bozor_vaziyati_matni}'] = narratives['bozor_tahlili_matni']
                    context['{bozor_tendensiyalari_tahlili}'] = narratives['bozor_tahlili_matni']
                if 'muvofiqlashtirish_matni' in narratives:
                    context['{muvofiqlashtirish_matni}'] = narratives['muvofiqlashtirish_matni']
                if 'xulosa_matni' in narratives:
                    context['{xulosa_matni}'] = narratives['xulosa_matni']
                    context['{xulosa_va_baholash_natijasi}'] = narratives['xulosa_matni']
                print("DEBUG: Narratives generated and merged into context.", flush=True)
            except Exception as narrative_err:
                print(f"CRITICAL ERROR generating narratives: {narrative_err}", flush=True)

            fill_docx_template(template_path, out_docx, context, qr_code_path=qr_obj.code_image.path)
            
            # Auto AI Reviewer adaptation based on selected entity_type
            entity_type = request.data.get('entity_type', 'physical')
            is_physical = (entity_type == 'physical')
            try:
                print(f"DEBUG: Running automated AI Reviewer for entity_type: {entity_type}...", flush=True)
                from reports.ai_reviewer import analyze_report_with_ai, apply_docx_corrections
                ai_res = analyze_report_with_ai(out_docx, is_physical=is_physical)
                issues = ai_res.get('issues', [])
                if issues:
                    print(f"DEBUG: AI Reviewer found {len(issues)} corrections. Applying...", flush=True)
                    apply_docx_corrections(out_docx, issues)
                    print("DEBUG: AI corrections applied successfully.", flush=True)
                else:
                    print("DEBUG: AI Reviewer found no entity/grammar issues.", flush=True)
            except Exception as ai_err:
                print(f"CRITICAL AI AUTO-REVIEW ERROR: {ai_err}", flush=True)

            docx_url = f"{settings.MEDIA_URL}tmp/{temp_id}/report_{valuation.id}.docx"
            
            try:
                print(f"DEBUG: Starting HTML-to-PDF generation for valuation {valuation.id}", flush=True)
                from reports.report_pdf_builder import convert_docx_to_html_and_render_pdf
                pdf_res = convert_docx_to_html_and_render_pdf(out_docx, out_pdf, context)
                if not pdf_res or not os.path.exists(pdf_res):
                    raise Exception("PDF konvertatsiya muvaffaqiyatsiz tugadi (fayl yaratilmadi)")
                
                protected_out_pdf = os.path.join(request_dir, f'report_{valuation.id}_protected.pdf')
                # Protect PDF (now just copies for compatibility via pdf_generator.py change)
                final_pdf = protect_pdf(out_pdf, protected_out_pdf, owner_password="smartbaholash_admin")
                
                if not final_pdf or not os.path.exists(final_pdf):
                    print("DEBUG: protect_pdf returned None, using original out_pdf", flush=True)
                    final_pdf = out_pdf
                
                print(f"DEBUG: Final PDF size check: {os.path.getsize(final_pdf)} bytes", flush=True)
                
                if os.path.exists(final_pdf) and os.path.getsize(final_pdf) > 0:
                    with open(final_pdf, 'rb') as f: 
                        report.file.save(f'{file_name}_{temp_id}.pdf', ContentFile(f.read()), save=True)
                    
                    # Persist DOCX for history page download
                    try:
                        import shutil
                        docx_persist_dir = os.path.join(settings.MEDIA_ROOT, 'reports', 'docx')
                        os.makedirs(docx_persist_dir, exist_ok=True)
                        docx_persist_path = os.path.join(docx_persist_dir, f'report_{report.id}.docx')
                        shutil.copy2(out_docx, docx_persist_path)
                    except Exception as docx_err:
                        print(f"DEBUG: Failed to persist DOCX: {docx_err}", flush=True)

                    report.status = 'approved'
                    report.save()
                    print(f"DEBUG: PDF successfully saved and status marked as APPROVED. URL: {report.file.url}", flush=True)
                else:
                    raise Exception("Yakuniy PDF fayli yaratilmadi yoki bo'sh (Unknown Error)")
                
                # Cache-busting: add timestamp to URLs
                ts = int(time.time())
                
                # Construct URLs using the identified host
                scheme = request.scheme
                
                final_docx_url = f"{scheme}://{web_host}{docx_url}?v={ts}"
                final_pdf_url = f"{scheme}://{web_host}{report.file.url}?v={ts}"
                final_qr_url = f"{scheme}://{web_host}{qr_obj.code_image.url}?v={ts}" if qr_obj and qr_obj.code_image else None
                
                return Response({
                    "message": "Hisobot shakllandi", 
                    "report_id": report.id, 
                    "docx_url": final_docx_url,
                    "pdf_url": final_pdf_url,
                    "qr_url": final_qr_url,
                    "debug_info": {
                        "template_used": template_name,
                        "template_path": template_path,
                        "temp_id": temp_id,
                        "valuation_id": valuation.id,
                        "host_used": web_host
                    }
                }, status=status.HTTP_200_OK)
            except Exception as pdf_error:
                # Do NOT delete the report record if PDF fails. We still need the DOCX and QR code for the Appraiser page!
                if 'report' in locals() and report and not report.file:
                    print(f"DEBUG: PDF failed, but keeping report record {report.id} for DOCX and QR", flush=True)

                ts = int(time.time())
                scheme = request.scheme
                
                final_docx_url = f"{scheme}://{web_host}{docx_url}?v={ts}"
                final_qr_url = f"{scheme}://{web_host}{qr_obj.code_image.url}?v={ts}" if qr_obj and qr_obj.code_image else None

                return Response({
                    "message": "Word shakllandi, PDF yuz berdi", 
                    "report_id": report.id, 
                    "docx_url": final_docx_url,
                    "pdf_url": None,
                    "qr_url": final_qr_url,
                    "warning": f"PDF xatosi: {str(pdf_error)}",
                    "debug_info": {
                        "template_used": template_name,
                        "template_path": template_path,
                        "temp_id": temp_id,
                        "valuation_id": valuation.id,
                        "host_used": web_host
                    }
                }, status=status.HTTP_200_OK)
        except Exception as e:
            err_msg = traceback.format_exc()
            try:
                with open(os.path.join(settings.BASE_DIR, 'critical_report_error.log'), 'a', encoding='utf-8') as f:
                    f.write(f"\n[{datetime.datetime.now()}] Error generating report ID {pk}:\n{err_msg}\n")
            except: pass
            print(f"CRITICAL GENERATE ERROR: {err_msg}", flush=True)
            # Cleanup on critical failure
            try:
                if 'report' in locals() and report and report.id and not report.file:
                    report.delete()
            except: pass
            
            # We already have traceback imported at top of file
            with open('critical_error.log', 'a', encoding='utf-8') as f:
                f.write(f"\n{datetime.datetime.now()}: {str(e)}\n{traceback.format_exc()}\n")
            return Response({"error": f"Tizimda xatolik: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# safe_generate moved outside for clarity, time already imported at top

def safe_generate(prompt, fallback_text, max_retries=3):
    if not genai_client: return fallback_text
    delay = 2
    for attempt in range(max_retries):
        try:
            print(f"DEBUG: Calling Gemini 2.5-Flash (Attempt {attempt+1})...", flush=True)
            res = genai_client.models.generate_content(model='gemini-2.5-flash', contents=[prompt])
            if res and res.text and len(res.text) > 200:
                print("DEBUG: Gemini call successful.", flush=True)
                return res.text
            raise ValueError(f"Javob juda qisqa (Uzunligi: {len(res.text) if res and res.text else 0} belgidan iborat).")
        except Exception as e:
            print(f"AI xatosi: {e}. Qaytadan urinish {attempt+1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
    return fallback_text

def generate_all_analyses(valuation, car_age, obj_wear):
    from google.genai import types
    fb_economic = (
        "O‘zbekiston Respublikasi iqtisodiyoti 2024-2025 yillarda qator tashqi va ichki xatarlarga qaramasdan, "
        "barqaror o‘sish sur'atlarini namoyon etmoqda. Davlat Statistika Agentligi (stat.uz) hamda Iqtisodiyot va Moliya vazirligi "
        "ma'lumotlariga ko'ra, mamlakat yalpi ichki mahsuloti (YaIM) barqaror ravishda o'rtacha 5-6% darajasida o'sib bormoqda. "
        "Inflyatsiya darajasi prognoz qilingan 8-9% doirasida saqlanib, Markaziy bankning asosiy stavkasi bozordagi "
        "pul massasini jilovlash hamda investitsion muhitni yaxshilash maqsadida mo'tadil hisoblanadi. "
        "Iqtisodiyotdagi bunday makroiqtisodiy barqarorlik to'g'ridan-to'g'ri aholining xarid qobiliyatiga va chakana "
        "savdo aylanmasiga, xususan, yirik iste'mol tovarlari va transport vositalari bozoriga ijobiy ta'sir ko'rsatmoqda. "
        "Yangi makroiqtisodiy strategiyalar doirasida ishlab chiqarishni mahalliylashtirish va sanoat korxonalariga berilayotgan "
        "imtiyozlar natijasida ichki bozordagi tovar ayriboshlash hajmi sezilarli darajada oshgan. Bozor ishtirokchilarining talabi "
        f"natijasida {valuation.car_model} kabi avtomobillarga bo'lgan barqaror talabni ta'minlovchi kafolat bo'lib xizmat qiladi."
    )
    fb_income = (
        "O'zbekiston Respublikasida aholi jon boshiga to'g'ri keladigan umumiy daromadlar hajmi so'nggi yillarda "
        "izchil o'sib bormoqda. Davlat qo'llab-quvvatlash dasturlari, xususiy sektorda yaratilayotgan yangi ish "
        "o'rinlari hamda o'rtacha ish haqi miqdorining inflyatsiya darajasidan yuqori sur'atlarda indeksatsiya qilinishi "
        "aholining real xarid qobiliyatini sezilarli darajada oshirmoqda. Iste'mol smetasida uzoq muddat foydalaniladigan "
        f"tovarlar, ayniqsa, shaxsiy transport vositalarini xarid qilishga yo'naltirilgan mablag'lar ulushi ortgan. "
        f"Bu esa {valuation.car_model} kabi avtomobillarga bo'lgan talabni oshiradi."
    )
    fb_trends = (
        "• **Raqobat muhiti va yangi brendlar:** O'zbekiston avtomobil bozori o'zining mutlaqo yangi rivojlanish bosqichiga qadam qo'ydi. "
        "Mahalliy ishlab chiqarish hajmi bo'yicha «UzAuto Motors» AJ yetakchilikni saqlab qolayotgan bo'lsa-da, bozor monopoliyasidan voz kechish borasidagi "
        "islohotlar natijasida G'arb va Osiyo brendlarining faol kirib kelishi davom etmoqda.\n"
        "• **Bozor barqarorligi va narxlar:** Tarmoqli raqobat erkin bozorda narxlarning tezlik bilan barqarorlashuviga, inflyatsion kutishlarning pasayishiga va iste'molchilar uchun kengroq tanlov imkoniyatlarining yaratilishiga bevosita xizmat qilmoqda.\n"
        f"• **Likvidlik va talab darajasi:** Ikkilamchi bozordagi faollik tahliliga ko'ra, aynan {valuation.car_model} modelining o'z o'rni va doimiy muxlislari bor bo'lib, o'z narxini uzoq muddat barqaror saqlab qolish imkoniyatiga ega."
    )
    fb_model_specific = (
        f"• **Yo'l va iqlim sharoitlariga mosligi:** Baholash obyektimiz hisoblangan {valuation.car_model} rusumli transport vositasi asosan bizning murakkab hududiy va iqlim sharoitlarimizda ekspluatatsiya qilish uchun moslashtirilgan.\n"
        "• **Ehtiyot qismlarining mavjudligi:** Modelning mamlakat bo'ylab keng ommalashganligi tufayli uning ehtiyot qismlarini dilerlik va xususiy ustaxona tarmoqlaridan qiyinchiliksiz topish mumkin.\n"
        f"• **Ikkilamchi bozordagi likvidligi:** {valuation.car_model} rusumi mamlakat ikkilamchi mulk bozorida eng yuqori likvidlikka ega modellardan biridir."
    )
    fb_tech = (
        f"• **Dvigatel va transmissiya holati:** Baholash ob'yekti {valuation.car_model} rusumli avtomobilning dvigatel va transmissiya uzellari shovqinsiz va tebranishlarsiz ishlamoqda.\n"
        "• **Kuzov va tashqi estetika:** Kuzovning bo'yoq qatlami (LKP) tahlil qilinganda, tabiiy eskirish natijasida yuzaga kelgan minimal darajadagi mikro-chiziqlar mavjudligi aniqlandi.\n"
        f"• **Ekspluatatsiya resursi va eskirish:** Yoshi {car_age:.1f} yil va jismoniy eskirish darajasi {obj_wear*100:.1f}% deb baholangan ushbu vositaning umumiy foydalanish resursi kelgusi ekspluatatsiya uchun yetarli darajada saqlangan."
    )
    fb_market = (
        "Hozirgi vaqtda mahalliy va xorijiy rusumdagi yengil avtomobillar bozori asosan erkin ochiq bozor qonuniyatlari asosida "
        "shakllanib bormoqda. Internet tarmog'idagi b2c platformalar (masalan, OLX.uz va avto-salonlar portallari) takliflarning "
        f"oson qidirilishini ta'minlab, hududlardagi narx diskriminatsiyasini kamaytirmoqda. Bu {valuation.car_model} kabi avtomobillar uchun ham xosdir."
    )
    fb_recon = (
        "Xarajat yondashuvi doirasida baholash ob’yektining qiymati qayta tiklanish yoki qayta yaratish qiymati asosida aniqlandi. "
        "Biroq avtotransport vositasi uchun ushbu yondashuv orqali hisoblangan qiymat real bozordagi taklif va talab muvozanati, "
        "ikkinchi qo‘l bozoridagi amaldagi narxlar, hamda ob’yektning iqtisodiy jihatdan samarador foydalanish muddati bilan to‘liq mos kelmaydi."
    )
    fb_app_q = "Mazkur yondashuv bozorda o'xshash avtomobillarning narxlarini tahlil qilish hamda ularning o'ziga xos xususiyatlariga qarab tegishli tuzatishlar kiritishga asoslangan."
    fb_app_x = "Xarajat yondashuvi baholash ob'yektini qayta tiklash yoki almashtirish xarajatlarini hisoblash orqali uning qiymatini aniqlaydi."
    fb_app_d = "Daromad yondashuvi avtomobildan kelajakda olinishi mumkin bo'lgan sof daromadlar oqimini joriy qiymatga keltirish orqali hisoblaydi."

    result = {
        'economic_analysis': fb_economic,
        'income_analysis': fb_income,
        'market_trends': fb_trends,
        'model_specific': fb_model_specific,
        'tech_condition': fb_tech,
        'market_analysis': fb_market,
        'reconciliation': fb_recon,
        'approach_qiyosiy': fb_app_q,
        'approach_xarajat': fb_app_x,
        'approach_daromad': fb_app_d,
    }

    if not genai_client:
        print("DEBUG: genai_client is None in generate_all_analyses, using fallbacks.", flush=True)
        return result

    prompt = f"""You are a certified senior automotive valuation engineer in Uzbekistan.
Generate the required valuation report sections for this vehicle:
Model: {valuation.car_model}
Year: {valuation.year}
Technical Condition: {valuation.technical_condition or 'Yaxshi'}
Age: {car_age:.1f} years
Physical Wear: {obj_wear*100:.1f}%

You MUST return a JSON object (no markdown formatting, no code blocks) with the following structure:
{{
  "economic_analysis": "O'zbekistondagi {valuation.car_model} uchun iqtisodiy vaziyat tahlili (2025). Juda professional, ilmiy-iqtisodiy tilda 8-10 ta uzun gapdan iborat matn.",
  "income_analysis": "O'zbekiston 2025 aholi daromadlari va {valuation.car_model} bozori tahlili. O'ta professional, 8-10 ta uzun gapdan iborat maqola matni.",
  "market_trends": "O'zbekiston 2025-2026 yillardagi avto bozor tendensiyalari haqida 3 ta asosiy banddan iborat professional tahliliy ro'yxat. Format: • **[Mavzu]**: [Tahlil matni, 3-4 gap]",
  "model_specific": "{valuation.car_model} ({valuation.year}) modelining o'ziga xos xususiyatlari, chidamliligi va likvidligi haqida 3 ta asosiy banddan iborat ro'yxat. Format: • **[Mavzu]**: [Tahlil matni, 3-4 gap]",
  "tech_condition": "{valuation.car_model} avtomobilining hozirgi texnik holati haqida 3 ta asosiy banddan iborat texnik-ekspertlik tahlil ro'yxati. Format: • **[Mavzu]**: [Tahlil matni, 3-4 gap]",
  "market_analysis": "O'zbekiston 2025 yengil mashinalar bozori tahlili. {valuation.car_model} bo'yicha likvidlik va narxlash holati. O'ta professional, 12-15 ta uzun gapdan iborat matn.",
  "reconciliation": "Muvofiqlashtirish tahlili. Xarajat yondashuvi (Cost Approach) natijasini 0% ulush bilan qabul qilish va nima uchun u bozor qiymatini aks ettirmasligi haqida O'TA BATAFSIL (20-25 ta gap), professional matn.",
  "approach_qiyosiy": "Qiyosiy yondashuv (Comparative Approach) professional tavsifi (3-4 gap).",
  "approach_xarajat": "Xarajat yondashuvi (Cost Approach) professional tavsifi (3-4 gap).",
  "approach_daromad": "Daromad yondashuvi (Income Approach) professional tavsifi (3-4 gap)."
}}

Rules:
- Write ALL texts in Uzbek.
- The values for "market_trends", "model_specific", and "tech_condition" MUST contain exactly 3 lines/bullet points starting with "• **" and ending with a newline.
- Return ONLY the raw JSON object. Do not wrap in ```json blocks or include any description.
"""

    try:
        print("DEBUG: Calling Gemini 2.5-Flash for consolidated report generation...", flush=True)
        response = genai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt],
            config=types.GenerateContentConfig(
                temperature=0.7,
                response_mime_type="application/json",
            )
        )
        text = response.text.strip()
        if text.startswith("```"):
            text = re.sub(r'^```(?:json)?\n', '', text)
            text = re.sub(r'\n```$', '', text)
        parsed = json.loads(text.strip())
        
        # Merge parsed data into result
        for k in result.keys():
            if k in parsed and parsed[k] and len(str(parsed[k]).strip()) > 30:
                result[k] = str(parsed[k]).strip()
        print("DEBUG: Consolidated Gemini call successful.", flush=True)
    except Exception as e:
        print(f"DEBUG: Consolidated Gemini call failed: {e}. Using fallbacks.", flush=True)
        
    return result

def generate_economic_analysis(valuation):
    fallback = (
        "O‘zbekiston Respublikasi iqtisodiyoti 2024-2025 yillarda qator tashqi va ichki xatarlarga qaramasdan, "
        "barqaror o‘sish sur'atlarini namoyon etmoqda. Davlat Statistika Agentligi (stat.uz) hamda Iqtisodiyot va Moliya vazirligi "
        "ma'lumotlariga ko'ra, mamlakat yalpi ichki mahsuloti (YaIM) barqaror ravishda o'rtacha 5-6% darajasida o'sib bormoqda. "
        "Inflyatsiya darajasi prognoz qilingan 8-9% doirasida saqlanib, Markaziy bankning asosiy stavkasi bozordagi "
        "pul massasini jilovlash hamda investitsion muhitni yaxshilash maqsadida mo'tadil hisoblanadi. "
        "Iqtisodiyotdagi bunday makroiqtisodiy barqarorlik to'g'ridan-to'g'ri aholining xarid qobiliyatiga va chakana "
        "savdo aylanmasiga, xususan, yirik iste'mol tovarlari va transport vositalari bozoriga ijobiy ta'sir ko'rsatmoqda. "
        "Yangi makroiqtisodiy strategiyalar doirasida ishlab chiqarishni mahalliylashtirish va sanoat korxonalariga berilayotgan "
        "imtiyozlar natijasida ichki bozordagi tovar ayriboshlash hajmi sezilarli darajada oshgan. Bu kabi ijobiy dinamika "
        "avtomobilsozlik tarmog'ida ham yaqqol ko'zga tashlanadi. Barqaror milliy valyuta kursi va bank tizimi orqali "
        "ajratilayotgan avtokreditlar hajmining oshishi hamda aholi real daromadlarining indeksatsiya qilinishi natijasida "
        f"{valuation.car_model} kabi avtomobillarga bo'lgan barqaror talabni ta'minlovchi kafolat bo'lib xizmat qiladi. "
        "Shu bilan birga, iqtisodiyotning diversifikatsiya qilinishi va raqobat muhitining yaxshilanishi iste'molchilar "
        "uchun keng tanlov imkoniyatlarini yaratmoqda, bu esa bozordagi narxlarning asossiz o'sishini oldini oladi."
    )
    prompt = (
        f"O'zbekistondagi {valuation.car_model} uchun iqtisodiy vaziyat tahlili (2025). "
        "Juda professional, ilmiy-iqtisodiy tilda 8-10 ta uzun gapdan iborat matn yozing. "
        "Stat.uz va Markaziy bank ma'lumotlariga tayaning. YaIM o'sishi, inflyatsiya kutilmalari, "
        "aholining xarid qobiliyati haqida."
    )
    return safe_generate(prompt, fallback)

def generate_income_analysis(valuation):
    fallback = (
        "O'zbekiston Respublikasida aholi jon boshiga to'g'ri keladigan umumiy daromadlar hajmi so'nggi yillarda "
        "izchil o'sib bormoqda. Davlat qo'llab-quvvatlash dasturlari, xususiy sektorda yaratilayotgan yangi ish "
        "o'rinlari hamda o'rtacha ish haqi miqdorining inflyatsiya darajasidan yuqori sur'atlarda indeksatsiya qilinishi "
        "aholining real xarid qobiliyatini sezilarli darajada oshirmoqda. Iste'mol smetasida uzoq muddat foydalaniladigan "
        "tovarlar, ayniqsa, shaxsiy transport vositalarini xarid qilishga yo'naltirilgan mablag'lar ulushi ortgan. "
        "Bunga qo'shimcha ravishda, tijorat banklari tomonidan taklif etilayotgan avtokredit va lizing xizmatlarining "
        "rang-barangligi aholining o'z jamg'armalari bilan bir qatorda tashqi moliyalashtirish manbalaridan ham faol "
        "foydalanishiga yo'l ochdi. Strategik jihatdan daromadlar tarkibining barqarorlashishi va tadbirkorlik "
        "faoliyatidan olinadigan ulushning ortishi uy xo'jaliklarining moliyaviy barqarorligini ta'minlamoqda. "
        "Bu esa iste'mol bozorida, xususan, ikkilamchi va birlamchi avtomobil bozorida yuqori likvidlikni saqlab qoladi. "
        f"Natijada {valuation.car_model} rusumidagi sifatli, zamonaviy va tejamkor avtomobillar segmentida haridorlar "
        "faolligining tushib ketmasligini va bozor konyunkturasining barcha mavsumiy tebranishlarga qaramasdan "
        "yuqori darajada saqlanishini ta'minlamoqda. Aholining iste'mol kayfiyati tahlillari shuni ko'rsatadiki, "
        "transport vositalari endilikda nafaqat harakatlanish vositasi, balki ishonchli investitsion aktiv sifatida ham ko'rilmoqda."
    )
    prompt = (
        f"O'zbekiston 2025 aholi daromadlari va {valuation.car_model} bozori tahlili. "
        "O'ta professional, 8-10 ta uzun gapdan iborat maqola matni. Aholining daromadlari, "
        "iste'mol savatchasi, bank kreditlari haqida."
    )
    return safe_generate(prompt, fallback)

def generate_market_trends_analysis(valuation):
    fallback = (
        "• **Raqobat muhiti va yangi brendlar:** O'zbekiston avtomobil bozori o'zining mutlaqo yangi rivojlanish bosqichiga qadam qo'ydi. "
        "Mahalliy ishlab chiqarish hajmi bo'yicha «UzAuto Motors» AJ yetakchilikni saqlab qolayotgan bo'lsa-da, bozor monopoliyasidan voz kechish borasidagi "
        "islohotlar natijasida yangi o'yinchilarning faol kirib kelishi davom etmoqda. ADM Jizzax (Kia, Chery) va BYD kompaniyasining gibrid hamda "
        "elektromobillar ishlab chiqarishi o'zbek bozorida mutlaqo yangi raqobat muhitini yaratdi.\n"
        "• **Bozor barqarorligi va narxlar:** Tarmoqli raqobat erkin bozorda narxlarning tezlik bilan barqarorlashuviga, inflyatsion kutishlarning pasayishiga va iste'molchilar uchun kengroq tanlov imkoniyatlarining yaratilishiga bevosita xizmat qilmoqda.\n"
        f"• **Likvidlik va talab darajasi:** Ikkilamchi bozordagi faollik tahliliga ko'ra, aynan {valuation.car_model} modelining o'z o'rni va doimiy muxlislari bor bo'lib, o'z narxini uzoq muddat barqaror saqlab qolish imkoniyatiga ega."
    )
    prompt = (
        f"O'zbekiston 2025-2026 yillardagi avto bozor tendensiyalari (UzAuto, BYD, ADM Jizzax) va aniq {valuation.car_model} rusumi bo'yicha. "
        "Quyidagi shaklda, har bir band yangi satrdan boshlanadigan, jami 3 ta asosiy banddan iborat professional tahliliy ro'yxat yozib bering:\n"
        "• **[Mavzu nomi]:** [Tahlil matni, kamida 3-4 ta gap]\n"
        "Matnda markdown qalin yozuvlardan (**tushuncha**) foydalaning va har bir band orasida bitta yangi satr (newline) tashlang. "
        "QAT'IY ESLATMA: Hech qanday kirish gapi, kirish so'zi, 'Mana tahlil:' kabi ortiqcha matnlar yozmang. To'g'ridan-to'g'ri '• **' belgisi bilan boshlang."
    )
    return safe_generate(prompt, fallback)

def generate_model_specific_analysis(valuation):
    fallback = (
        f"• **Yo'l va iqlim sharoitlariga mosligi:** Baholash obyektimiz hisoblangan {valuation.car_model} rusumli transport vositasi asosan bizning murakkab hududiy va iqlim sharoitlarimizda ekspluatatsiya qilish uchun moslashtirilgan. "
        "Uning kuzov detallari va osma mustahkamlash mexanizmlari (xodovoy qismi) chidamlilik va rezonanslarni kamaytirish ko'rsatkichlari bo'yicha mustahkam va ishonchli hisoblanadi.\n"
        "• **Ehtiyot qismlarining mavjudligi:** Modelning mamlakat bo'ylab keng ommalashganligi tufayli uning ehtiyot qismlarini dilerlik va xususiy ustaxona tarmoqlaridan qiyinchiliksiz topish mumkin. Bu esa ehtimoliy ta'mirlash xarajatlarini sezilarli darajada kamaytiradi.\n"
        f"• **Ikkilamchi bozordagi likvidligi:** {valuation.car_model} rusumi mamlakat ikkilamchi mulk bozorida eng yuqori likvidlikka ega modellardan biridir. Operatsiyalar asosan juda qisqa muddatlarda (2-3 kun) amalga oshadi va o'z qiymatini uzoq muddat saqlaydi."
    )
    prompt = (
        f"{valuation.car_model} ({valuation.year}) modelining o'ziga xos xususiyatlari, texnik afzalliklari, yurtimiz yo'llari va iqlimiga mosligi va likvidligi haqida. "
        "Quyidagi shaklda, har bir band yangi satrdan boshlanadigan, jami 3 ta asosiy banddan iborat professional tahliliy ro'yxat yozib bering:\n"
        "• **[Mavzu nomi]:** [Tahlil matni, kamida 3-4 ta gap]\n"
        "Matnda markdown qalin yozuvlardan (**tushuncha**) foydalaning va har bir band orasida bitta yangi satr (newline) tashlang. "
        "QAT'IY ESLATMA: Hech qanday kirish gapi, kirish so'zi, 'Mana tahlil:' kabi ortiqcha matnlar yozmang. To'g'ridan-to'g'ri '• **' belgisi bilan boshlang."
    )
    return safe_generate(prompt, fallback)

def generate_tech_condition_analysis(valuation, car_age, obj_wear):
    fallback = (
        f"• **Dvigatel va transmissiya holati:** Baholash ob'yekti {valuation.car_model} rusumli avtomobilning dvigatel va transmissiya uzellari shovqinsiz va tebranishlarsiz ishlamoqda. Agregatlarning germetikligi buzilmagan, moy oqishi kuzatilmadi.\n"
        "• **Kuzov va tashqi estetika:** Kuzovning bo'yoq qatlami (LKP) tahlil qilinganda, tabiiy eskirish natijasida yuzaga kelgan minimal darajadagi mikro-chiziqlar mavjudligi aniqlandi. Geometrik aniqlik zavod parametrlariga to'liq mos keladi.\n"
        f"• **Ekspluatatsiya resursi va eskirish:** Yoshi {car_age:.1f} yil va jismoniy eskirish darajasi {obj_wear*100:.1f}% deb baholangan ushbu vositaning umumiy foydalanish resursi kelgusi ekspluatatsiya uchun yetarli darajada saqlangan."
    )
    prompt = (
        f"{valuation.car_model} ({valuation.year}) avtomobilining hozirgi texnik holati: {valuation.technical_condition or 'Yaxshi'} holatda, yoshi {car_age:.1f} yil, eskirishi {obj_wear*100:.1f}%. "
        "Quyidagi shaklda, har bir band va tavsif yangi satrdan boshlanadigan, jami 3 ta asosiy banddan iborat professional texnik-ekspertlik tahlil ro'yxatini yozib bering:\n"
        "• **[Mavzu nomi]:** [Texnik holat tavsifi, kamida 3-4 ta gap]\n"
        "Dvigatel, kuzov, salon, agregatlar holati haqida yozing. Matnda markdown qalin yozuvlardan (**tushuncha**) foydalaning va har bir band orasida bitta yangi satr (newline) tashlang. "
        "QAT'IY ESLATMA: Hech qanday kirish gapi, kirish so'zi, 'Mana tahlil:' kabi ortiqcha matnlar yozmang. To'g'ridan-to'g'ri '• **' belgisi bilan boshlang."
    )
    return safe_generate(prompt, fallback)

def generate_market_analysis(valuation):
    fallback = (
        "Hozirgi vaqtda mahalliy va xorijiy rusumdagi yengil avtomobillar bozori asosan erkin ochiq bozor qonuniyatlari asosida "
        "shakllanib bormoqda. Internet tarmog'idagi b2c platformalar (masalan, OLX.uz va avto-salonlar portallari) takliflarning "
        "oson qidirilishini ta'minlab, hududlardagi narx diskriminatsiyasini kamaytirmoqda. Sotuvchilar va xaridorlar o'rtasida "
        "axborot assimetriyasi yo'qligi va takliflarning yetarliligi tufayli haqiqiy raqobat muhiti shakllangan. "
        "O'zbekiston Respublikasining Jahon Savdo Tashkilotiga integratsiyalashuv bosqichlari va import bojlarining optimallashtirilishi "
        "bozordagi xalqaro brendlar ulushini sezilarli darajada oshirdi. Bu esa o'z navbatida ikkilamchi bozorda ham narxlarning "
        "haqqoniy shakllanishiga va spekulyativ tebranishlarning kamayishiga xizmat qilmoqda. "
        f"Qiyosiy bozor tahlillariga ko'ra, xuddi {valuation.car_model} modeliga o'xshash avtomobillarning oldi-sotdisi doimiy "
        "ravishda faolligini saqlamoqda. Hozirgi iqtisodiy sharoitda ikkilamchi bozordagi narx takliflari yangi avtomobillar "
        "katalogiga to'g'ridan-to'g'ri bog'liq bo'lib, mos ravishda doimiy korreksiyalanadi. Bozor ishtirokchilarining onglilik "
        "darajasi va texnik tahlillar asosida narx belgilashga bo'lgan moyilligi ortib bormoqda, bu esa baholash jarayonining "
        "muhimligini yanada oshiradi."
    )
    prompt = (
        f"O'zbekiston 2025 yengil mashinalar bozori tahlili. {valuation.car_model} bo'yicha likvidlik va narxlash holati. "
        "O'ta professional, 15-20 ta uzun murakkab gapdan iborat tahlil yozing. Bozor segmentatsiyasi, "
        "raqobat muhiti va elektron savdo maydonchalarining ta'sirini ochib bering."
    )
    return safe_generate(prompt, fallback)

def generate_reconciliation_analysis(valuation):
    fallback = (
        "Xarajat yondashuvi doirasida baholash ob’yektining qiymati qayta tiklanish yoki qayta yaratish qiymati asosida aniqlandi. "
        "Biroq avtotransport vositasi uchun ushbu yondashuv orqali hisoblangan qiymat real bozordagi taklif va talab muvozanati, "
        "ikkinchi qo‘l bozoridagi amaldagi narxlar, hamda ob’yektнинг iqtisodiy jihatdan samarador foydalanish muddati bilan to‘liq mos kelmaydi.\n\n"
        "Shu bois, xarajat yondashuvi hisobotni texnik jihatdan to‘ldirish uchun qo‘llanilgan bo‘lsa-da, uning natijasi joriy bozor qiymatini aks ettirmaydi. "
        "Bozordagi real bitimlar bilan taqqoslanganda olingan natija ehtimoliy juda yuqori ko‘rsatkichni namoyon etdi. "
        "Shuning uchun muvofiqlashtirish (korrektirovka) jarayonida xarajat yondashuvi natijasi nolga teng ulush bilan qabul qilindi, "
        "ya’ni umumiy yakuniy qiymatni shakllantirishda hisobga olinmadi."
    )
    prompt = (
        f"Xarajat yondashuvi (Cost Approach) natijasini 0% ulush bilan qabul qilish va nima uchun u bozor qiymatini aks ettirmasligi haqida "
        f"O'TA BATAFSIL (35-40 ta uzun gap), professional va iqtisodiy tahlil yozing. {valuation.car_model} misolida tushuntiring. "
        "Ikkilamchi bozor dinamikasi, yangi avtomobillar raqobati va muvofiqlashtirish (reconciliation) prinsiplariga chuqur to'xtaling. "
        "Jadvallarsiz va ro'yxatlarsiz professional matn bo'lsin."
    )
    return safe_generate(prompt, fallback)

def generate_approach_description(valuation, approach_type):
    fallback = "Mazkur yondashuv bozorda o'xshash avtomobillarning narxlarini tahlil qilish hamda ularning o'ziga xos xususiyatlariga qarab tegishli tuzatishlar kiritishga asoslangan."
    prompt = f"{approach_type} yondashuvining professional tavsifi ({valuation.car_model} uchun)."
    return safe_generate(prompt, fallback)

def generate_cp_tags(valuation, a1, a2, a3, val_date, usd_rate, obj_wear):
    tags = {}
    analogs = [a1, a2, a3]
    val_date_str = val_date.strftime('%d/%m/%Y')
    
    def fmt_v(v, currency="$"):
        try:
            if v == "-" or v is None: return "-"
            f_val = float(str(v).replace('$', '').replace(' ', '').replace(',', '.'))
            formatted = f"{f_val:,.22f}".split('.') # High precision check
            formatted = f"{f_val:,.2f}".replace(',', ' ').replace('.', ',')
            return f"{currency}{formatted}" if currency == "$" else formatted
        except Exception:
            return str(v)

    tags['{cp_huquq_o}'] = "to'liq tasarruf etish mulkiy huquqi"
    tags['{cp_moliya_o}'] = "o'zaro huquq va majburiyat asosida"
    tags['{cp_vaqt_o}'] = val_date_str
    tags['{cp_turi_o}'] = "bozor qiymati"
    tags['{cp_dvigatel_o}'] = str(valuation.engine_capacity or '1500').replace(',', ' ')
    tags['{cp_kpp_o}'] = str(valuation.transmission_type or 'Mexanika')
    tags['{cp_location_o}'] = str(valuation.region or 'Toshkent')
    
    # Missing tags requested by user for the object
    tags['{cp_yosh_a0}'] = f"{(val_date.year - int(valuation.year)):.1f}".replace('.', ',') if valuation.year else "0,0"
    tags['{cp_probeg_o}'] = f"{obj_wear * 100000:.0f}" if obj_wear else "Noma'lum" # Fallback if we don't have exact mileage easily accessible here, we'll override it below
    tags['{cp_eskirish_o}'] = f"{obj_wear * 100:.2f}%".replace('.', ',')
    tags['{cp_eskirish_2}'] = "0,00%"
    tags['{cp_eskirish_3}'] = "0,00%"
    
    for i, analog in enumerate(analogs, 1):
        s = f"a{i}"
        print(f"DEBUG: Processing CP tags for analog {i} (Success: {analog is not None})", flush=True)
        tags[f'{{cp_vaqt_{s}}}'] = val_date_str
        if not analog:
            for k in ['usd', 'kurs', 'uzs', 'huquq_tuz', 'huquq_narx', 'moliya_tuz', 'moliya_narx', 'vaqt_tuz', 'vaqt_narx', 'type_tuz_p', 'type_tuz_s', 'type_narx', 'yosh_tuz_p', 'yosh_narx', 'vazn']:
                tags[f'{{cp_{k}_{s}}}'] = "-"
            continue
        
        usd_narx = float(analog.price)
        tags[f'{{cp_usd_{s}}}'] = fmt_v(usd_narx, "$")
        tags[f'{{cp_kurs_{s}}}'] = fmt_v(usd_rate, "")
        uzs_base = usd_narx * usd_rate
        tags[f'{{cp_uzs_{s}}}'] = fmt_v(uzs_base, "")
        
        try: a_age = f"{(val_date.year - int(analog.year)):.1f}".replace('.', ',')
        except: a_age = "7,0"
        tags[f'{{cp_yosh_{s}}}'] = a_age
        tags[f'{{cp_probeg_{s}}}'] = str(analog.mileage or '0').replace(',', ' ')
        tags[f'{{cp_dvigatel_{s}}}'] = str(getattr(analog, 'engine_capacity', '1.5')).replace(',', ' ')
        tags[f'{{cp_kpp_{s}}}'] = str(getattr(analog, 'transmission_type', 'Mexanika'))
        tags[f'{{cp_location_{s}}}'] = str(getattr(analog, 'location', 'Toshkent'))
        
        # Suffix with 1, 2, 3 for other templates
        tags[f'{{cp_yosh_{i}}}'] = a_age
        tags[f'{{cp_probeg_{i}}}'] = str(analog.mileage or '0').replace(',', ' ')
        tags[f'{{cp_dvigatel_{i}}}'] = str(getattr(analog, 'engine_capacity', '1.5')).replace(',', ' ')
        tags[f'{{cp_kpp_{i}}}'] = str(getattr(analog, 'transmission_type', 'Mexanika'))
        tags[f'{{cp_location_{i}}}'] = str(getattr(analog, 'location', 'Toshkent'))
        
        tags[f'{{a{i}_probeg}}'] = str(analog.mileage or '0').replace(',', ' ')
        tags[f'{{a{i}_yosh}}'] = a_age
        
        # Jismoniy eskirish %
        a_wear_val = getattr(analog, 'wear_percent', 0)
        if a_wear_val == 0:
            try:
                a_age_num = val_date.year - int(analog.year)
                digits = re.sub(r'[^\d]', '', str(analog.mileage))
                a_mileage = int(digits) if digits else 0
                a_wear_val = VehicleMathEngine.calculate_physical_wear(a_age_num, a_mileage) * 100
            except: a_wear_val = obj_wear * 100
            
        tags[f'{{cp_eskirish_{s}}}'] = f"{a_wear_val:.2f}%".replace('.', ',')
        tags[f'{{a{i}_eskirish}}'] = f"{a_wear_val:.2f}%".replace('.', ',') 
        tags[f'{{cp_eskirish_{i}}}'] = f"{a_wear_val:.2f}%".replace('.', ',')
        tags[f'{{cp_yosh_{i}}}'] = a_age
        tags[f'{{cp_probeg_{i}}}'] = str(analog.mileage or '0').replace(',', ' ')

        # Simple placeholder logic for other corrections to keep it stable
        tags[f'{{cp_huquq_tuz_{s}}}'] = "0,00"
        tags[f'{{cp_huquq_narx_{s}}}'] = fmt_v(uzs_base, "")
        tags[f'{{cp_moliya_tuz_{s}}}'] = "0,00"
        tags[f'{{cp_moliya_narx_{s}}}'] = fmt_v(uzs_base, "")
        tags[f'{{cp_vaqt_tuz_{s}}}'] = "0,00"
        tags[f'{{cp_vaqt_narx_{s}}}'] = fmt_v(uzs_base, "")
        print(f"DEBUG: Basic corrections done for analog {i}", flush=True)
        
        # Aliases for 1, 2, 3 without 'a'
        tags[f'{{cp_huquq_tuz_{i}}}'] = "0,00"
        tags[f'{{cp_moliya_tuz_{i}}}'] = "0,00"
        tags[f'{{cp_vaqt_tuz_{i}}}'] = "0,00"
        
        type_tuz_p = -5.0
        type_tuz_s = uzs_base * (type_tuz_p / 100.0)
        type_narx = uzs_base + type_tuz_s
        tags[f'{{cp_type_tuz_p_{s}}}'] = "-5,00%"
        tags[f'{{cp_type_tuz_s_{s}}}'] = fmt_v(type_tuz_s, "")
        tags[f'{{cp_type_narx_{s}}}'] = fmt_v(type_narx, "")
        
        if a_wear_val < 100.0:
            yosh_tuz_p = (a_wear_val - obj_wear * 100.0) / (100.0 - a_wear_val) * 100.0
        else:
            yosh_tuz_p = 0.0
            
        yosh_tuz_s = type_narx * (yosh_tuz_p / 100.0)
        yosh_narx = type_narx + yosh_tuz_s
        
        tags[f'{{cp_yosh_tuz_p_{s}}}'] = f"{yosh_tuz_p:.2f}%".replace('.', ',')
        tags[f'{{cp_eskirish_tuz_{s}}}'] = f"{yosh_tuz_p:.2f}%".replace('.', ',')
        tags[f'{{cp_eskirish_tuz_{i}}}'] = f"{yosh_tuz_p:.2f}%".replace('.', ',')
        tags[f'{{cp_yosh_narx_{s}}}'] = fmt_v(yosh_narx, "")
        vazn = getattr(analog, 'weight', 0)
        tags[f'{{cp_vazn_{s}}}'] = f"{vazn:.3f}".replace('.', ',')
        
        # Vazn bo'yicha hisoblangan yakuniy narx
        v_narx = yosh_narx * vazn
        tags[f'{{cp_v_narx_{s}}}'] = fmt_v(v_narx, "")
        print(f"DEBUG: Weight based price calculated for analog {i}", flush=True)

        # Professional Template Specific tags mapping
        tags[f'{{a{i}_url}}'] = str(analog.url)
        tags[f'{{analog_{i}_narxi_usd}}'] = fmt_v(usd_narx, "$")
        tags[f'{{analog_{i}_sum}}'] = fmt_v(uzs_base, "")
        tags[f'{{usd_kurs}}'] = fmt_v(usd_rate, "")
        
        # Adjustments % (placeholders for now matching the UI image)
        tags[f'{{muvofik_foiz_{i}}}'] = "0,00"
        tags[f'{{muvofik_narx_{i}}}'] = fmt_v(uzs_base, "")
        tags[f'{{muvofik_koef_{i}}}'] = "1,00"
        tags[f'{{muvofik_ulush_narx_{i}}}'] = fmt_v(v_narx, "")

        # Avariyaviy shikastlanishga tuzatish
        tags[f'{{cp_avariya_tuz_{s}}}'] = "0,00"
        tags[f'{{cp_avariya_narx_{s}}}'] = fmt_v(yosh_narx, "")

        # Kiritilgan tuzatishlar soni (Count non-zero adjustments)
        huquq_tuz, moliya_tuz, vaqt_tuz = 0, 0, 0
        adjs = [huquq_tuz, moliya_tuz, vaqt_tuz, type_tuz_p, yosh_tuz_p]
        count = len([x for x in adjs if x != 0])
        tags[f'{{cp_tuz_soni_{s}}}'] = f"{float(count):.2f}".replace('.', ',')

    # Tuzatishlar yig'indisi
    total_count = 0
    total_v_narx = 0
    for i in range(1, 4):
        val = tags.get(f'{{cp_tuz_soni_a{i}}}', "0,00").replace(',', '.')
        try: total_count += float(val)
        except: pass
        
        # Yakuniy aniq narxni hisoblash (weighted sum)
        v_narx_str = tags.get(f'{{cp_v_narx_a{i}}}', "0,00").replace('$', '').replace(' ', '').replace(',', '.')
        try: total_v_narx += float(v_narx_str)
        except: pass

    tags['{cp_tuz_jami}'] = f"{total_count:.2f}".replace('.', ',')
    tags['{cp_jami_narx}'] = fmt_v(total_v_narx, "")
    tags['{urtacha_qiymat}'] = fmt_v(total_v_narx, "")

    # Avariya ob'yekt uchun
    tags['{cp_avariya_o}'] = "mavjud emas"
    
    # Tovar ko'rinishining yo'qotilishi (Loss of market value) - Usually 0 for standard valuations
    tags['{cp_tovar_o}'] = "0,00"
    tags['{cp_tovar_v_y_o}'] = "0,00"
    for i in range(1, 4):
        s = f"a{i}"
        tags[f'{{cp_tovar_tuz_{s}}}'] = "0,00"
        tags[f'{{cp_tovar_narx_{s}}}'] = tags.get(f'{{cp_avariya_narx_{s}}}', "0,00")
        tags[f'{{cp_tovar_v_y_{s}}}'] = "0,00"
        # Aliases without 'a'
        tags[f'{{cp_tovar_tuz_{i}}}'] = "0,00"
        tags[f'{{cp_tovar_narx_{i}}}'] = tags.get(f'{{cp_avariya_narx_{s}}}', "0,00")
        tags[f'{{cp_tovar_v_y_{i}}}'] = "0,00"
        tags[f'{{cp_tovar_v_y_{s}}}'] = "0,00"

    return tags

def generate_wear_calculation_text(valuation, car_age, obj_mileage, obj_wear, scale_wear, aggregate_wear):
    import math
    df = float(car_age)
    pf = float(obj_mileage) / 1000.0
    omega = (0.07 * df) + (0.0035 * pf)
    exp_val = math.exp(-omega)
    
    act_wear = float(getattr(valuation, 'act_wear_percent', 70.0))
    formula_wear_pct = obj_wear * 100.0
    
    lines = [
        "Baholash ob’yekti uchun ma’lumotlar:",
        f"•\thaqiqiy xizmat muddati — {df:.1f}".replace('.', ',') + " yil;",
        f"•\thaqiqiy bosib o‘tgan masofa — {obj_mileage:,}".replace(',', ' ') + f" km ({pf:.1f}".replace('.', ',') + " ming km).",
        "Hisob-kitob natijasi:",
        f"Ω = 0,07 × {df:.1f}".replace('.', ',') + f" + 0,0035 × {pf:.1f}".replace('.', ',') + f" = {0.07*df:.2f}".replace('.', ',') + f" + {0.0035*pf:.4f}".replace('.', ',') + f" = {omega:.4f}".replace('.', ',') + f";      e^{{-{omega:.4f}}} ≈ {exp_val:.4f}".replace('.', ','),
        f"I = 1 − {exp_val:.4f} = {obj_wear:.4f} = {formula_wear_pct:.2f}%".replace('.', ','),
        "Yuqoridagi ma’lumot va hisob-kitoblardan kelib chiqib, ob’yektning jismoniy eskirishi quyidagicha aniqlandi:",
        f"({act_wear:.1f}% + {scale_wear:.1f}% + {formula_wear_pct:.2f}%) / 3 = {aggregate_wear:.2f}%".replace('.', ','),
        f"Shunday qilib, baholash ob’yektining jamlangan jismoniy eskirishi {aggregate_wear:.2f}% deb qabul qilindi."
    ]
    return "\n".join(lines)

def generate_cost_approach_text(replacement_cost_uzs, aggregate_wear_percent, cost_value_uzs):
    tikl = f"{replacement_cost_uzs:,.2f}".replace(',', ' ').replace('.', ',')
    esk = f"{aggregate_wear_percent:.2f}%".replace('.', ',')
    qoldiq_coef = f"{(1 - aggregate_wear_percent/100.0):.4f}".replace('.', ',')
    final = f"{cost_value_uzs:,.2f}".replace(',', ' ').replace('.', ',')
    
    lines = [
        f"Baholash natijalariga ko‘ra jamlangan jismoniy eskirish {esk} ni tashkil etdi.",
        f"Shuningdek, baholash ob’yektining tiklash qiymati {tikl} so‘m deb qabul qilindi.",
        "Shu holda baholash ob’yektining joriy (qoldiq) qiymati quyidagicha hisoblandi:",
        f"Cqold = {tikl} * (1 – {esk}) = {tikl} * {qoldiq_coef} = {final} so‘m.",
        f"Shunday qilib, baholash ob’yektining xarajat yondashuvida aniqlangan qiymati {final} so‘mni tashkil etdi."
    ]
    return "\n".join(lines)

# End of Gemini analysis functions

def generate_macro_data(valuation):
    return {
        'period_label': '2025 yil yanvar-iyun',
        'rows': [
            ('Yalpi Ichki Mahsulot (YAIM)', '807 937,1 mlrd so‘m', '7,2%', 'Iqtisodiy barqarorlikni ta’minlaydi'),
            ('Chakana savdo aylanmasi', '198 703,1 mlrd so‘m', '9,7%', 'Iste’mol faolligi yuqori'),
            ('Xizmatlar sohasi hajmi', '458 196,9 mlrd so‘m', '13,3%', f'{valuation.car_model} likvidliligini oshiradi'),
            ('Import hajmi', '20,1 mlrd AQSH dollari', '7,0%', 'Raqobat muhiti kuchaymoqda')
        ]
    }

class VehicleAnalogViewSet(viewsets.ModelViewSet):
    from .serializers import VehicleAnalogSerializer
    serializer_class = VehicleAnalogSerializer
    queryset = VehicleAnalog.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        valuation_pk = self.request.query_params.get('valuation')
        if valuation_pk:
            return VehicleAnalog.objects.filter(valuation_id=valuation_pk)
        return VehicleAnalog.objects.all()

    def perform_create(self, serializer):
        valuation_id = self.request.data.get('valuation')
        if not valuation_id:
            valuation_id = self.request.query_params.get('valuation')
        
        from django.shortcuts import get_object_or_404
        valuation = get_object_or_404(VehicleValuation, id=valuation_id)
        serializer.save(valuation=valuation)


class GlobalAnalogViewSet(viewsets.ModelViewSet):
    from .serializers import GlobalAnalogSerializer
    serializer_class = GlobalAnalogSerializer
    queryset = GlobalAnalog.objects.all().order_by('-created_at')
    permission_classes = [permissions.AllowAny] # Set AllowAny or IsAuthenticated. AllowAny is simpler for initial testing.

    def get_queryset(self):
        model_name = self.request.query_params.get('model')
        year = self.request.query_params.get('year')
        qs = self.queryset
        if model_name:
            qs = qs.filter(model_name__icontains=model_name)
        if year:
            qs = qs.filter(year=year)
        return qs

    def perform_create(self, serializer):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = self.request.user if self.request.user.is_authenticated else User.objects.first()
        serializer.save(user=user)


