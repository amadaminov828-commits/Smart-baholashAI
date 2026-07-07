"use client";

import { useState, useEffect, Suspense } from 'react';
import { api } from '@/services/api';
import { useTranslation } from '@/i18n/I18nProvider';
import { motion, AnimatePresence } from 'framer-motion';
import {
    FileText, Camera, Search, Download, Building, ArrowLeft, CheckCircle2,
    Upload, MapPin, ClipboardList, Key, AlertCircle, TrendingUp, DollarSign,
    Calculator, ArrowRight, Zap, ExternalLink, CreditCard, Clock, FileDown
} from 'lucide-react';
import { useRouter, useSearchParams } from 'next/navigation';
import SmartEditor from './components/SmartEditor';
import CalculationEditor from './components/CalculationEditor';

const getMediaUrl = (path: string | null | undefined) => {
    if (!path) return '#';
    if (path.startsWith('http')) return path;
    const cleanPath = path.startsWith('/') ? path.substring(1) : path;
    return `/${cleanPath}`;
};

function RealEstateContent() {
    const { t } = useTranslation();
    const router = useRouter();
    const searchParams = useSearchParams();
    const editId = searchParams.get('edit');
    const [step, setStep] = useState(1);
    const [files, setFiles] = useState<File[]>([]);
    const [extractedData, setExtractedData] = useState<any>(null);
    const [purpose, setPurpose] = useState('garov');
    const [analogs, setAnalogs] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [valuationId, setValuationId] = useState<number | null>(null);
    const [templates, setTemplates] = useState<any[]>([]);
    const [reportData, setReportData] = useState<any>(null);
    const [templateFile, setTemplateFile] = useState<File | null>(null);
    const [uploadingTemplate, setUploadingTemplate] = useState(false);
    const [selectedTemplate, setSelectedTemplate] = useState<number | null>(null);
    const [user, setUser] = useState<any>(null);
    const [isEditing, setIsEditing] = useState(false);
    
    // Payment states
    const [receiptFile, setReceiptFile] = useState<File | null>(null);
    const [paymentSubmitting, setPaymentSubmitting] = useState(false);

    useEffect(() => {
        api.get(`users/me?t=${Date.now()}`).then(res => setUser(res.data)).catch(() => {
            window.location.href = '/login';
        });

        if (editId) {
            api.get(`/real-estate/valuations/${editId}/`).then(res => {
                const data = res.data;
                setValuationId(Number(editId));
                setExtractedData(data);
                if (data.status === 'approved') {
                    if (data.report_data) setReportData(data.report_data);
                    setStep(5);
                }
                else if (data.status === 'verifying' || data.status === 'payment_pending') setStep(4);
                else setStep(2);
                setIsEditing(true);
            }).catch(err => console.error(err));
        }
    }, [editId]);

    const fetchTemplates = () => {
        api.get('/templates/').then(res => {
            const reTemplates = res.data.filter((t: any) => t.object_type === 'real_estate');
            setTemplates(reTemplates);
            if (reTemplates.length > 0 && !selectedTemplate) {
                setSelectedTemplate(reTemplates[0].id);
            }
        }).catch(err => console.error(err));
    };

    useEffect(() => {
        if (step === 3) fetchTemplates();
    }, [step]);

    const fetchAnalogs = async (vId: number) => {
        try {
            const res = await api.get(`/real-estate/valuations/${vId}/search-analogs/`);
            setAnalogs(res.data.slice(0, 3));
        } catch (e: any) {
            setAnalogs([]);
        }
    };

    const handleFileUpload = async () => {
        if (files.length === 0) return alert('Hujjatlar yuklanishi shart');
        setLoading(true);
        try {
            const valRes = await api.post('/real-estate/valuations/', { purpose });
            const vId = valRes.data.id;
            setValuationId(vId);
            const formData = new FormData();
            files.forEach(f => formData.append('documents', f));
            const ocrRes = await api.post('/real-estate/valuations/ocr-upload/', formData);
            const ocrData = ocrRes.data.extracted_data;
            setExtractedData(ocrData);
            await api.patch(`/real-estate/valuations/${vId}/`, ocrData);
            setStep(2);
            setIsEditing(true);
        } catch (e: any) {
            alert("Xato yuz berdi");
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
            fd.append('object_type', 'real_estate');
            fd.append('file', templateFile);
            const res = await api.post('/templates/', fd);
            setSelectedTemplate(res.data.id);
            fetchTemplates();
            setTemplateFile(null);
        } catch (e) {
            alert('Error');
        }
        setUploadingTemplate(false);
    };

    const handleFindAnalogs = async () => {
        setLoading(true);
        try {
            await api.post(`/real-estate/valuations/${valuationId}/find-analogs/`);
            const valInfo = await api.get(`/real-estate/valuations/${valuationId}/`);
            setAnalogs(valInfo.data.analogs || []);
            setStep(3);
        } catch (e: any) {
            alert("Analoglar qidirishda xato");
        }
        setLoading(false);
    };

    const handleGoToPayment = async () => {
        if (!valuationId) return;
        setLoading(true);
        try {
            await api.patch(`/real-estate/valuations/${valuationId}/`, { status: 'payment_pending' });
            setStep(4);
        } catch (e) {
            alert("Xatolik");
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
            const res = await api.patch(`/real-estate/valuations/${valuationId}/`, fd);
            
            if (res.data.status === 'approved') {
                setReportData(res.data.report_data);
                setStep(5);
            } else {
                alert("Chek yuborildi. Admin tasdiqlashini kuting.");
                router.push('/');
            }
        } catch (e) {
            alert("Xatolik");
        }
        setPaymentSubmitting(false);
    };

    return (
        <div className="min-h-screen bg-[#0a0f1c] text-slate-200 py-12 px-6 relative overflow-hidden font-sans">
            <div className="max-w-5xl mx-auto relative z-10">
                {/* Steps Navigation */}
                <div className="relative mb-16 px-4">
                    <div className="flex items-center justify-between relative z-10">
                        {[
                            { s: 1, l: 'Yuklash', i: <Camera size={18} /> },
                            { s: 2, l: 'Tahrirlash', i: <ClipboardList size={18} /> },
                            { s: 3, l: 'Analoglar', i: <Search size={18} /> },
                            { s: 4, l: 'To\'lov', i: <CreditCard size={18} /> },
                            { s: 5, l: 'Tayyor', i: <CheckCircle2 size={18} /> }
                        ].map((item) => (
                            <div key={item.s} className="flex flex-col items-center gap-3">
                                <div className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-500 border ${step >= item.s ? 'bg-emerald-600 border-emerald-400 text-white shadow-[0_0_20px_rgba(16,185,129,0.3)]' : 'bg-slate-900 border-slate-700 text-slate-500'}`}>
                                    {item.i}
                                </div>
                                <span className={`text-[9px] font-black uppercase tracking-widest ${step >= item.s ? 'text-emerald-400' : 'text-slate-600'}`}>{item.l}</span>
                            </div>
                        ))}
                    </div>
                </div>

                <AnimatePresence mode="wait">
                    {step === 1 && (
                        <motion.div key="s1" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-slate-900/40 p-10 rounded-[40px] border border-white/5 shadow-2xl">
                            <h2 className="text-3xl font-black mb-8 flex items-center gap-4"><Building className="text-emerald-400" /> Mulk turini tanlang</h2>
                            <select value={purpose} onChange={e => setPurpose(e.target.value)} className="w-full p-4 bg-slate-950 border border-slate-800 rounded-2xl text-white font-bold mb-8 outline-none">
                                <option value="garov">Garov qiymati</option>
                                <option value="soliq">Soliq qiymati</option>
                                <option value="snos">Snos va zarar</option>
                            </select>
                            <label className="block mb-8">
                                <div className="border-2 border-dashed border-slate-800 rounded-[35px] p-10 bg-slate-950/30 hover:border-emerald-500 transition-all text-center cursor-pointer">
                                    <Camera className="mx-auto text-slate-600 mb-4" size={40} />
                                    <p className="font-black text-slate-300 text-lg">Kadastr hujjatlarini yuklang</p>
                                    <input type="file" multiple accept="image/*,.pdf" className="hidden" onChange={(e) => setFiles(Array.from(e.target.files || []))} />
                                </div>
                            </label>
                            {files.length > 0 && <p className="mb-4 text-emerald-400 font-bold">{files.length} ta fayl tanlandi</p>}
                            <button onClick={handleFileUpload} disabled={loading || files.length === 0} className="w-full py-6 bg-emerald-600 rounded-2xl font-black text-xl shadow-xl">
                                {loading ? 'SKANERLANMOQDA...' : 'TAHLILNI BOSHLASH'}
                            </button>
                        </motion.div>
                    )}

                    {step === 2 && valuationId && extractedData && (
                        <SmartEditor
                            valuationId={valuationId}
                            initialData={{ ...extractedData, confirmed_fields: {} }}
                            userRole={user?.role || 'user'}
                            onComplete={() => { setStep(3); if (purpose === 'garov') fetchAnalogs(valuationId); }}
                        />
                    )}

                    {step === 3 && (
                        <motion.div key="s3" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-slate-900/40 p-10 rounded-[40px] border border-white/5 shadow-2xl">
                            <h2 className="text-3xl font-black mb-8 flex items-center gap-4"><Search className="text-emerald-400" /> Analoglar va Hisobot</h2>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                                {analogs.map((a, i) => (
                                    <div key={i} className="bg-slate-950 p-4 rounded-2xl border border-white/5">
                                        <p className="font-black text-emerald-400">{a.price.toLocaleString()} UZS</p>
                                        <p className="text-xs text-slate-400">{a.rooms} xona | {a.area}</p>
                                    </div>
                                ))}
                            </div>
                            <div className="p-8 bg-purple-600/5 rounded-3xl border border-purple-500/10 mb-10">
                                <h3 className="font-black text-white mb-4">Andoza tanlang</h3>
                                <select value={selectedTemplate || ''} onChange={e => setSelectedTemplate(Number(e.target.value))} className="w-full p-4 bg-slate-900 border border-slate-800 rounded-2xl text-white font-bold outline-none mb-4">
                                    {templates.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                                </select>
                                <input type="file" accept=".docx" onChange={e => setTemplateFile(e.target.files?.[0] || null)} className="text-xs text-slate-500" />
                                {templateFile && <button onClick={handleTemplateUpload} className="bg-purple-600 px-4 py-1 rounded-lg text-xs font-bold ml-2">Yuklash</button>}
                            </div>
                            <button onClick={handleGoToPayment} className="w-full py-7 bg-emerald-600 rounded-[30px] font-black text-2xl shadow-xl">
                                HISOBOTNI TAYYORLASH VA TO'LOVGA O'TISH
                            </button>
                        </motion.div>
                    )}

                    {step === 4 && (
                        <motion.div key="s4" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="bg-slate-900/60 p-12 rounded-[50px] border border-emerald-500/20 text-center shadow-2xl">
                            <div className="w-20 h-20 bg-amber-500/20 text-amber-500 rounded-3xl flex items-center justify-center mx-auto mb-6"><CreditCard size={40} /></div>
                            <h2 className="text-4xl font-black text-white mb-2">To'lov Sahifasi</h2>
                            <p className="text-slate-400 mb-8">Hisobot tayyor, uni yuklab olish uchun to'lovni amalga oshiring.</p>
                            <div className="bg-slate-950 p-8 rounded-[30px] border border-white/5 mb-8 max-w-md mx-auto text-left">
                                <div className="flex justify-between items-center mb-6">
                                    <span className="text-slate-500 font-bold uppercase text-xs">To'lov miqdori:</span>
                                    <span className="text-2xl font-black text-emerald-400">150,000 so'm</span>
                                </div>
                                <div className="p-4 bg-white/5 rounded-2xl border border-white/5">
                                    <p className="text-[10px] text-slate-500 font-black uppercase mb-1">Karta raqami</p>
                                    <p className="text-xl font-black text-white tracking-widest">9860 1234 5678 9012</p>
                                    <p className="text-xs text-slate-400 mt-1">Eshonov Nodirbek</p>
                                </div>
                            </div>
                            <div className="max-w-md mx-auto space-y-4">
                                <label className="block">
                                    <div className={`p-6 border-2 border-dashed rounded-2xl cursor-pointer ${receiptFile ? 'border-emerald-500 bg-emerald-500/5' : 'border-slate-700 hover:border-emerald-500'}`}>
                                        <Upload size={24} className="mx-auto mb-2 text-slate-500" />
                                        <p className="font-bold text-sm">{receiptFile ? receiptFile.name : 'To\'lov chekini (skrinshot) yuklang'}</p>
                                        <input type="file" accept="image/*" className="hidden" onChange={(e) => setReceiptFile(e.target.files?.[0] || null)} />
                                    </div>
                                </label>
                                <button onClick={handleSubmitReceipt} disabled={!receiptFile || paymentSubmitting} className="w-full py-5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-2xl font-black text-lg shadow-lg shadow-emerald-500/30">
                                    {paymentSubmitting ? 'YUBORILMOQDA...' : 'TASDIQLASHGA YUBORISH'}
                                </button>
                            </div>
                        </motion.div>
                    )}

                    {step === 5 && (
                        <motion.div key="s5" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="bg-slate-900/50 p-16 rounded-[60px] border border-emerald-500/20 text-center min-h-[400px] flex flex-col justify-center items-center">
                            {reportData ? (
                                <>
                                    <div className="w-24 h-24 bg-emerald-500 rounded-3xl flex items-center justify-center text-white mx-auto mb-8 shadow-lg shadow-emerald-500/20"><CheckCircle2 size={48} /></div>
                                    <h2 className="text-5xl font-black text-white mb-4 tracking-tighter">HISOBOT TAYYOR!</h2>
                                    <p className="text-slate-400 mb-12 text-xl">To'lov muvaffaqiyatli qabul qilindi. Hujjatlarni yuklab oling.</p>
                                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                                        <a href={getMediaUrl(reportData.docx_url)} download className="px-10 py-5 bg-white text-black rounded-2xl font-black flex items-center gap-2 hover:bg-slate-200 transition-all"><Download size={24} /> WORD</a>
                                        <a href={getMediaUrl(reportData.file_url)} target="_blank" className="px-10 py-5 bg-emerald-600 text-white rounded-2xl font-black flex items-center gap-2 hover:bg-emerald-700 transition-all"><FileDown size={24} /> PDF YUKLASH</a>
                                    </div>
                                </>
                            ) : (
                                <>
                                    <div className="w-20 h-20 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin mb-8"></div>
                                    <h2 className="text-3xl font-black text-white mb-4">HISOBOT SHAKLLANTIRILMOQDA...</h2>
                                    <p className="text-slate-400 mb-8">Iltimos, bir necha soniya kuting. PDF fayl tayyorlanmoqda.</p>
                                    <button onClick={() => window.location.reload()} className="text-emerald-400 font-bold hover:underline">Sahifani yangilash</button>
                                </>
                            )}
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}

export default function RealEstateModule() {
    return (
        <Suspense fallback={<div>Yuklanmoqda...</div>}>
            <RealEstateContent />
        </Suspense>
    );
}
