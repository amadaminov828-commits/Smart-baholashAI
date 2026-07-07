"use client";

import { useState, useEffect, Suspense } from 'react';
import { api } from '@/services/api';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from '@/i18n/I18nProvider';
import {
    Camera,
    Search,
    FileText,
    CheckCircle2,
    FileDown,
    ExternalLink,
    Upload,
    FileSearch,
    ArrowRight,
    Database,
    ShieldCheck,
    Gauge,
    Car,
    User,
    Calendar,
    Hash,
    Plus,
    Zap,
    CreditCard,
    Clock,
    AlertCircle,
    Download,
    Edit,
    Trash2,
    X,
    Settings2
} from 'lucide-react';

const getMediaUrl = (path: string | null | undefined) => {
    if (!path) return '#';
    if (path.startsWith('http')) return path;
    const cleanPath = path.startsWith('/') ? path.substring(1) : path;
    return `/${cleanPath}`;
};

const labelMap: Record<string, string> = {
    owner_name: "Egasi (F.I.Sh)",
    passport_serial: "Pasport seriyasi",
    passport_type: "Hujjat turi",
    passport_given_date: "Berilgan sanasi",
    passport_jshshir: "JShShIR",
    passport_given_by: "Kim tomonidan berilgan",
    region: "Viloyat",
    district: "Tuman",
    client_company_name: "Kompaniya nomi",
    client_company_account: "Hisob raqami (20 xonali)",
    client_company_inn: "INN (STIR - 9 xonali)",
    client_company_oked: "OKED (5 xonali)",
    client_company_mfo: "MFO (5 xonali)",
    client_company_bank: "Bank nomi",
    client_company_address: "Kompaniya manzili",
    car_model: "Avtomobil rusumi",
    plate_number: "Davlat raqami",
    year: "Ishlab chiqarilgan yili",
    vin_code: "VIN kod",
    engine_capacity: "Dvigatel hajmi",
    engine_horsepower: "Dvigatel quvvati (ot kuchi)",
    engine_number: "Dvigatel raqami",
    body_number: "Kuzov raqami",
    color: "Rangi",
    vehicle_type: "Transport turi",
    full_weight: "To'la vazni (kg)",
    empty_weight: "Yuksiz vazni (kg)",
    seats_count: "O'rindiqlar soni",
    fuel_type: "Yoqilg'i turi",
    tech_passport_serial: "Guvohnoma seriyasi",
    tech_passport_owner: "Tex-pasport egasi",
    registration_number: "Ro'yxatdan o'tkazish raqami",
    report_number: "Hisobot raqami",
    agreement_number: "Shartnoma raqami",
    agreement_date: "Shartnoma sanasi"
};

function VehicleModuleInner() {
    const { t } = useTranslation();
    const router = useRouter();
    const searchParams = useSearchParams();
    const editId = searchParams?.get('edit');
    const [me, setMe] = useState<any>(null);
    const [step, setStep] = useState(1);
    const [files, setFiles] = useState<File[]>([]);
    const [extractedData, setExtractedData] = useState<any>(null);
    const [analogs, setAnalogs] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [sending, setSending] = useState(false);

    useEffect(() => {
        api.get(`users/me?t=${Date.now()}`).then(res => setMe(res.data)).catch(() => {
            window.location.href = '/login';
        });
    }, []);

    // Load existing data if editing
    useEffect(() => {
        if (editId) {
            setLoading(true);
            api.get(`/vehicles/valuations/${editId}/`)
                .then(res => {
                    const data = res.data;
                    setValuationId(data.id);
                    setExtractedData(data);
                    setAnalogs(data.analogs || []);
                    // Check status to determine step
                    if (data.status === 'approved') setStep(5);
                    else if (data.status === 'verifying' || data.status === 'payment_pending') setStep(4);
                    else setStep(2); 
                })
                .catch(err => {
                    console.error("Failed to load valuation for edit", err);
                })
                .finally(() => setLoading(false));
        }
    }, [editId]);

    const [valuationId, setValuationId] = useState<number | null>(null);
    const [templates, setTemplates] = useState<any[]>([]);
    const [reportData, setReportData] = useState<any>(null);
    const [reportDocxUrl, setReportDocxUrl] = useState<string | null>(null);
    const [templateFile, setTemplateFile] = useState<File | null>(null);
    const [uploadingTemplate, setUploadingTemplate] = useState(false);
    const [selectedTemplate, setSelectedTemplate] = useState<number | null>(null);
    const [entityType, setEntityType] = useState<'physical' | 'legal'>('physical');
    const [method, setMethod] = useState<'qiyosiy' | 'xarajat' | 'daromad'>('qiyosiy');
    const [validationErrors, setValidationErrors] = useState<string[]>([]);
    const [flaggedFields, setFlaggedFields] = useState<string[]>([]);
    
    // Payment states
    const [receiptFile, setReceiptFile] = useState<File | null>(null);
    const [paymentSubmitting, setPaymentSubmitting] = useState(false);
    const [paymentTab, setPaymentTab] = useState<'auto' | 'manual'>('auto');
    const [showPaymentSimulator, setShowPaymentSimulator] = useState<'click' | 'payme' | null>(null);
    const [simulating, setSimulating] = useState(false);

    const [fetchingSpecs, setFetchingSpecs] = useState(false);
    const [specsMessage, setSpecsMessage] = useState<{ text: string, type: 'success' | 'error' | 'info' } | null>(null);

    const handleFetchStandardSpecs = async () => {
        const model = extractedData?.car_model;
        if (!model || model === "Noma'lum" || model.trim() === "") {
            setSpecsMessage({ text: "Iltimos, avval avtomobil rusumini kiriting!", type: 'error' });
            setTimeout(() => setSpecsMessage(null), 3000);
            return;
        }

        setFetchingSpecs(true);
        setSpecsMessage({ text: "Katalogdan standart texnik ko'rsatkichlar olinmoqda...", type: 'info' });
        try {
            const res = await api.get(`/vehicles/valuations/get-standard-specs/?model=${encodeURIComponent(model)}`);
            const specs = res.data;
            if (specs) {
                setExtractedData((prev: any) => ({
                    ...prev,
                    engine_capacity: specs.engine_capacity,
                    engine_horsepower: specs.engine_horsepower,
                    seats_count: specs.seats_count,
                    empty_weight: specs.empty_weight,
                    full_weight: specs.full_weight,
                    fuel_type: specs.fuel_type,
                }));
                // Clear any flags on specs fields
                setFlaggedFields((prev) => prev.filter(f => ![
                    'engine_capacity', 'engine_horsepower', 'seats_count', 
                    'empty_weight', 'full_weight', 'fuel_type'
                ].includes(f)));
                setSpecsMessage({ text: "Standart zavod texnik ko'rsatkichlari muvaffaqiyatli to'ldirildi! ⚡", type: 'success' });
            }
        } catch (err) {
            console.error("Specs fetch failed", err);
            setSpecsMessage({ text: "Texnik ko'rsatkichlarni yuklashda xatolik yuz berdi.", type: 'error' });
        } finally {
            setFetchingSpecs(false);
            setTimeout(() => setSpecsMessage(null), 4000);
        }
    };

    // Analog CRUD States & Methods
    const [editingAnalog, setEditingAnalog] = useState<any | null>(null);
    const [showAnalogModal, setShowAnalogModal] = useState(false);
    const [analogForm, setAnalogForm] = useState({
        source: 'OLX',
        model_name: '',
        year: new Date().getFullYear(),
        engine_capacity: '1.5',
        mileage: '50000',
        price: '8000',
        location: 'Toshkent',
        url: '',
        transmission: 'Mexanika',
        color: 'Oq',
        body_type: 'Sedan'
    });

    const [globalSearchQuery, setGlobalSearchQuery] = useState('');
    const [globalSearchResults, setGlobalSearchResults] = useState<any[]>([]);
    const [searchingGlobal, setSearchingGlobal] = useState(false);

    const handleSearchGlobalAnalogs = async () => {
        if (!globalSearchQuery.trim()) return;
        setSearchingGlobal(true);
        try {
            const res = await api.get(`/vehicles/global-analogs/?model=${encodeURIComponent(globalSearchQuery)}`);
            setGlobalSearchResults(res.data || []);
        } catch (err) {
            console.error("Global search failed:", err);
        } finally {
            setSearchingGlobal(false);
        }
    };

    const handleSelectGlobalAnalog = (gAnalog: any) => {
        setAnalogForm({
            source: gAnalog.source || 'OLX',
            model_name: gAnalog.model_name || '',
            year: gAnalog.year || new Date().getFullYear(),
            engine_capacity: gAnalog.engine_capacity || '1.5',
            mileage: gAnalog.mileage || '0',
            price: String(gAnalog.price) || '0',
            location: gAnalog.location || 'Toshkent',
            url: gAnalog.url || '',
            transmission: gAnalog.transmission || 'Mexanika',
            color: gAnalog.color || 'Oq',
            body_type: gAnalog.body_type || 'Sedan'
        });
        setGlobalSearchResults([]);
    };

    const handleDeleteAnalog = async (analogId: number) => {
        if (!confirm("Haqiqatdan ham ushbu analogni o'chirmoqchimisiz?")) return;
        try {
            await api.delete(`/vehicles/analogs/${analogId}/`);
            setAnalogs(prev => prev.filter(a => a.id !== analogId));
        } catch (e) {
            alert("Analog o'chirishda xatolik yuz berdi");
        }
    };

    const handleOpenAddAnalog = () => {
        setEditingAnalog(null);
        setAnalogForm({
            source: 'OLX',
            model_name: extractedData?.car_model || '',
            year: parseInt(extractedData?.year) || new Date().getFullYear(),
            engine_capacity: extractedData?.engine_capacity || '1.5',
            mileage: '50000',
            price: '8000',
            location: extractedData?.region || 'Toshkent',
            url: '',
            transmission: 'Mexanika',
            color: 'Oq',
            body_type: 'Sedan'
        });
        setShowAnalogModal(true);
    };

    const handleOpenEditAnalog = (analog: any) => {
        setEditingAnalog(analog);
        setAnalogForm({
            source: analog.source || 'OLX',
            model_name: analog.model_name || '',
            year: analog.year || new Date().getFullYear(),
            engine_capacity: analog.engine_capacity || '1.5',
            mileage: analog.mileage || '0',
            price: String(analog.price) || '0',
            location: analog.location || 'Toshkent',
            url: analog.url || '',
            transmission: analog.transmission || 'Mexanika',
            color: analog.color || 'Oq',
            body_type: analog.body_type || 'Sedan'
        });
        setShowAnalogModal(true);
    };

    const handleSaveAnalog = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!valuationId) return;
        setLoading(true);
        try {
            const payload = {
                ...analogForm,
                valuation: valuationId,
                price: parseFloat(analogForm.price) || 0,
                year: parseInt(String(analogForm.year)) || new Date().getFullYear()
            };
            if (editingAnalog) {
                // UPDATE
                const res = await api.put(`/vehicles/analogs/${editingAnalog.id}/`, payload);
                setAnalogs(prev => prev.map(a => a.id === editingAnalog.id ? res.data : a));
            } else {
                // CREATE
                const res = await api.post(`/vehicles/analogs/`, payload);
                setAnalogs(prev => [...prev, res.data]);
            }
            setShowAnalogModal(false);
        } catch (e: any) {
            alert("Saqlashda xatolik: " + JSON.stringify(e.response?.data || e.message));
        }
        setLoading(false);
    };

    const fetchTemplates = () => {
        api.get('/templates/').then(res => {
            const vehicleTemplates = res.data
                .filter((t: any) => t.object_type === 'vehicle')
                .sort((a: any, b: any) => b.id - a.id);
            setTemplates(vehicleTemplates);
            setSelectedTemplate((prev) => {
                if (prev) return prev;
                if (vehicleTemplates.length > 0) return vehicleTemplates[0].id;
                return null;
            });
        }).catch(err => console.error(err));
    };

    useEffect(() => {
        if (step === 3) fetchTemplates();
    }, [step]);

    const handleFileUpload = async () => {
        setLoading(true);
        const formData = new FormData();
        files.forEach(f => formData.append('documents', f));

        try {
            const valRes = await api.post('/vehicles/valuations/', { method: 'qiyosiy' });
            const vId = valRes.data.id;
            setValuationId(vId);
            const res = await api.post('/vehicles/valuations/ocr-upload/', formData);
            const data = res.data.extracted_data || {};
            const flagged = res.data.flagged_fields || [];
            setFlaggedFields(flagged);
            
            const updatedData = { 
                ...data,
                report_number: data.report_number || "",
                agreement_number: data.agreement_number || "",
            };
            if (data.agreement_date) {
                updatedData.agreement_date = data.agreement_date;
            }
            setExtractedData({
                ...updatedData,
                agreement_date: data.agreement_date || "" // Keep string for UI state
            });
            const payload = sanitizeDataForApi(updatedData);
            await api.patch(`/vehicles/valuations/${vId}/`, payload);
            setStep(2);
        } catch (e: any) {
            console.warn("Fayl yuklashda xatolik yuz berdi:", e.response?.data || e);
            const errorMsg = e.response?.data?.error || 
                             e.response?.data?.details || 
                             (e.response?.data ? JSON.stringify(e.response.data) : "") || 
                             e.message || 
                             "Noma'lum xatolik";
            alert("Xato yuz berdi: " + errorMsg);
        }
        setLoading(false);
    };

    const handleTemplateUpload = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!templateFile) return;
        setUploadingTemplate(true);
        try {
            const fd = new FormData();
            fd.append('name', `Mening Andozam`);
            fd.append('file', templateFile);
            fd.append('object_type', 'vehicle');
            const res = await api.post('/templates/', fd);
            setUploadingTemplate(false);
            setTemplateFile(null);
            if (res.data && res.data.id) setSelectedTemplate(res.data.id);
            fetchTemplates();
        } catch (e) {
            setUploadingTemplate(false);
        }
    };

    const handleFieldChange = (key: string, val: string) => {
        setExtractedData((prev: any) => ({ ...prev, [key]: val }));
        setFlaggedFields((prev) => prev.filter(f => f !== key));
        setValidationErrors([]);
    };

    const sanitizeDataForApi = (data: any) => {
        const payload = { ...data };
        // Ensure year is integer
        if (payload.year) payload.year = parseInt(payload.year) || null;
        
        // Convert DD.MM.YYYY to YYYY-MM-DD for agreement_date
        if (payload.agreement_date) {
            const dateStr = String(payload.agreement_date).trim();
            if (/^\d{2}[.\-\/]\d{2}[.\-\/]\d{4}$/.test(dateStr)) {
                const parts = dateStr.split(/[.\-\/]/);
                payload.agreement_date = `${parts[2]}-${parts[1]}-${parts[0]}`;
            } else if (!/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
                payload.agreement_date = null; // Invalid date format, prevent DRF 400
            }
        } else {
            payload.agreement_date = null;
        }
        return payload;
    };

    const handleFindAnalogs = async () => {
        if (!valuationId) return;
        
        // Advanced frontend validation
        const errors: string[] = [];
        
        const clientType = extractedData.client_type || 'physical';
        if (clientType === 'legal') {
            const companyName = String(extractedData.client_company_name || '').trim();
            if (!companyName) {
                errors.push("Kompaniya nomi kiritilishi shart!");
            }
            const inn = String(extractedData.client_company_inn || '').replace(/\s/g, '');
            if (!inn) {
                errors.push("INN (STIR) kiritilishi shart!");
            } else if (inn.length !== 9 || /\D/.test(inn)) {
                errors.push(`INN xato kiritilgan (9 ta raqam bo'lishi shart, hozir: ${inn.length} ta raqam)!`);
            }
            const account = String(extractedData.client_company_account || '').replace(/\s/g, '');
            if (!account) {
                errors.push("Hisob raqami kiritilishi shart!");
            } else if (account.length !== 20 || /\D/.test(account)) {
                errors.push(`Hisob raqami xato kiritilgan (20 ta raqam bo'lishi shart, hozir: ${account.length} ta raqam)!`);
            }
            const mfo = String(extractedData.client_company_mfo || '').replace(/\s/g, '');
            if (!mfo) {
                errors.push("MFO kiritilishi shart!");
            } else if (mfo.length !== 5 || /\D/.test(mfo)) {
                errors.push(`MFO xato kiritilgan (5 ta raqam bo'lishi shart, hozir: ${mfo.length} ta raqam)!`);
            }
        } else {
            const jshshir = String(extractedData.passport_jshshir || '').replace(/\s/g, '');
            if (!jshshir || jshshir === "Noma'lum") {
                errors.push("JShShIR (Jismoniy shaxsning shaxsiy identifikatsiya raqami) kiritilishi shart!");
            } else if (jshshir.length !== 14 || /\D/.test(jshshir)) {
                errors.push(`JShShIR xato kiritilgan (14 ta raqam bo'lishi shart, hozir: ${jshshir.length} ta raqam)!`);
            }
            
            const owner = String(extractedData.owner_name || '').trim();
            if (!owner || owner === "Noma'lum") {
                errors.push("Egasi (F.I.Sh) kiritilishi shart!");
            }
        }
        
        const vin = String(extractedData.vin_code || '').replace(/\s/g, '').toUpperCase();
        if (!vin || vin === "Noma'lum") {
            errors.push("VIN kod (kuzov raqami) kiritilishi shart!");
        } else if (vin.length !== 17) {
            errors.push(`VIN kod xato kiritilgan (17 ta belgi bo'lishi shart, hozir: ${vin.length} ta belgi)!`);
        }
        
        const serial = String(extractedData.tech_passport_serial || '').replace(/\s/g, '').toUpperCase();
        if (!serial || serial === "Noma'lum") {
            errors.push("Guvohnoma seriyasi kiritilishi shart!");
        } else if (!/^[A-Z]{2,3}\d{6,8}$/.test(serial)) {
            errors.push("Guvohnoma seriyasi formati noto'g'ri (masalan: VLF0003414 yoki VL0003414)!");
        }
        
        const plate = String(extractedData.plate_number || '').replace(/\s/g, '').toUpperCase();
        if (!plate || plate === "Noma'lum") {
            errors.push("Davlat raqami kiritilishi shart!");
        } else if (plate.length !== 8) {
            errors.push("Davlat raqami formati noto'g'ri (8 ta belgi bo'lishi shart, masalan: 40O205PA)!");
        }
        
        const year = parseInt(String(extractedData.year || '')) || 0;
        const currentYear = new Date().getFullYear();
        if (!year) {
            errors.push("Ishlab chiqarilgan yili kiritilishi shart!");
        } else if (year < 1900 || year > currentYear + 1) {
            errors.push(`Ishlab chiqarilgan yili noto'g'ri (1900 dan ${currentYear + 1} gacha bo'lishi shart)!`);
        }
        
        if (errors.length > 0) {
            setValidationErrors(errors);
            const container = document.getElementById("step2-container");
            if (container) {
                container.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
            return;
        }
        
        setLoading(true);
        try {
            const payload = sanitizeDataForApi(extractedData);
            await api.patch(`/vehicles/valuations/${valuationId}/`, payload);
            await api.post(`/vehicles/valuations/${valuationId}/find-analogs/`, { method });
            const res = await api.get(`/vehicles/valuations/${valuationId}/`);
            setAnalogs(res.data.analogs || []);
            setStep(3);
        } catch (e: any) {
            alert(`Xato: ${e.response?.data?.error || JSON.stringify(e.response?.data) || "Analoglar topilmadi"}`);
        }
        setLoading(false);
    };

    const handleGoToPayment = async () => {
        if (!valuationId) return;
        setLoading(true);
        try {
            // Sanitize data: remove fields that DRF might reject in PATCH
            const { id, user, created_at, analogs, report_file_pdf, report_file_docx, qr_url, assigned_to, ...validData } = extractedData;
            
            const payload = sanitizeDataForApi(validData);

            // Save state and set status to payment_pending
            await api.patch(`/vehicles/valuations/${valuationId}/`, { 
                ...payload, 
                status: 'payment_pending' 
            });
            setStep(4);
        } catch (e: any) {
            console.error("Submission error:", e.response?.data);
            alert("Ma'lumotlarni saqlashda xatolik yuz berdi: " + (e.response?.data?.error || JSON.stringify(e.response?.data) || "Noma'lum"));
        }
        setLoading(false);
    };

    const handleSubmitReceipt = async () => {
        if (!valuationId || !receiptFile) return;
        setPaymentSubmitting(true);
        try {
            const fd = new FormData();
            fd.append('payment_receipt', receiptFile);
            fd.append('status', 'verifying');
            const res = await api.patch(`/vehicles/valuations/${valuationId}/`, fd);
            
            // If the backend auto-approved it (new logic), go straight to report generation
            if (res.data && res.data.status === 'approved') {
                await generateReport();
            } else {
                alert("Chek yuklandi. Admin tasdiqlashini kuting.");
                router.push('/');
            }
        } catch (e) {
            alert("Chek yuklashda xatolik");
        }
        setPaymentSubmitting(false);
    };

    const handleSimulatePayment = async (gateway: 'click' | 'payme') => {
        if (!valuationId) return;
        setSimulating(true);
        try {
            const res = await api.post(`/vehicles/valuations/${valuationId}/simulate-payment/`, {
                gateway
            });
            if (res.data && res.data.status === 'approved') {
                setShowPaymentSimulator(null);
                await generateReport();
            }
        } catch (e: any) {
            alert("To'lovda xatolik yuz berdi: " + (e.response?.data?.error || "Noma'lum"));
        } finally {
            setSimulating(false);
        }
    };

    const generateReport = async () => {
        if (!valuationId) return;
        setLoading(true);
        try {
            const res = await api.post(`/vehicles/valuations/${valuationId}/generate-report/`, {
                template_id: selectedTemplate,
                entity_type: entityType
            });
            setReportData(res.data);
            if (res.data.docx_url) setReportDocxUrl(res.data.docx_url);
            setStep(5);
        } catch (e: any) {
            alert("Xato");
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen bg-[#0a0f1c] text-slate-200 py-12 px-6 relative overflow-hidden font-sans">
            <div className="max-w-5xl mx-auto relative z-10">
                {/* Dashboard Header */}
                <div className="flex justify-between items-center mb-10 px-4">
                    <span className="text-xl font-black tracking-tight text-white select-none">
                        SMART<span className="text-blue-500">BAHOLASH</span>
                    </span>
                    
                    <Link href="/settings" className="inline-flex items-center gap-2 px-5 py-2.5 bg-slate-900 border border-white/5 hover:border-blue-500/30 rounded-xl text-slate-300 hover:text-white transition-all font-black text-xs shadow-md">
                        <Settings2 size={15} />
                        SOZLAMALAR
                    </Link>
                </div>

                {/* Steps Navigation */}
                <div className="relative mb-16 px-4">
                    <div className="flex items-center justify-between relative z-10">
                        {[
                            { s: 1, l: 'Yuklash', i: <Camera size={20} /> },
                            { s: 2, l: 'Tahrirlash', i: <FileSearch size={20} /> },
                            { s: 3, l: 'Analoglar', i: <Database size={20} /> },
                            { s: 4, l: 'To\'lov', i: <CreditCard size={20} /> },
                            { s: 5, l: 'Tayyor', i: <CheckCircle2 size={20} /> }
                        ].map((item) => (
                            <div key={item.s} className="flex flex-col items-center gap-3 group">
                                <div className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-500 border-2 ${step >= item.s ? 'bg-blue-600 border-blue-400 text-white shadow-[0_0_20px_rgba(37,99,235,0.4)]' : 'bg-slate-900 border-slate-700 text-slate-500'}`}>
                                    {item.i}
                                </div>
                                <span className={`text-[10px] font-black uppercase tracking-widest ${step >= item.s ? 'text-blue-400' : 'text-slate-600'}`}>{item.l}</span>
                            </div>
                        ))}
                    </div>
                </div>

                <AnimatePresence mode="wait">
                    {step === 1 && (
                        <motion.div key="s1" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-slate-900/40 p-12 rounded-[40px] border border-white/5 text-center">
                            <h2 className="text-4xl font-black text-white mb-3">Hujjatlarni Yuklang</h2>
                            <p className="text-slate-400 mb-8">Texpasport va Pasport rasmlarini birgalikda yuklang.</p>
                            <label className="block mb-10">
                                <div className="border-2 border-dashed border-slate-700 rounded-[30px] p-16 hover:border-blue-500 transition-all cursor-pointer">
                                    <Upload size={40} className="mx-auto mb-4 text-slate-500" />
                                    <p className="text-xl font-bold">Fayllarni tanlash</p>
                                    <input type="file" multiple accept="image/*,.pdf" className="hidden" onChange={(e) => setFiles(Array.from(e.target.files || []))} />
                                </div>
                            </label>
                            {files.length > 0 && <p className="mb-6 text-blue-400 font-bold">{files.length} ta fayl tanlandi</p>}
                            <button onClick={handleFileUpload} disabled={loading || files.length === 0} className="w-full py-6 bg-blue-600 rounded-2xl font-black text-2xl shadow-xl disabled:opacity-50">
                                {loading ? 'TAHLIL QILINMOQDA...' : 'BOSHLASH'}
                            </button>
                        </motion.div>
                    )}

                    {step === 2 && extractedData && (() => {
                        const clientType = extractedData.client_type || 'physical';
                        const visibleFields = clientType === 'legal'
                            ? [
                                'client_company_name', 'client_company_inn', 'client_company_account',
                                'client_company_oked', 'client_company_mfo', 'client_company_bank',
                                'client_company_address',
                                'car_model', 'plate_number', 'year', 'vin_code', 'engine_capacity', 
                                'engine_horsepower', 'engine_number', 'body_number', 'color', 
                                'vehicle_type', 'full_weight', 'empty_weight', 'seats_count', 
                                'fuel_type', 'tech_passport_serial', 'tech_passport_owner', 
                                'registration_number', 'report_number', 'agreement_number', 
                                'agreement_date'
                              ]
                            : [
                                'owner_name', 'passport_serial', 'passport_type', 'passport_given_date',
                                'passport_given_by', 'passport_jshshir', 'region', 'district',
                                'car_model', 'plate_number', 'year', 'vin_code', 'engine_capacity', 
                                'engine_horsepower', 'engine_number', 'body_number', 'color', 
                                'vehicle_type', 'full_weight', 'empty_weight', 'seats_count', 
                                'fuel_type', 'tech_passport_serial', 'tech_passport_owner', 
                                'registration_number', 'report_number', 'agreement_number', 
                                'agreement_date'
                              ];
                        
                        return (
                            <motion.div id="step2-container" key="s2" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-slate-900/40 p-8 rounded-[40px] border border-white/5">
                                <h2 className="text-3xl font-black mb-8">Ma'lumotlarni tekshiring</h2>
                                
                                {/* Buyurtmachi Turi Selector */}
                                <div className="mb-8 p-6 bg-slate-950/80 rounded-3xl border border-white/5">
                                    <label className="text-[10px] font-black uppercase tracking-wider text-slate-500 mb-3 block">
                                        Buyurtmachi Turi
                                    </label>
                                    <div className="grid grid-cols-2 gap-4">
                                        <button
                                            type="button"
                                            onClick={() => handleFieldChange('client_type', 'physical')}
                                            className={`py-4 rounded-xl border font-bold text-sm transition-all flex items-center justify-center gap-2 ${
                                                clientType === 'physical'
                                                    ? 'bg-blue-600/20 border-blue-500 text-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.15)]'
                                                    : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                                            }`}
                                        >
                                            👤 Jismoniy shaxs
                                        </button>
                                        <button
                                            type="button"
                                            onClick={() => handleFieldChange('client_type', 'legal')}
                                            className={`py-4 rounded-xl border font-bold text-sm transition-all flex items-center justify-center gap-2 ${
                                                clientType === 'legal'
                                                    ? 'bg-blue-600/20 border-blue-500 text-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.15)]'
                                                    : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                                            }`}
                                        >
                                            🏢 Yuridik shaxs
                                        </button>
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                                    {visibleFields.map(k => {
                                        const isFlagged = flaggedFields.includes(k);
                                        const rawVal = extractedData[k];
                                        const displayVal = rawVal !== null && rawVal !== undefined ? String(rawVal) : '';
                                        return (
                                            <div key={k} className="transition-all duration-300">
                                                <div className="flex justify-between items-center mb-1">
                                                    <label className={`text-[10px] font-black uppercase ml-2 block transition-colors duration-300 ${isFlagged ? 'text-red-400' : 'text-slate-500'}`}>
                                                        {labelMap[k] || k}
                                                    </label>
                                                    {k === 'car_model' && (
                                                        <button 
                                                            type="button"
                                                            onClick={handleFetchStandardSpecs}
                                                            disabled={fetchingSpecs}
                                                            className="text-[9px] font-black text-emerald-400 hover:text-emerald-300 uppercase tracking-widest transition-all duration-300 bg-emerald-500/10 px-2.5 py-1.5 rounded-lg border border-emerald-500/20 hover:bg-emerald-500/20 cursor-pointer outline-none active:scale-95 mr-2"
                                                        >
                                                            {fetchingSpecs ? "Olinmoqda..." : "🔄 KATALOGDAN TO'LDIRISH"}
                                                        </button>
                                                    )}
                                                    {isFlagged && k !== 'car_model' && (
                                                        <span className="text-[9px] font-black text-red-500 uppercase tracking-widest animate-pulse mr-2">
                                                            ⚠️ OCR XATOLIK EHTIMOLI!
                                                        </span>
                                                    )}
                                                </div>
                                                <input 
                                                    type="text" 
                                                    value={displayVal} 
                                                    onChange={(e) => handleFieldChange(k, e.target.value)} 
                                                    className={`w-full px-5 py-3 rounded-xl outline-none font-bold transition-all duration-300 border ${
                                                        isFlagged 
                                                            ? 'bg-red-950/20 border-red-500/80 text-red-200 placeholder-red-400 focus:border-red-500 shadow-[0_0_15px_rgba(239,68,68,0.15)]' 
                                                            : 'bg-slate-950 border-slate-800 focus:border-blue-500 text-slate-200'
                                                    }`} 
                                                />
                                                {k === 'car_model' && specsMessage && (
                                                    <div className={`mt-2 text-[10px] font-extrabold px-3 py-1.5 rounded-lg border text-left transition-all duration-300 ${
                                                        specsMessage.type === 'success' ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-400' :
                                                        specsMessage.type === 'error' ? 'bg-red-950/20 border-red-500/30 text-red-400' :
                                                        'bg-blue-950/20 border-blue-500/30 text-blue-400'
                                                    }`}>
                                                        {specsMessage.text}
                                                    </div>
                                                )}
                                            </div>
                                        );
                                    })}
                                </div>

                                {validationErrors.length > 0 && (
                                    <motion.div 
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="mb-8 p-6 bg-red-950/40 border border-red-500/50 rounded-[25px] text-left shadow-[0_0_25px_rgba(239,68,68,0.15)]"
                                    >
                                        <div className="flex items-center gap-3 mb-3 text-red-400">
                                            <AlertCircle size={24} className="animate-bounce" />
                                            <h4 className="font-black text-base uppercase tracking-wider">Tizimda xatoliklar aniqlandi!</h4>
                                        </div>
                                        <p className="text-xs text-slate-300 mb-4 font-medium">
                                            Hisobotni to'g'ri va xatosiz tayyorlash uchun quyidagi maydonlarni to'g'rilashingiz shart:
                                        </p>
                                        <ul className="list-disc list-inside space-y-1.5 text-xs text-red-200 font-bold">
                                            {validationErrors.map((err, idx) => (
                                                <li key={idx}>{err}</li>
                                            ))}
                                        </ul>
                                    </motion.div>
                                )}

                                <button onClick={handleFindAnalogs} disabled={loading} className="w-full py-6 bg-blue-600 rounded-2xl font-black text-xl hover:bg-blue-750 transition-all shadow-[0_0_20px_rgba(37,99,235,0.2)] disabled:opacity-50">
                                    {loading ? 'TAHLIL QILINMOQDA...' : 'ANALOGLARNI TOPISH'}
                                </button>
                            </motion.div>
                        );
                    })()}

                    {step === 3 && (
                        <motion.div key="s3" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-slate-900/40 p-8 rounded-[40px] border border-white/5">
                            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
                                <h2 className="text-3xl font-black">Analoglar</h2>
                                <button 
                                    onClick={handleOpenAddAnalog}
                                    className="px-5 py-3 bg-blue-600 hover:bg-blue-750 text-white rounded-xl font-bold text-sm flex items-center gap-2 transition-all shadow-[0_0_15px_rgba(37,99,235,0.2)]"
                                >
                                    <Plus size={16} /> Yangi Analog Qo'shish
                                </button>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                                {analogs.map((a, i) => {
                                    return (
                                        <div 
                                            key={i} 
                                            className="p-6 bg-slate-950/80 rounded-3xl border border-white/5 hover:border-blue-500/30 hover:shadow-[0_0_20px_rgba(59,130,246,0.1)] transition-all group flex flex-col justify-between"
                                        >
                                            <div>
                                                <div className="flex justify-between items-start mb-4">
                                                    <span className="px-3 py-1 bg-blue-500/10 text-blue-400 text-[10px] font-black uppercase tracking-wider rounded-lg border border-blue-500/10">
                                                        {a.source || "E'lon"}
                                                    </span>
                                                    <span className="text-xs text-slate-500 font-bold">
                                                        {a.year}-yil
                                                    </span>
                                                </div>
                                                <h4 className="font-black text-white text-lg mb-2 group-hover:text-blue-400 transition-colors line-clamp-2">
                                                    {a.model_name}
                                                </h4>
                                                <p className="text-2xl font-black text-emerald-400 mb-6">
                                                    ${parseFloat(a.price).toLocaleString()}
                                                </p>
                                            </div>
                                            
                                            <div className="flex gap-2 mt-4">
                                                <a 
                                                    href={a.url || "#"} 
                                                    target="_blank" 
                                                    rel="noopener noreferrer" 
                                                    className="flex-1 py-3 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-xl font-bold text-xs text-center flex items-center justify-center gap-1.5 text-slate-300 transition-all shadow-md"
                                                >
                                                    E'lonni ko'rish
                                                    <ExternalLink size={12} />
                                                </a>
                                                <button 
                                                    onClick={() => handleOpenEditAnalog(a)}
                                                    className="px-3.5 py-3 bg-slate-900 hover:bg-blue-600 border border-slate-800 hover:border-blue-500 rounded-xl font-bold text-xs text-center flex items-center justify-center text-slate-300 hover:text-white transition-all shadow-md"
                                                    title="Tahrirlash"
                                                >
                                                    <Edit size={14} />
                                                </button>
                                                <button 
                                                    onClick={() => handleDeleteAnalog(a.id)}
                                                    className="px-3.5 py-3 bg-slate-900 hover:bg-red-600 border border-slate-800 hover:border-red-500 rounded-xl font-bold text-xs text-center flex items-center justify-center text-slate-300 hover:text-white transition-all shadow-md"
                                                    title="O'chirish"
                                                >
                                                    <Trash2 size={14} />
                                                </button>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>

                            {/* Mulkdor Turi */}
                            <div className="max-w-xl mx-auto mb-8">
                                <div className="p-8 bg-slate-950/80 rounded-3xl border border-white/5">
                                    <div className="text-center mb-6">
                                        <h3 className="font-black text-lg mb-2 text-white">Mulkdor Shaxs Turi</h3>
                                        <p className="text-xs text-slate-500">AI tizim tahrirchisi hisobotni tanlangan shaxs turiga moslab avtomatik ravishda 100% tahrirlab beradi.</p>
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                        <button
                                            type="button"
                                            onClick={() => setEntityType('physical')}
                                            className={`p-6 rounded-2xl border transition-all flex flex-col items-center gap-2 font-bold text-sm ${entityType === 'physical' ? 'bg-blue-600/20 border-blue-500 text-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.15)]' : 'bg-slate-900/40 border-white/5 text-slate-400 hover:border-white/10'}`}
                                        >
                                            <span className="text-3xl">👤</span>
                                            Jismoniy shaxs
                                        </button>
                                        <button
                                            type="button"
                                            onClick={() => setEntityType('legal')}
                                            className={`p-6 rounded-2xl border transition-all flex flex-col items-center gap-2 font-bold text-sm ${entityType === 'legal' ? 'bg-blue-600/20 border-blue-500 text-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.15)]' : 'bg-slate-900/40 border-white/5 text-slate-400 hover:border-white/10'}`}
                                        >
                                            <span className="text-3xl">🏢</span>
                                            Yuridik shaxs
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <button onClick={handleGoToPayment} className="w-full py-6 bg-emerald-600 rounded-2xl font-black text-xl">
                                HISOBOTNI TAYYORLASH VA TO'LOVGA O'TISH
                            </button>

                            {/* Analog Edit/Add Modal */}
                            {showAnalogModal && (
                                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
                                    <motion.div 
                                        initial={{ opacity: 0, scale: 0.95 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        exit={{ opacity: 0, scale: 0.95 }}
                                        className="bg-slate-900 border border-white/10 rounded-[30px] w-full max-w-2xl overflow-hidden shadow-2xl text-slate-200"
                                    >
                                        <div className="flex justify-between items-center px-8 py-6 border-b border-white/5 bg-slate-950/40">
                                            <h3 className="text-xl font-black text-white">
                                                {editingAnalog ? "Analogni tahrirlash" : "Yangi analog qo'shish"}
                                            </h3>
                                            <button 
                                                onClick={() => setShowAnalogModal(false)}
                                                className="p-2 hover:bg-slate-800 rounded-xl text-slate-400 hover:text-white transition-colors"
                                            >
                                                <X size={20} />
                                            </button>
                                        </div>
                                        <form onSubmit={handleSaveAnalog} className="p-8 max-h-[70vh] overflow-y-auto space-y-6 text-left">
                                            {/* Global Analogs Search */}
                                            <div className="bg-slate-950/50 p-6 rounded-2xl border border-white/5 mb-4">
                                                <h4 className="text-xs font-black text-blue-400 uppercase tracking-widest mb-3">Global Analoglar Bazasidan qidirish</h4>
                                                <div className="flex gap-2">
                                                    <input 
                                                        type="text" 
                                                        placeholder="Mashina rusumi bo'yicha qidirish..." 
                                                        value={globalSearchQuery}
                                                        onChange={(e) => setGlobalSearchQuery(e.target.value)}
                                                        className="flex-1 px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl outline-none font-bold text-sm text-slate-200"
                                                    />
                                                    <button 
                                                        type="button" 
                                                        onClick={handleSearchGlobalAnalogs}
                                                        className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold text-xs transition-all shadow-md outline-none"
                                                    >
                                                        {searchingGlobal ? 'Qidirilmoqda...' : 'Qidirish'}
                                                    </button>
                                                </div>
                                                
                                                {globalSearchResults.length > 0 && (
                                                    <div className="mt-4 max-h-[150px] overflow-y-auto space-y-2 border-t border-white/5 pt-3">
                                                        {globalSearchResults.map((g, idx) => (
                                                            <div 
                                                                key={idx} 
                                                                onClick={() => handleSelectGlobalAnalog(g)}
                                                                className="p-3 bg-slate-900 hover:bg-blue-600/20 border border-slate-800 hover:border-blue-500/30 rounded-xl flex justify-between items-center cursor-pointer transition-all"
                                                            >
                                                                <div>
                                                                    <p className="font-bold text-xs text-white">{g.model_name} ({g.year})</p>
                                                                    <p className="text-[10px] text-slate-500">{g.mileage} km | {g.location}</p>
                                                                </div>
                                                                <p className="font-black text-sm text-emerald-400">${parseFloat(g.price).toLocaleString()}</p>
                                                            </div>
                                                        ))}
                                                    </div>
                                                )}
                                            </div>
                                            
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                <div>
                                                    <label className="text-[10px] font-black text-slate-500 uppercase ml-2 mb-1 block">Rusumi va Modeli</label>
                                                    <input 
                                                        type="text" 
                                                        required 
                                                        value={analogForm.model_name}
                                                        onChange={(e) => setAnalogForm({...analogForm, model_name: e.target.value})}
                                                        className="w-full px-5 py-3 bg-slate-950 border border-slate-800 rounded-xl focus:border-blue-500 outline-none font-bold"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="text-[10px] font-black text-slate-500 uppercase ml-2 mb-1 block">Ishlab chiqarilgan yili</label>
                                                    <input 
                                                        type="number" 
                                                        required
                                                        value={analogForm.year}
                                                        onChange={(e) => setAnalogForm({...analogForm, year: parseInt(e.target.value) || new Date().getFullYear()})}
                                                        className="w-full px-5 py-3 bg-slate-950 border border-slate-800 rounded-xl focus:border-blue-500 outline-none font-bold"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="text-[10px] font-black text-slate-500 uppercase ml-2 mb-1 block">Narxi (USD)</label>
                                                    <input 
                                                        type="number" 
                                                        required
                                                        value={analogForm.price}
                                                        onChange={(e) => setAnalogForm({...analogForm, price: e.target.value})}
                                                        className="w-full px-5 py-3 bg-slate-950 border border-slate-800 rounded-xl focus:border-blue-500 outline-none font-bold"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="text-[10px] font-black text-slate-500 uppercase ml-2 mb-1 block">Bosib o'tgan masofasi (km)</label>
                                                    <input 
                                                        type="text" 
                                                        value={analogForm.mileage}
                                                        onChange={(e) => setAnalogForm({...analogForm, mileage: e.target.value})}
                                                        className="w-full px-5 py-3 bg-slate-950 border border-slate-800 rounded-xl focus:border-blue-500 outline-none font-bold"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="text-[10px] font-black text-slate-500 uppercase ml-2 mb-1 block">Dvigatel hajmi (sm3)</label>
                                                    <input 
                                                        type="text" 
                                                        value={analogForm.engine_capacity}
                                                        onChange={(e) => setAnalogForm({...analogForm, engine_capacity: e.target.value})}
                                                        className="w-full px-5 py-3 bg-slate-950 border border-slate-800 rounded-xl focus:border-blue-500 outline-none font-bold"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="text-[10px] font-black text-slate-500 uppercase ml-2 mb-1 block">Uzatma qutisi (KPP)</label>
                                                    <select 
                                                        value={analogForm.transmission}
                                                        onChange={(e) => setAnalogForm({...analogForm, transmission: e.target.value})}
                                                        className="w-full px-5 py-3 bg-slate-950 border border-slate-800 rounded-xl focus:border-blue-500 outline-none font-bold text-slate-300"
                                                    >
                                                        <option value="Mexanika">Mexanika</option>
                                                        <option value="Avtomat">Avtomat</option>
                                                        <option value="Variator">Variator</option>
                                                        <option value="Robot">Robot</option>
                                                    </select>
                                                </div>
                                                <div>
                                                    <label className="text-[10px] font-black text-slate-500 uppercase ml-2 mb-1 block">Rangi</label>
                                                    <input 
                                                        type="text" 
                                                        value={analogForm.color}
                                                        onChange={(e) => setAnalogForm({...analogForm, color: e.target.value})}
                                                        className="w-full px-5 py-3 bg-slate-950 border border-slate-800 rounded-xl focus:border-blue-500 outline-none font-bold"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="text-[10px] font-black text-slate-500 uppercase ml-2 mb-1 block">Kuzov turi</label>
                                                    <input 
                                                        type="text" 
                                                        value={analogForm.body_type}
                                                        onChange={(e) => setAnalogForm({...analogForm, body_type: e.target.value})}
                                                        className="w-full px-5 py-3 bg-slate-950 border border-slate-800 rounded-xl focus:border-blue-500 outline-none font-bold"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="text-[10px] font-black text-slate-500 uppercase ml-2 mb-1 block">Manzili (Viloyat/Shahar)</label>
                                                    <input 
                                                        type="text" 
                                                        value={analogForm.location}
                                                        onChange={(e) => setAnalogForm({...analogForm, location: e.target.value})}
                                                        className="w-full px-5 py-3 bg-slate-950 border border-slate-800 rounded-xl focus:border-blue-500 outline-none font-bold"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="text-[10px] font-black text-slate-500 uppercase ml-2 mb-1 block">Manba (Sayt)</label>
                                                    <input 
                                                        type="text" 
                                                        value={analogForm.source}
                                                        onChange={(e) => setAnalogForm({...analogForm, source: e.target.value})}
                                                        className="w-full px-5 py-3 bg-slate-950 border border-slate-800 rounded-xl focus:border-blue-500 outline-none font-bold"
                                                    />
                                                </div>
                                            </div>
                                            <div>
                                                <label className="text-[10px] font-black text-slate-500 uppercase ml-2 mb-1 block">E'lon havolasi (URL)</label>
                                                <input 
                                                    type="url" 
                                                    value={analogForm.url}
                                                    onChange={(e) => setAnalogForm({...analogForm, url: e.target.value})}
                                                    className="w-full px-5 py-3 bg-slate-950 border border-slate-800 rounded-xl focus:border-blue-500 outline-none font-bold"
                                                    placeholder="https://olx.uz/d/oz/obyavlenie/..."
                                                />
                                            </div>
                                            <div className="flex gap-4 pt-4 border-t border-white/5">
                                                <button 
                                                    type="button"
                                                    onClick={() => setShowAnalogModal(false)}
                                                    className="flex-1 py-4 bg-slate-800 hover:bg-slate-750 text-white rounded-2xl font-bold text-center transition-all"
                                                >
                                                    Bekor qilish
                                                </button>
                                                <button 
                                                    type="submit"
                                                    disabled={loading}
                                                    className="flex-1 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl font-bold text-center transition-all shadow-lg shadow-blue-500/20"
                                                >
                                                    {loading ? "Saqlanmoqda..." : "Saqlash"}
                                                </button>
                                            </div>
                                        </form>
                                    </motion.div>
                                </div>
                            )}
                        </motion.div>
                    )}

                    {step === 4 && (
                        <motion.div key="s4" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="bg-slate-900/60 p-12 rounded-[50px] border border-blue-500/20 text-center shadow-2xl relative overflow-hidden">
                            <div className="absolute top-0 right-0 p-8 text-blue-500/10"><CreditCard size={200} /></div>
                            <div className="relative z-10">
                                <div className="w-20 h-20 bg-amber-500/20 text-amber-500 rounded-3xl flex items-center justify-center mx-auto mb-6">
                                    <CreditCard size={40} />
                                </div>
                                <h2 className="text-4xl font-black text-white mb-2">To'lov Qiling</h2>
                                <p className="text-slate-400 mb-8">Hisobotni yuklab olish uchun to'lovni amalga oshiring.</p>

                                {/* Payment Methods Tabs */}
                                <div className="flex justify-center gap-4 mb-10 max-w-md mx-auto bg-slate-950/80 p-2 rounded-2xl border border-white/5">
                                    <button 
                                        onClick={() => setPaymentTab('auto')}
                                        className={`flex-1 py-3 px-4 rounded-xl text-xs font-black uppercase tracking-wider transition-all duration-300 ${paymentTab === 'auto' ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
                                    >
                                        Avtomatik to'lov
                                    </button>
                                    <button 
                                        onClick={() => setPaymentTab('manual')}
                                        className={`flex-1 py-3 px-4 rounded-xl text-xs font-black uppercase tracking-wider transition-all duration-300 ${paymentTab === 'manual' ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
                                    >
                                        Chek yuklash (Qo'lda)
                                    </button>
                                </div>
                                
                                {paymentTab === 'auto' ? (
                                    <div className="max-w-xl mx-auto bg-slate-950/80 p-8 rounded-[35px] border border-white/5 text-center">
                                        <div className="flex justify-between items-center mb-8 pb-6 border-b border-white/5">
                                            <span className="text-slate-500 font-bold uppercase text-xs tracking-widest">To'lov summasi:</span>
                                            <span className="text-3xl font-black text-emerald-400">100,000 so'm</span>
                                        </div>
                                        <p className="text-sm text-slate-400 mb-8 leading-relaxed">
                                            Tizim to'lovni avtomatik tekshiradi. To'lov amalga oshishi bilanoq hisobot yuklab olish uchun darhol ochiladi.
                                        </p>
                                        
                                        <div className="grid grid-cols-2 gap-4 max-w-md mx-auto mb-6">
                                            {/* Click Button */}
                                            <button 
                                                onClick={() => setShowPaymentSimulator('click')}
                                                className="group relative overflow-hidden bg-gradient-to-br from-blue-600 to-indigo-700 hover:from-blue-500 hover:to-indigo-600 text-white py-6 px-4 rounded-2xl shadow-xl transition-all duration-300 hover:scale-[1.03] border border-blue-400/20"
                                            >
                                                <div className="font-black text-xl mb-1 tracking-wider uppercase">CLICK</div>
                                                <div className="text-[10px] text-blue-200 font-semibold tracking-wider uppercase">Click to Pay</div>
                                                <div className="absolute top-2 right-2 w-2 h-2 rounded-full bg-emerald-400 animate-ping"></div>
                                            </button>

                                            {/* Payme Button */}
                                            <button 
                                                onClick={() => setShowPaymentSimulator('payme')}
                                                className="group relative overflow-hidden bg-gradient-to-br from-teal-600 to-cyan-700 hover:from-teal-500 hover:to-cyan-600 text-white py-6 px-4 rounded-2xl shadow-xl transition-all duration-300 hover:scale-[1.03] border border-teal-400/20"
                                            >
                                                <div className="font-black text-xl mb-1 tracking-wider uppercase">PAYME</div>
                                                <div className="text-[10px] text-teal-200 font-semibold tracking-wider uppercase">Pay with Payme</div>
                                                <div className="absolute top-2 right-2 w-2 h-2 rounded-full bg-emerald-400 animate-ping"></div>
                                            </button>
                                        </div>
                                        
                                        <p className="text-[10px] text-slate-500 italic">
                                            * To'lov tugmasini bosgandan so'ng test to'lov simulyatori ochiladi.
                                        </p>
                                    </div>
                                ) : (
                                    <div className="grid md:grid-cols-2 gap-8 mb-10 items-start">
                                        {/* Card Details */}
                                        <div className="bg-slate-950/80 p-8 rounded-[35px] border border-white/5 text-left h-full flex flex-col justify-center">
                                            <div className="flex justify-between items-center mb-6">
                                                <span className="text-slate-500 font-bold uppercase text-[10px] tracking-[0.2em]">To'lov miqdori:</span>
                                                <span className="text-2xl font-black text-emerald-400">100,000 so'm</span>
                                            </div>
                                            <div className="p-6 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl shadow-xl relative overflow-hidden group">
                                                <div className="absolute -right-4 -bottom-4 opacity-10 group-hover:scale-110 transition-transform duration-700">
                                                    <CreditCard size={120} />
                                                </div>
                                                <p className="text-[10px] text-blue-100 font-black uppercase mb-4 tracking-widest opacity-80">Karta raqami (HUMO/UZCARD)</p>
                                                <p className="text-2xl font-black text-white tracking-[0.2em] mb-6">9860 1234 5678 9012</p>
                                                <div className="flex justify-between items-end">
                                                    <p className="text-sm font-bold text-white/90">Eshonov Nodirbek</p>
                                                    <div className="w-10 h-6 bg-white/20 rounded-md backdrop-blur-sm"></div>
                                                </div>
                                            </div>
                                            <p className="text-[10px] text-slate-500 mt-6 leading-relaxed italic">
                                                * To'lovni amalga oshirgach, chekni (skrinshot) pastdagi maydonga yuklang.
                                            </p>
                                        </div>

                                        {/* QR Code Section */}
                                        <div className="bg-white p-8 rounded-[35px] shadow-2xl flex flex-col items-center justify-center h-full group hover:scale-[1.02] transition-all duration-500">
                                            <img 
                                                src="/payment_qr_code_1777971861714.png" 
                                                alt="Payment QR" 
                                                className="w-48 h-48 object-contain mb-4"
                                            />
                                            <p className="text-slate-900 font-black text-xs uppercase tracking-[0.2em] mb-2">Tezkor to'lov (QR Skaner)</p>
                                            <div className="flex gap-2">
                                                <div className="px-3 py-1 bg-blue-50 text-blue-600 text-[8px] font-black rounded-full border border-blue-100">CLICK</div>
                                                <div className="px-3 py-1 bg-emerald-50 text-emerald-600 text-[8px] font-black rounded-full border border-emerald-100">PAYME</div>
                                                <div className="px-3 py-1 bg-indigo-50 text-indigo-600 text-[8px] font-black rounded-full border border-indigo-100">UZUM</div>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* Process Guide */}
                                <div className="max-w-2xl mx-auto mb-12 grid grid-cols-3 gap-4">
                                    {[
                                        { i: "1", t: "To'lov", d: "Avtomatik yoki Qo'lda" },
                                        { i: "2", t: "Tasdiqlash", d: "Avtomat (1-soniya) yoki chek yuklash" },
                                        { i: "3", t: "Tayyor", d: "Hisobot yuklash uchun ochiladi" }
                                    ].map((s, idx) => (
                                        <div key={idx} className="text-center">
                                            <div className="w-8 h-8 bg-slate-800 rounded-full flex items-center justify-center text-blue-400 font-black text-xs mx-auto mb-2 border border-white/5">
                                                {s.i}
                                            </div>
                                            <p className="text-[10px] font-black text-white uppercase tracking-wider mb-1">{s.t}</p>
                                            <p className="text-[9px] text-slate-500 font-medium leading-tight">{s.d}</p>
                                        </div>
                                    ))}
                                </div>

                                {paymentTab === 'manual' && (
                                    <div className="max-w-md mx-auto space-y-4">
                                        <label className="block">
                                            <div className={`p-6 border-2 border-dashed rounded-2xl transition-all cursor-pointer ${receiptFile ? 'border-emerald-500 bg-emerald-500/5' : 'border-slate-700 hover:border-blue-500'}`}>
                                                <Upload size={24} className="mx-auto mb-2 text-slate-500" />
                                                <p className="font-bold text-sm">{receiptFile ? receiptFile.name : 'To\'lov chekini yuklang'}</p>
                                                <input type="file" accept="image/*" className="hidden" onChange={(e) => setReceiptFile(e.target.files?.[0] || null)} />
                                            </div>
                                        </label>
                                        <button 
                                            onClick={handleSubmitReceipt} 
                                            disabled={!receiptFile || paymentSubmitting} 
                                            className="w-full py-5 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl font-black text-lg shadow-lg shadow-blue-500/30 disabled:opacity-50 transition-all"
                                        >
                                            {paymentSubmitting ? 'YUBORILMOQDA...' : 'CHEKNI TASDIQLASHGA YUBORISH'}
                                        </button>
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    )}

                    {/* Payment Simulator Popup */}
                    <AnimatePresence>
                        {showPaymentSimulator && (
                            <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-md p-4">
                                <motion.div 
                                    initial={{ opacity: 0, scale: 0.9 }} 
                                    animate={{ opacity: 1, scale: 1 }} 
                                    exit={{ opacity: 0, scale: 0.9 }} 
                                    className="bg-slate-900 border border-slate-700/50 rounded-[40px] max-w-md w-full overflow-hidden shadow-2xl relative"
                                >
                                    <button 
                                        onClick={() => setShowPaymentSimulator(null)} 
                                        className="absolute top-6 right-6 text-slate-400 hover:text-white p-2 rounded-full bg-slate-800 hover:bg-slate-700 transition-all"
                                    >
                                        <X size={20} />
                                    </button>
                                    
                                    {showPaymentSimulator === 'click' ? (
                                        <div className="p-8">
                                            <div className="flex items-center gap-3 mb-6">
                                                <div className="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center text-white font-black text-lg">C</div>
                                                <div className="text-left">
                                                    <h3 className="text-lg font-black text-white">CLICK Checkout</h3>
                                                    <p className="text-[10px] text-slate-400">Xavfsiz to'lov tizimi (Sandbox)</p>
                                                </div>
                                            </div>
                                            
                                            <div className="bg-slate-950/50 p-6 rounded-2xl border border-white/5 mb-6 text-left">
                                                <div className="flex justify-between mb-2">
                                                    <span className="text-xs text-slate-400">Qabul qiluvchi:</span>
                                                    <span className="text-xs font-bold text-white">Smart Baholash MChJ</span>
                                                </div>
                                                <div className="flex justify-between mb-2">
                                                    <span className="text-xs text-slate-400">Hisobot ID:</span>
                                                    <span className="text-xs font-bold text-white">#{valuationId}</span>
                                                </div>
                                                <div className="flex justify-between pt-2 border-t border-white/5">
                                                    <span className="text-xs text-slate-400 font-bold">To'lov summasi:</span>
                                                    <span className="text-sm font-black text-emerald-400">100,000 UZS</span>
                                                </div>
                                            </div>
                                            
                                            <div className="space-y-4 text-left">
                                                <div>
                                                    <label className="block text-[10px] uppercase font-bold tracking-wider text-slate-400 mb-1">Karta raqami (TEST MODE)</label>
                                                    <input type="text" readOnly value="8600 1234 5678 9012" className="w-full bg-slate-950 border border-slate-800 p-4 rounded-xl text-white font-mono text-sm focus:outline-none" />
                                                </div>
                                                <div>
                                                    <label className="block text-[10px] uppercase font-bold tracking-wider text-slate-400 mb-1">Amal qilish muddati</label>
                                                    <input type="text" readOnly value="12/29" className="w-full bg-slate-950 border border-slate-800 p-4 rounded-xl text-white font-mono text-sm focus:outline-none" />
                                                </div>
                                            </div>
                                            
                                            <button 
                                                onClick={() => handleSimulatePayment('click')} 
                                                disabled={simulating}
                                                className="w-full py-4 bg-blue-600 hover:bg-blue-700 text-white font-black text-sm uppercase tracking-wider rounded-2xl mt-8 shadow-lg shadow-blue-500/20 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
                                            >
                                                {simulating ? 'TO\'LOV AMALGA OSHIRILMOQDA...' : '100,000 UZS TO\'LASH'}
                                            </button>
                                        </div>
                                    ) : (
                                        <div className="p-8">
                                            <div className="flex items-center gap-3 mb-6">
                                                <div className="w-12 h-12 bg-teal-500 rounded-2xl flex items-center justify-center text-white font-black text-lg">P</div>
                                                <div className="text-left">
                                                    <h3 className="text-lg font-black text-white">Payme Checkout</h3>
                                                    <p className="text-[10px] text-slate-400">Xavfsiz to'lov tizimi (Sandbox)</p>
                                                </div>
                                            </div>
                                            
                                            <div className="bg-slate-950/50 p-6 rounded-2xl border border-white/5 mb-6 text-left">
                                                <div className="flex justify-between mb-2">
                                                    <span className="text-xs text-slate-400">Qabul qiluvchi:</span>
                                                    <span className="text-xs font-bold text-white">Smart Baholash MChJ</span>
                                                </div>
                                                <div className="flex justify-between mb-2">
                                                    <span className="text-xs text-slate-400">Hisobot ID:</span>
                                                    <span className="text-xs font-bold text-white">#{valuationId}</span>
                                                </div>
                                                <div className="flex justify-between pt-2 border-t border-white/5">
                                                    <span className="text-xs text-slate-400 font-bold">To'lov summasi:</span>
                                                    <span className="text-sm font-black text-emerald-400">100,000 UZS</span>
                                                </div>
                                            </div>
                                            
                                            <div className="space-y-4 text-left">
                                                <div>
                                                    <label className="block text-[10px] uppercase font-bold tracking-wider text-slate-400 mb-1">Telefon raqami (TEST MODE)</label>
                                                    <input type="text" readOnly value="+998 (90) 123-4567" className="w-full bg-slate-950 border border-slate-800 p-4 rounded-xl text-white font-mono text-sm focus:outline-none" />
                                                </div>
                                                <div>
                                                    <label className="block text-[10px] uppercase font-bold tracking-wider text-slate-400 mb-1">Tasdiqlash kodi</label>
                                                    <input type="text" readOnly value="12345" className="w-full bg-slate-950 border border-slate-800 p-4 rounded-xl text-white font-mono text-sm focus:outline-none" />
                                                </div>
                                            </div>
                                            
                                            <button 
                                                onClick={() => handleSimulatePayment('payme')} 
                                                disabled={simulating}
                                                className="w-full py-4 bg-teal-500 hover:bg-teal-600 text-white font-black text-sm uppercase tracking-wider rounded-2xl mt-8 shadow-lg shadow-teal-500/20 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
                                            >
                                                {simulating ? 'TO\'LOV AMALGA OSHIRILMOQDA...' : '100,000 UZS TO\'LASH'}
                                            </button>
                                        </div>
                                    )}
                                </motion.div>
                            </div>
                        )}
                    </AnimatePresence>

                    {step === 5 && (
                        <motion.div key="s5" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="bg-slate-900/50 p-16 rounded-[60px] border border-emerald-500/20 text-center">
                            <div className="w-24 h-24 bg-emerald-500 rounded-3xl flex items-center justify-center text-white mx-auto mb-8 shadow-lg shadow-emerald-500/20">
                                <CheckCircle2 size={48} />
                            </div>
                            <h2 className="text-4xl font-black text-white mb-2">Tabriklaymiz!</h2>
                            <p className="text-slate-400 mb-12">To'lovingiz tasdiqlandi. Hisobotni yuklab olishingiz mumkin.</p>
                            
                            <div className="flex flex-col sm:flex-row gap-4 justify-center">
                                {reportData?.docx_url && (
                                    <a href={getMediaUrl(reportData.docx_url)} download className="flex-1 max-w-[240px] py-4 bg-white text-black rounded-2xl font-black flex items-center justify-center gap-2 hover:bg-slate-200 transition-all">
                                        <Download size={20} /> WORD (.DOCX)
                                    </a>
                                )}
                                {reportData?.pdf_url && (
                                    <a href={getMediaUrl(reportData.pdf_url)} download className="flex-1 max-w-[240px] py-4 bg-rose-600 text-white rounded-2xl font-black flex items-center justify-center gap-2 hover:bg-rose-700 transition-all">
                                        <FileDown size={20} /> PDF (YUKLASH)
                                    </a>
                                )}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}

export default function VehicleModule() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <VehicleModuleInner />
        </Suspense>
    );
}
