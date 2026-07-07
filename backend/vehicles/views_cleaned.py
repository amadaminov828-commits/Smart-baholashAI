import os
import datetime
import requests
from django.conf import settings
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import VehicleValuation, VehicleAnalog
from reports.models import ReportDocument, QRCode
from .serializers import VehicleValuationSerializer, OCRDocumentUploadSerializer
from .ocr import extract_vehicle_info, client as genai_client
from google.genai import types
from .scraper import search_analogs
from .docx_generator import fill_docx_template
from valuation_engine.vehicle_math import VehicleMathEngine
from .pdf_generator import convert_docx_to_pdf, protect_pdf
from reports.qr_generator import generate_qr_for_report
from utils.date_utils import format_uzbek_date_long
from django.core.files.storage import default_storage
from django.core.files import File

class VehicleValuationViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleValuationSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def get_queryset(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = self.request.user if self.request.user.is_authenticated else User.objects.first()
        return VehicleValuation.objects.filter(user=user) if user else VehicleValuation.objects.all()
    
    def perform_create(self, serializer):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = self.request.user if self.request.user.is_authenticated else User.objects.first()
        serializer.save(user=user)

    @action(detail=False, methods=['post'], url_path='ocr-upload')
    def ocr_upload(self, request):
        print("OCR Upload started...")
        documents = request.FILES.getlist('documents')
        if not documents:
            print("No documents found in request.FILES")
            return Response({"error": "No files provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        extracted_data = {}
        try:
            for doc in documents:
                print(f"Processing document: {doc.name}")
                path = default_storage.save(doc.name, doc)
                full_path = default_storage.path(path)
                print(f"Saved to: {full_path}")
                
                data = extract_vehicle_info(full_path)
                print(f"Extracted data from {doc.name}: {data}")
                
                for k, v in data.items():
                    if v and str(v) != "Noma'lum":
                        if k not in extracted_data or str(extracted_data[k]) == "Noma'lum" or not extracted_data[k]:
                            extracted_data[k] = v
                    elif k not in extracted_data:
                        extracted_data[k] = v
                        
                default_storage.delete(path)
                print(f"Deleted temp file: {path}")

            return Response({"extracted_data": extracted_data}, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"CRITICAL ERROR in ocr_upload: {str(e)}")
            print(error_trace)
            return Response({"error": str(e), "traceback": error_trace}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='find-analogs')
    def find_analogs(self, request, pk=None):
        valuation = self.get_object()
        
        # Clear existing analogs
        valuation.analogs.all().delete()

        analogs_data = search_analogs(valuation.car_model, valuation.year)
        for data in analogs_data:
            VehicleAnalog.objects.create(valuation=valuation, **data)
            
        return Response({"message": f"{len(analogs_data)} analogs topildi"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='generate-report')
    def generate_report(self, request, pk=None):
        import datetime
        import requests
        import re
        from utils.number_to_words import number_to_uzbek_words
        
        valuation = self.get_object()
        
        # JSHSHIR Extraction (14 digits)
        raw_jshshir = getattr(valuation, 'passport_jshshir', '')
        jshshir = 'Mavjud emas'
        if raw_jshshir:
            match = re.search(r'\d{14}', str(raw_jshshir).replace(" ", ""))
            if match:
                jshshir = match.group(0)
            else:
                jshshir = str(raw_jshshir)
                
        # Default exchange rates
        usd_rate, eur_rate, rub_rate = 12600.0, 14000.0, 140.0
        
        val_date = valuation.valuation_date or datetime.date.today()
        # Format for API: YYYY-MM-DD
        date_str = val_date.strftime('%Y-%m-%d')
        
        try:
            # cbu.uz provides historical data at /uz/arkhiv-kursov-valyut/json/all/{date}/
            cbu_res = requests.get(f'https://cbu.uz/uz/arkhiv-kursov-valyut/json/all/{date_str}/', timeout=1.5)
            if cbu_res.status_code == 200:
                data = cbu_res.json()
                for currency in data:
                    if currency['Ccy'] == 'USD': usd_rate = float(currency['Rate'])
                    if currency['Ccy'] == 'EUR': eur_rate = float(currency['Rate'])
                    if currency['Ccy'] == 'RUB': rub_rate = float(currency['Rate'])
            else:
                # Fallback to current rates if historical fails
                cbu_res_current = requests.get('https://cbu.uz/uz/arkhiv-kursov-valyut/json/', timeout=1.5)
                if cbu_res_current.status_code == 200:
                    data = cbu_res_current.json()
                    for currency in data:
                        if currency['Ccy'] == 'USD': usd_rate = float(currency['Rate'])
                        if currency['Ccy'] == 'EUR': eur_rate = float(currency['Rate'])
                        if currency['Ccy'] == 'RUB': rub_rate = float(currency['Rate'])
        except Exception:
            pass
            
        today_str = datetime.date.today().strftime('%d.%m.%Y')
        val_date_str = val_date.strftime('%d.%m.%Y')
        analogs = list(valuation.analogs.all()[:3])
        while len(analogs) < 3: analogs.append(None)
        a1, a2, a3 = analogs[0], analogs[1], analogs[2]
        
        def g_p(a): return f"{float(a.price):,.0f}" if a else "0"
        def g_s(a): return f"{(float(a.price) * usd_rate):,.0f}" if a else "0"
        def g_u(a): return a.url if a and a.url else "-"
        
        avg_usd = sum(float(a.price) for a in analogs if a) / max(1, len([a for a in analogs if a]))
        avg_sum = round((avg_usd * usd_rate) / 1000) * 1000
        avg_sum_words = number_to_uzbek_words(avg_sum) + " so'm"
        
        try:
            car_age = val_date.year - int(valuation.year)
        except (ValueError, TypeError):
            car_age = 0

        def clean_mileage(m):
            if not m or str(m) == "Noma'lum": return 0
            # Extracts numbers from "120 000 km" or "120000"
            digits = re.sub(r'[^\d]', '', str(m))
            return int(digits) if digits else 0

        obj_mileage = clean_mileage(valuation.mileage)
        obj_wear = VehicleMathEngine.calculate_physical_wear(car_age, obj_mileage)
        
        table_rows = []
        analogs_wear_adjustments = []
        
        v_date_str = val_date.strftime("%d/%m/%Y")
        
        # Add hisobot_raqami for template tagging
        report_context = {
            'hisobot_raqami': valuation.id,
            'hisobot_sanasi': v_date_str,
            # ... existing tags will stay below ...
        }

        # Comparative Value (average from analogs)
        avg_usd = sum(float(a.price) for a in analogs if a) / max(1, len([a for a in analogs if a]))
        comp_value_uzs = avg_usd * usd_rate
        
        for analog in [a1, a2, a3]:
            if analog:
                a_age = car_age 
                a_mileage = clean_mileage(analog.mileage)
                a_wear = VehicleMathEngine.calculate_physical_wear(a_age, a_mileage)
                k_wear = VehicleMathEngine.calculate_wear_adjustment(obj_wear, a_wear)
                analogs_wear_adjustments.append(k_wear)
                
                # Save to DB for record
                analog.wear_percent = a_wear * 100
                analog.wear_adjustment = k_wear * 100
                analog.save()
            else:
                analogs_wear_adjustments.append(0)

        # Weights calculation
        weights = VehicleMathEngine.calculate_weights(analogs_wear_adjustments)
        for i, analog in enumerate([a1, a2, a3]):
            if analog and i < len(weights):
                analog.weight = weights[i]
                analog.save()

        # --- Cost Approach Calculations ---
        replacement_cost_usd = float(valuation.replacement_cost_usd or 13500)
        replacement_cost_uzs = replacement_cost_usd * usd_rate
        
        act_wear = float(valuation.act_wear_percent or 70.0)
        scale_wear = VehicleMathEngine.get_scale_wear(valuation.technical_condition or "Qoniqarli")
        formula_wear_percent = obj_wear * 100.0
        
        aggregate_wear = VehicleMathEngine.calculate_aggregate_wear(act_wear, scale_wear, formula_wear_percent)
        cost_value_uzs = VehicleMathEngine.calculate_residual_value(replacement_cost_uzs, aggregate_wear)
        
        # --- Final Reconciliation ---
        # User example: Comp=12pts (weight 1.0), Cost=0pts (weight 0.0)
        final_value_raw = VehicleMathEngine.calculate_final_weighted_value(comp_value_uzs, cost_value_uzs, 12, 0)
        final_value_rounded = VehicleMathEngine.round_to_nearest_thousand(final_value_raw)
        final_value_words = number_to_uzbek_words(final_value_rounded) + " so'm"
        
        # Save to valuation model
        valuation.formula_wear_percent = formula_wear_percent
        valuation.scale_wear_percent = scale_wear
        valuation.aggregate_wear_percent = aggregate_wear
        valuation.save()

        # Build Professional Table Data
        prof_data = {
            'rows': [
                ("AQSH dollarida taklif etilgan qiymat", ["-", f"${g_p(a1)}", f"${g_p(a2)}", f"${g_p(a3)}"]),
                ("Valyuta kursi (CBU)", ["-", f"{usd_rate:,.2f}", f"{usd_rate:,.2f}", f"{usd_rate:,.2f}"]),
                ("So'mdagi taklif etilgan", ["-", g_s(a1), g_s(a2), g_s(a3)]),
                ("Mulkiy huquqlar", ["To'liq", "To'liq", "To'liq", "To'liq"]),
                ("Vaqt omili", [v_date_str, v_date_str, v_date_str, v_date_str]),
                ("Qiymat turi (Bozor vs Taklif)", ["Bozor", "Taklif", "Taklif", "Taklif"]),
                ("Kiritilgan tuzatish (Qiymat turi)", ["-", "-5.00%", "-5.00%", "-5.00%"]),
                ("Yosh (yil)", [car_age, car_age, car_age, car_age]),
                ("Bosib o'tgan masofasi (km)", [valuation.mileage or 0, (getattr(a1, 'mileage', '0') or '0'), (getattr(a2, 'mileage', '0') or '0'), (getattr(a3, 'mileage', '0') or '0')]),
                ("Jismoniy eskirish (%)", [f"{obj_wear*100:.2f}%", 
                                            f"{(getattr(a1, 'wear_percent', 0) or 0):.2f}%", 
                                            f"{(getattr(a2, 'wear_percent', 0) or 0):.2f}%", 
                                            f"{(getattr(a3, 'wear_percent', 0) or 0):.2f}%"]),
                ("Eskirishga tuzatish", ["-", 
                                            f"{(getattr(a1, 'wear_adjustment', 0) or 0):.2f}%", 
                                            f"{(getattr(a2, 'wear_adjustment', 0) or 0):.2f}%", 
                                            f"{(getattr(a3, 'wear_adjustment', 0) or 0):.2f}%"]),
                ("Vazn koeffisiyenti", ["-", 
                                            f"{(getattr(a1, 'weight', 0) or 0):.3f}", 
                                            f"{(getattr(a2, 'weight', 0) or 0):.3f}", 
                                            f"{(getattr(a3, 'weight', 0) or 0):.3f}"]),
            ]
        }
        
        criteria_data = {
            'rows': [
                ("Baholash maqsadini hisobga olish qobiliyati", 2, 0),
                ("Bozor sharoitlarini hisobga olish qobiliyati", 2, 0),
                ("Ob’yektning fizik va iqtisodiy parametrlarini hisobga olish qobiliyati", 2, 0),
                ("Axborot sifati", 2, 0),
                ("Qo‘llanilgan ma’lumotlarning ishonchliligi", 2, 0),
                ("Hisoblash usulining shaffofligi va takrorlanish imkoniyati", 2, 0),
                ("JAMI BALL", 12, 0),
                ("VAZN KOEFFISIYENTI", "1.00", "0.00")
            ]
        }
        
        recon_data = {
            'rows': [
                ("Baholash qiymati, so'mda", f"{cost_value_uzs:,.2f}", f"{comp_value_uzs:,.2f}"),
                ("Solishtirma og'irlik koeffisiyenti", "0.00", "1.00"),
                ("Baholash yondashuvi ulushi, so'mda", "0.00", f"{comp_value_uzs:,.2f}"),
                ("Yakuniy baholash qiymati, so'mda", "-", f"{final_value_rounded:,.0f}")
            ]
        }

        # 1. Provide context. Everything stringified safely.
        context = {
            'professional_table_data': prof_data,
            'criteria_table_data': criteria_data,
            'reconciliation_table_data': recon_data,
            '{{FISH}}': str(valuation.owner_name or ''),
            '{{MODEL}}': str(valuation.car_model or ''),
            '{{VIN}}': str(valuation.vin_code or ''),
            '{{YEAR}}': str(valuation.year or ''),
            '{{PRICE}}': f"{avg_usd:,.0f} USD",
            '{{PLATE_NUMBER}}': str(valuation.plate_number or ''),
            '{{ENGINE_CAPACITY}}': str(valuation.engine_capacity or ''),

            # Exact custom user template tags mapping
            '{shartnoma_sanasi}': valuation.agreement_date.strftime('%d.%m.%Y') if valuation.agreement_date else today_str,
            '{shartnoma_raqami}': str(valuation.agreement_number or f"{valuation.id:04d}"),
            
            '{hisobot_sanasi}': today_str,
            '{hisobot_sanasi_qisqa}': datetime.date.today().strftime("%d/%m/%Y"),
            '{hisobot_raqami}': str(valuation.id),
            'hisobot_raqami': str(valuation.id),
            '{ishlab_chiqarilgan_yili}': str(valuation.year or ''),
            '{yoshi}': str(car_age),
            '{davlat_raqami}': str(valuation.plate_number or ''),
            '{modeli}': str(valuation.car_model or ''),
            '{baholash_sanasi}': val_date_str,
            '{baholash_sanasi_qisqa}': val_date.strftime("%d/%m/%Y"),
            '{buyurtmachi_fish}': str(valuation.owner_name or ''),
            '{buyurtmachi}': str(valuation.owner_name or ''),
            '{mulk_egasi_fish}': str(valuation.owner_name or ''),
            
            # Shaxsni tasdiqlovchi hujjat va Manzil
            '{mulk_egasi_hujjat_malumoti}': f"Pasport: {getattr(valuation, 'passport_serial', '')}, {getattr(valuation, 'passport_given_by', '')}, {getattr(valuation, 'passport_given_date', '')}",
            '{hujjat_turi}': str(getattr(valuation, 'passport_type', 'O\'zbekiston Respublikasi Fuqarosining ID-kartasi')),
            '{pasport_seriyasi}': str(getattr(valuation, 'passport_serial', '')),
            '{pasport_berilgan_sana}': str(getattr(valuation, 'passport_given_date', '')),
            '{pasport_berilgan_joyi}': str(getattr(valuation, 'passport_given_by', '')),
            '{mulk_egasi_jshshir}': jshshir,
            '{jshshir}': jshshir,
            '{yakuniy_narx}': f"{final_value_rounded:,.0f} UZS",
            '{yakuniy_narx_suzlarda}': final_value_words, 
            
            # Xarajat yondashuvi natijalari
            '{tiklanish_qiymati_usd}': f"${replacement_cost_usd:,.0f}",
            '{tiklanish_qiymati_sum}': f"{replacement_cost_uzs:,.0f}",
            '{jamlangan_eskirish}': f"{aggregate_wear:.2f}%",
            '{xarajat_narxi}': f"{cost_value_uzs:,.0f}",
            '{transport_turi}': str(getattr(valuation, 'vehicle_type', 'Yengil')),
            '{kuzov_raqami}': str(getattr(valuation, 'body_number', valuation.vin_code or '')),
            '{dvigatel_raqami}': str(getattr(valuation, 'engine_number', 'Noma`lum')),
            '{rangi}': str(getattr(valuation, 'color', 'Oq')),
            '{yoqilgi_turi}': str(getattr(valuation, 'fuel_type', 'Benzin')),
            '{dvigatel_quvvati}': str(getattr(valuation, 'engine_horsepower', getattr(valuation, 'engine_capacity', ''))),
            '{dvigatel_hajmi}': str(getattr(valuation, 'engine_capacity', '')),
            '{guvoxnoma_raqami}': str(getattr(valuation, 'tech_passport_serial', getattr(valuation, 'registration_number', ''))),
            '{ruyxatdan_utkazish_raqami}': str(getattr(valuation, 'registration_number', getattr(valuation, 'tech_passport_serial', ''))),
            '{tola_vazni}': str(getattr(valuation, 'full_weight', '')),
            '{yuksiz_vazni}': str(getattr(valuation, 'empty_weight', '')),
            '{orindiqlar_soni}': str(getattr(valuation, 'seats_count', '')),
            '{yurgan_masofasi}': str(getattr(valuation, 'mileage', '0 km')),
            
            '{texnik_holati}': str(getattr(valuation, 'technical_condition', 'Qoniqarli')),
            '{dastlabki_balans_qiymati}': str(getattr(valuation, 'initial_balance_value', '0.00')),
            '{qoldiq_balans_qiymati}': str(getattr(valuation, 'residual_balance_value', '0.00')),
            '{uzatma_qutisi}': str(getattr(valuation, 'transmission_type', '')),
            '{maksimal_tezlik}': str(getattr(valuation, 'top_speed', '')),
            
            '{a1_url}': g_u(a1), '{a2_url}': g_u(a2), '{a3_url}': g_u(a3),
            'a1_url': g_u(a1), 'a2_url': g_u(a2), 'a3_url': g_u(a3),
            '{analog_1_narxi_usd}': g_p(a1), '{analog_2_narxi_usd}': g_p(a2), '{analog_3_narxi_usd}': g_p(a3),
            '{usd_kurs}': f"{usd_rate:,.2f}".replace(',', ' ').replace('.', ','),
            '{usd_kursi}': f"{usd_rate:,.2f}".replace(',', ' ').replace('.', ','),
            '{eur_kursi}': f"{eur_rate:,.2f}".replace(',', ' ').replace('.', ','),
            '{rub_kursi}': f"{rub_rate:,.2f}".replace(',', ' ').replace('.', ','),
            '{analog_1_sum}': g_s(a1), '{analog_2_sum}': g_s(a2), '{analog_3_sum}': g_s(a3),
            '{muvofik_foiz_1}': '0', '{muvofik_foiz_2}': '0', '{muvofik_narx_3}%': '0%',
            '{muvofik_narx_1}': g_s(a1), '{muvofik_narx_2}': g_s(a2), '{muvofik_narx_3}': g_s(a3),
            '{muvofik_koef_1}': '0.33', '{muvofik_koef_2}': '0.33', '{muvofik_koef_3}': '0.34',
            '{muvofik_ulush_narx_1}': g_s(a1), '{muvofik_ulush_narx_2}': g_s(a2), '{muvofik_ulush_narx_3}': g_s(a3),
            '{urtacha_qiymat}': f"{avg_sum:,.0f}",
            'urtacha_qiymat': f"{avg_sum:,.0f}",
            
            # Professional Text Sections
            '{qiyosiy_yondashuv_matni}': "IX.3-bo‘limida asoslanganidek, baholash ob’yekti ikkilamchi avtotransport bozorida yuqori likvidli bo‘lganligi sababli, uning qiymatini aniqlashda Qiyosiy yondashuv qo‘llanildi. Qiyosiy yondashuv bo‘yicha hisob-kitob 'Sotuvlarni to‘g‘ridan-to‘g‘ri qiyoslash usuli' asosida amalga oshirildi.",
            '{eskirish_matni}': f"Jismoniy eskirish darajasi baholash ob’yektining foydalanish boshlangandan so‘nggi xronologik yoshi ({car_age} yil) va bosib o‘tgan masofasini ({valuation.mileage or 0} km) hisobga olgan holda, I=1−e−Ω formulasi orqali hisoblangan. Natijada ob'yektning jismoniy eskirishi {obj_wear*100:.2f}%ni tashkil etdi.",
            '{formula_metodika}': "C = Can × Kfv × Kiz × K1 × K2 × … × Kn + Cdop formulasi asosida, baholash ob’yektiga o‘xshash kamida uchta analog ob’yekt tanlanib, ularning narxlari qiyoslash elementlari bo‘yicha tuzatildi.",
            
            '{iqtisodiy_vaziyat_matni}': generate_economic_analysis(valuation),
            '{bozor_vaziyati_matni}': generate_market_analysis(valuation),
            
            # Title Page & Letter of Transmittal (New Lacetti Example Request)
            '{baholash_sanasi_uz_long}': format_uzbek_date_long(val_date),
            '{hisobot_sanasi_uz_long}': format_uzbek_date_long(datetime.date.today()),
            '{shartnoma_sanasi_uz_long}': format_uzbek_date_long(valuation.agreement_date) if valuation.agreement_date else "",
            '{buyurtmachi_rahbari}': f"{valuation.owner_name} boshqaruv raisiga" if "AJ" in str(valuation.owner_name) else "Rahbariga",
            '{baholovchi_tashkilot}': "“PERCEPTION VALUE” MCHJ",
            '{shartnoma_turi}': "elektron shartnoma"
        }

        template_id = request.data.get('template_id')
        if template_id:
            from reports.models import ReportTemplate
            try:
                template_obj = ReportTemplate.objects.get(id=template_id)
                template_path = template_obj.file.path
            except ReportTemplate.DoesNotExist:
                return Response({"error": "Template not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            os.makedirs('tmp', exist_ok=True)
            template_path = 'tmp/base_template.docx'
            if not os.path.exists(template_path):
                return Response({"error": "Base template (base_template.docx) is missing. Upload professional_shablon to tmp directory."}, status=status.HTTP_404_NOT_FOUND)

        out_docx = f'tmp/report_{valuation.id}.docx'
        out_pdf = f'tmp/report_{valuation.id}.pdf'
        protected_pdf = f'tmp/report_{valuation.id}_protected.pdf'

        # Create Report DB Entry First
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = self.request.user if self.request.user.is_authenticated else User.objects.first()
        
        report = ReportDocument.objects.create(
            user=user,
            object_type='vehicle',
            object_id=valuation.id,
            approach=valuation.method or "qiyosiy"
        )
        
        import re
        import socket
        safe_model = re.sub(r'[^a-zA-Z0-9_\-]', '', str(valuation.car_model).replace(" ", "_")) 
        if not safe_model: safe_model = "Mashina"
        file_name = f"{safe_model}_{int(avg_usd)}_USD_{report.id}"

        # Dyanmically grab local IP for mobile QR access
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = "127.0.0.1"
        finally:
            s.close()
        
        base_url = f"http://{local_ip}:8000"
        qr_file_url = f"{base_url}{settings.MEDIA_URL}reports/{file_name}.pdf" if hasattr(settings, 'MEDIA_URL') else f"{base_url}/media/reports/{file_name}.pdf"
        qr_file = generate_qr_for_report(report.id, verify_url=qr_file_url)
        qr_obj = QRCode.objects.create(report=report, code_image=qr_file)
        qr_image_path = qr_obj.code_image.path

        # 2. Fill DOCX (now with QR)
        fill_docx_template(template_path, out_docx, context, qr_code_path=qr_image_path)
        
        # 3. Convert to PDF and Handle Word Version
        try:
            # Save Raw Word Document First
            with open(out_docx, 'rb') as f:
                report.file.save(f'{file_name}.docx', File(f))
                
            # Note: We overwrite the `file` field with the PDF below, but the docx is safely stored in media.
            # To serve both, we might want to temporarily store the docx url or rename the attribute, 
            # but for now we provide a direct download mechanism based on the report ID in the frontend.
            
            convert_docx_to_pdf(out_docx, out_pdf)
            # 4. Protect PDF
            protect_pdf(out_pdf, protected_pdf, owner_password="admin")
            
            with open(protected_pdf, 'rb') as f:
                report.file.save(f'{file_name}.pdf', File(f))
            
            # cleanup
            os.remove(out_docx)
            if os.path.exists(out_pdf): os.remove(out_pdf)
            os.remove(protected_pdf)

            return Response({
                "message": "Hisobot shakllandi", 
                "report_id": report.id,
                "docx_url": request.build_absolute_uri(report.file.url).replace('.pdf', '.docx')
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            print("ERROR IN GENERATE_REPORT:")
            print(traceback.format_exc())
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

 d e f   g e n e r a t e _ e c o n o m i c _ a n a l y s i s ( v a l u a t i o n ) : 
         i f   n o t   g e n a i _ c l i e n t : 
                 r e t u r n   ' I q t i s o d i y   t a h l i l   m a \ ' l u m o t l a r i   y u k l a n m a d i . ' 
         
         p r o m p t   =   f ' ' ' 
         S e n   p r o f e s s i o n a l   b a h o l a s h   h i s o b o t i   t a h l i l c h i s i s a n .   Q u y i d a g i   a v t o m o b i l   u c h u n   b a h o l a s h   h i s o b o t i n i n g   
         ' V I .   M A M L A K A T   V A   M I N T A Q A D A G I   B A H O L A S H   O B Y E K T I   B I L A N   B O G �L I Q   U M U M I Y   I Q T I S O D I Y   V A Z I Y A T N I N G   T A V S I F I '   
         b o ' l i m i n i   l o t i n   a l i f b o s i d a ,   o ' z b e k   t i l i d a   p r o f e s s i o n a l   d a r a j a d a   y o z i b   b e r i s h i n g   k e r a k . 
         
         A v t o m o b i l :   { { v a l u a t i o n . c a r _ m o d e l } }   ( { { v a l u a t i o n . y e a r } } - y i l ) 
         
         M a t n   t a r k i b i d a   q u y i d a g i l a r   b o ' l i s h i   s h a r t   ( s t a t . u z   d a g i   s o ' n g g i   m a k r o i q t i s o d i y   k o ' r s a t k i c h l a r g a   a s o s l a n ) : 
         V I . 1 .   M a k r o i q t i s o d i y   v a z i y a t   v a   m o l i y a v i y   o m i l l a r   ( Y A I M   o ' s i s h i ,   c h a k a n a   s a v d o ,   x i z m a t l a r   s o h a s i ) . 
         V I . 2 .   A h o l i   d a r o m a d l a r i   v a   i s t e m o l   q o b i l i y a t i   ( I s h   h a q i   o ' s i s h i ,   a v t o k r e d i t l a r   t a ' s i r i ) . 
         
         M a t n   f o r m a t i   f o y d a l a n u v c h i   b e r g a n   s t r u k t u r a g a   ( j a d v a l l a r   v a   b u l l e t   p o i n t l a r )   a y n a n   m o s   b o ' l i s h i   k e r a k . 
         F a q a t   p r o f e s s i o n a l   m a t n n i   q a y t a r   ( q o ' s h i m c h a   i z o h l a r s i z ) . 
         ' ' ' 
         
         t r y : 
                 r e s p o n s e   =   g e n a i _ c l i e n t . m o d e l s . g e n e r a t e _ c o n t e n t ( 
                         m o d e l = ' g e m i n i - 2 . 0 - f l a s h ' , 
                         c o n t e n t s = [ p r o m p t ] , 
                         c o n f i g = t y p e s . G e n e r a t e C o n t e n t C o n f i g ( t e m p e r a t u r e = 0 . 2 ) 
                 ) 
                 r e t u r n   r e s p o n s e . t e x t 
         e x c e p t   E x c e p t i o n   a s   e : 
                 p r i n t ( f ' E c o n o m i c   a n a l y s i s   g e n e r a t i o n   e r r o r :   { { e } } ' ) 
                 r e t u r n   ' I q t i s o d i y   t a h l i l   j a r a y o n i d a   x a t o l i k   y u z   b e r d i . ' 
 
 d e f   g e n e r a t e _ m a r k e t _ a n a l y s i s ( v a l u a t i o n ) : 
         i f   n o t   g e n a i _ c l i e n t : 
                 r e t u r n   ' B o z o r   t a h l i l i   m a \ ' l u m o t l a r i   y u k l a n m a d i . ' 
         
         p r o m p t   =   f ' ' ' 
         S e n   p r o f e s s i o n a l   a v t o - b o z o r   t a h l i l c h i s i s a n .   Q u y i d a g i   a v t o m o b i l   u c h u n   b a h o l a s h   h i s o b o t i n i n g   
         ' V I I .   B A H O L A S H   O B Y E K T I   T E G I S H L I   B O L G A N   T A R M O Q   V A   B O Z O R N I N G   T A V S I F I '   
         b o ' l i m i n i   l o t i n   a l i f b o s i d a ,   o ' z b e k   t i l i d a   p r o f e s s i o n a l   d a r a j a d a   y o z i b   b e r i s h i n g   k e r a k . 
         
         A v t o m o b i l :   { { v a l u a t i o n . c a r _ m o d e l } }   ( { { v a l u a t i o n . y e a r } } - y i l ) 
         
         M a t n   t a r k i b i d a   q u y i d a g i l a r   b o ' l i s h i   s h a r t : 
         V I I . 1 .   B o z o r   t e n d e n s i y a l a r i   v a   r a q o b a t   m u h i t i   ( U z A u t o   M o t o r s   s o t u v l a r i ,   i m p o r t   o ' s i s h i ,   B Y D   v a   K i a   t a ' s i r i ) . 
         V I I . 2 .   M o d e l l a r n i n g   q i y m a t g a   t a s i r   e t u v c h i   o z i g a   x o s   x u s u s i y a t l a r i   ( F u n k s i o n a l   e s k i r i s h ,   l i k v i d l i l i k ) . 
         
         M a t n   f o r m a t i   f o y d a l a n u v c h i   b e r g a n   s t r u k t u r a g a   ( b u l l e t   p o i n t l a r   v a   q a l i n   h a r f   b i l a n   a j r a t i l g a n   b a n d l a r )   a y n a n   m o s   b o ' l i s h i   k e r a k . 
         F a q a t   p r o f e s s i o n a l   m a t n n i   q a y t a r   ( q o ' s h i m c h a   i z o h l a r s i z ) . 
         ' ' ' 
         
         t r y : 
                 r e s p o n s e   =   g e n a i _ c l i e n t . m o d e l s . g e n e r a t e _ c o n t e n t ( 
                         m o d e l = ' g e m i n i - 2 . 0 - f l a s h ' , 
                         c o n t e n t s = [ p r o m p t ] , 
                         c o n f i g = t y p e s . G e n e r a t e C o n t e n t C o n f i g ( t e m p e r a t u r e = 0 . 2 ) 
                 ) 
                 r e t u r n   r e s p o n s e . t e x t 
         e x c e p t   E x c e p t i o n   a s   e : 
                 p r i n t ( f ' M a r k e t   a n a l y s i s   g e n e r a t i o n   e r r o r :   { { e } } ' ) 
                 r e t u r n   ' B o z o r   t a h l i l i   j a r a y o n i d a   x a t o l i k   y u z   b e r d i . ' 
  
 
