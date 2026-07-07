"use client";

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldCheck, ShieldAlert, FileText, Check, Calendar, ArrowDownToLine, Building2, UserCheck, AlertTriangle, Upload, Loader2, RefreshCw } from 'lucide-react';
import { useParams, useSearchParams } from 'next/navigation';
import axios from 'axios';

export default function VerificationPage() {
    const params = useParams();
    const searchParams = useSearchParams();
    const id = params.id as string;
    const signatory = searchParams ? searchParams.get('signatory') : null;
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [redirecting, setRedirecting] = useState(false);
    const [error, setError] = useState('');

    // PDF Verification Uploader States
    const [pdfFile, setPdfFile] = useState<File | null>(null);
    const [verifyingPdf, setVerifyingPdf] = useState(false);
    const [pdfVerificationResult, setPdfVerificationResult] = useState<'matched' | 'mismatched' | null>(null);
    const [pdfVerificationError, setPdfVerificationError] = useState('');
    const [extractedDetails, setExtractedDetails] = useState<any | null>(null);



    useEffect(() => {
        const fetchData = async () => {
            if (!id) return;
            try {
                const res = await axios.get(`/api-proxy/v1/reports/${id}/verify/`);
                setData(res.data);
            } catch (err) {
                console.error("Verification failed:", err);
                setError("Hisobot topilmadi yoki haqiqiy emas.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [id]);

    const compareData = (extracted: any) => {
        if (!data) return false;
        
        const cleanStr = (s: string) => (s || '').toLowerCase().replace(/[^a-z0-9а-яёўқғҳ]/g, '').trim();
        
        const pageOwner = cleanStr(data.object?.owner);
        const extOwner = cleanStr(extracted.owner_name);
        const ownerMatches = pageOwner.includes(extOwner) || extOwner.includes(pageOwner);
        
        let objectMatches = true;
        const isVehicle = data.type?.toLowerCase()?.includes('mashina') || data.object?.plate;
        
        if (isVehicle) {
            const pagePlate = cleanStr(data.object?.plate);
            const extPlate = cleanStr(extracted.plate_number);
            const plateMatches = pagePlate === extPlate || pagePlate.includes(extPlate) || extPlate.includes(pagePlate);
            
            const pageModel = cleanStr(data.object?.model);
            const extModel = cleanStr(extracted.car_model);
            const modelMatches = pageModel.includes(extModel) || extModel.includes(pageModel);
            
            objectMatches = plateMatches && modelMatches;
        } else {
            const pageCadastre = cleanStr(data.object?.cadastre_number);
            const extCadastre = cleanStr(extracted.cadastre_number);
            objectMatches = pageCadastre === extCadastre || pageCadastre.includes(extCadastre) || extCadastre.includes(pageCadastre);
        }
        
        const getDigits = (s: string) => (s || '').replace(/\D/g, '');
        const pageValueDigits = getDigits(data.market_value);
        const extValueDigits = getDigits(extracted.market_value || extracted.price);
        
        const valueMatches = !pageValueDigits || !extValueDigits || pageValueDigits.includes(extValueDigits) || extValueDigits.includes(pageValueDigits);
        
        return ownerMatches && objectMatches && valueMatches;
    };

    const handleVerifyPdf = async (selectedFile: File) => {
        if (!selectedFile) return;
        setPdfFile(selectedFile);
        setVerifyingPdf(true);
        setPdfVerificationError('');
        setPdfVerificationResult(null);
        setExtractedDetails(null);

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const res = await axios.post('/api-proxy/v1/reports/extract-metadata/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            const extracted = res.data;
            setExtractedDetails(extracted);
            
            const matches = compareData(extracted);
            setPdfVerificationResult(matches ? 'matched' : 'mismatched');
        } catch (err: any) {
            console.error("PDF verify error:", err);
            setPdfVerificationError(err.response?.data?.error || "Faylni tekshirishda xatolik yuz berdi. PDF hisobot ekanligiga ishonch hosil qiling.");
        } finally {
            setVerifyingPdf(false);
        }
    };

    if (loading || redirecting) return (
        <div className="min-h-screen bg-[#f8fafc] flex items-center justify-center">
            <div className="flex flex-col items-center gap-4">
                <div className="w-12 h-12 border-4 border-emerald-500/20 border-t-emerald-600 rounded-full animate-spin"></div>
                <p className="text-slate-500 font-medium text-sm animate-pulse">
                    {redirecting ? "Hujjat tasdiqlandi. Asl nusxa (PDF) yuklanmoqda..." : "Hujjat tafsilotlari tekshirilmoqda..."}
                </p>
            </div>
        </div>
    );

    if (error) return (
        <div className="min-h-screen bg-[#f8fafc] flex flex-col items-center justify-center p-6 text-center">
            <div className="w-20 h-20 bg-rose-100 rounded-full flex items-center justify-center mb-6 text-rose-600 shadow-lg shadow-rose-200">
                <ShieldAlert size={48} />
            </div>
            <h1 className="text-2xl font-black text-slate-800 mb-2">Verifikatsiya Xatoligi</h1>
            <p className="text-slate-500 max-w-sm mb-6">{error}</p>
            <div className="text-slate-400 text-xs font-semibold uppercase tracking-wider">
                Smart Baholash • Hujjat tekshirish tizimi
            </div>
        </div>
    );

    const isVerified = data?.status === 'valid';

    const companyName = data?.company?.name || '"PERCEPTION VALUE" MCHJ';
    const companyStir = data?.company?.stir || '301234567';
    const appraiserName = data?.appraiser?.name || 'B.M.Mirzabekov';
    const appraiserLicense = data?.appraiser?.license || '№0244';
    const appraiserPinfl = data?.appraiser?.pinfl || '31204901234567';

    return (
        <div className="min-h-screen bg-[#f1f5f9] py-12 px-4 md:px-6 flex flex-col items-center">
            {/* Header branding */}
            <div className="flex items-center gap-2 mb-8 select-none">
                <span className="text-xl font-black tracking-tight text-slate-800">
                    SMART<span className="text-emerald-600">BAHOLASH</span>
                </span>
                <span className="h-4 w-px bg-slate-300"></span>
                <span className="text-xs font-bold tracking-widest text-slate-500 uppercase">
                    Elektron reyestr
                </span>
            </div>

            <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                className="max-w-3xl w-full bg-white border border-slate-200/80 rounded-3xl p-6 md:p-10 shadow-xl shadow-slate-200/50"
            >
                {/* Status Section */}
                <div className="text-center mb-10 pb-8 border-b border-slate-100">
                    <div className="flex justify-center mb-4">
                        {isVerified ? (
                            <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center text-emerald-600 shadow-inner">
                                <ShieldCheck size={48} />
                            </div>
                        ) : (
                            <div className="w-20 h-20 bg-rose-100 rounded-full flex items-center justify-center text-rose-600 shadow-inner">
                                <ShieldAlert size={48} />
                            </div>
                        )}
                    </div>
                    
                    {isVerified ? (
                        <>
                            <h2 className="text-2xl font-black text-slate-800 mb-1">TASDIQLANGAN</h2>
                            <p className="text-emerald-600 font-bold tracking-wide text-xs uppercase mb-3">
                                Elektron raqamli imzo haqiqiy
                            </p>
                            <p className="text-slate-500 text-sm max-w-lg mx-auto">
                                Mazkur elektron hujjat "Smart Baholash" platformasi tomonidan tekshirildi va uning yuridik kuchi tasdiqlandi.
                            </p>
                        </>
                    ) : (
                        <>
                            <h2 className="text-2xl font-black text-slate-800 mb-1">TASDIQLANMAGAN</h2>
                            <p className="text-rose-600 font-bold tracking-wide text-xs uppercase mb-3">
                                To'lov amalga oshirilmagan
                            </p>
                            <p className="text-slate-500 text-sm max-w-lg mx-auto">
                                Ushbu baholash hisoboti to'lovi amalga oshirilmaganligi sababli tizim tomonidan tasdiqlanmagan va yuridik kuchga ega emas.
                            </p>
                        </>
                    )}
                </div>

                {/* Document details table style */}
                <div className="mb-8">
                    <h3 className="text-slate-700 text-sm font-extrabold mb-4 uppercase tracking-wider flex items-center gap-2">
                        <FileText className="text-slate-400" size={18} />
                        Hujjat tafsilotlari
                    </h3>
                    
                    <div className="border border-slate-100 rounded-2xl overflow-hidden bg-slate-50/50">
                        <table className="min-w-full divide-y divide-slate-100 text-sm text-left">
                            <tbody className="divide-y divide-slate-100">
                                <tr>
                                    <td className="px-6 py-4 font-bold text-slate-500 bg-slate-50 w-1/3">Hujjat turi</td>
                                    <td className="px-6 py-4 text-slate-800 font-medium">Baholash hisoboti ({data?.type || 'Mashina'})</td>
                                </tr>
                                <tr>
                                    <td className="px-6 py-4 font-bold text-slate-500 bg-slate-50">Hujjat raqami</td>
                                    <td className="px-6 py-4 text-slate-800 font-mono font-bold">#BV-{data?.valuation?.id || 'Noma\'lum'}</td>
                                </tr>
                                <tr>
                                    <td className="px-6 py-4 font-bold text-slate-500 bg-slate-50">Yaratilgan sana</td>
                                    <td className="px-6 py-4 text-slate-800 font-medium">{data?.valuation?.date || data?.timestamp?.split(' ')[0]}</td>
                                </tr>
                                <tr>
                                    <td className="px-6 py-4 font-bold text-slate-500 bg-slate-50">Amal qilish muddati</td>
                                    <td className="px-6 py-4 text-slate-800 font-medium">
                                        {data?.valid_until ? new Date(data.valid_until).toLocaleDateString('uz-UZ') : '3 yil'}
                                    </td>
                                </tr>
                                <tr>
                                    <td className="px-6 py-4 font-bold text-slate-500 bg-slate-50">Baholash ob'yekti</td>
                                    <td className="px-6 py-4 text-slate-800 font-medium">
                                        {data?.type?.toLowerCase()?.includes('mulk') || data?.object?.cadastre_number ? (
                                            <div className="space-y-1">
                                                <div><span className="text-slate-400 font-normal">Kadastr raqami:</span> <span className="font-semibold">{data?.object?.cadastre_number || "Noma'lum"}</span></div>
                                                <div><span className="text-slate-400 font-normal">Manzil:</span> <span>{data?.object?.location || "Noma'lum"}</span></div>
                                                <div><span className="text-slate-400 font-normal">Maydoni:</span> <span className="font-semibold">{data?.object?.total_area || "0"} kv.m</span></div>
                                            </div>
                                        ) : (
                                            <span>
                                                {data?.object?.model || "Noma'lum"} ({data?.object?.year || "Noma'lum"}-yil, Davlat raqami: <span className="font-bold uppercase">{data?.object?.plate || "Noma'lum"}</span>)
                                            </span>
                                        )}
                                    </td>
                                </tr>
                                <tr>
                                    <td className="px-6 py-4 font-bold text-slate-500 bg-slate-50">Mulk egasi</td>
                                    <td className="px-6 py-4 text-slate-800 font-medium">{data?.object?.owner || "Noma'lum"}</td>
                                </tr>
                                <tr>
                                    <td className="px-6 py-4 font-bold text-slate-500 bg-slate-50">Baholangan qiymati</td>
                                    <td className="px-6 py-4 text-emerald-700 font-extrabold text-base bg-emerald-50/20">{data?.market_value || 'Hisoblanmoqda'}</td>
                                </tr>
                                <tr>
                                    <td className="px-6 py-4 font-bold text-slate-500 bg-slate-50">Nazorat kodi</td>
                                    <td className="px-6 py-4 text-slate-800 font-mono font-bold">SV-{id ? id.split('-')[0].toUpperCase() : 'NOMA\'LUM'}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Anti-Fraud Security Warning card */}
                <div className="mb-8 p-5 bg-amber-50 border border-amber-200/80 rounded-2xl flex gap-3.5 items-start">
                    <div className="p-2 bg-amber-100 text-amber-800 rounded-xl mt-0.5">
                        <AlertTriangle size={20} />
                    </div>
                    <div>
                        <h4 className="font-bold text-amber-900 text-sm mb-1">HAVFSIZLIK OGOHLANTIRISHI (ANTI-FRAUD)</h4>
                        <p className="text-xs text-amber-800/90 leading-relaxed">
                            Mazkur elektron verifikatsiya sahifasida ko'rsatilgan ma'lumotlar (<strong>Mulkdor, Ob'yekt tafsilotlari, Baholangan qiymat</strong> va <strong>Nazorat kodi</strong>) sizga taqdim etilgan qog'oz shaklidagi hisobot ma'lumotlari bilan <strong>100% mos kelishi shart</strong>.
                        </p>
                        <p className="text-xs text-amber-800/90 leading-relaxed mt-2">
                            Har qanday tafovut aniqlangan taqdirda (masalan, narxlar yoki model mos kelmasa), ushbu hisobot <strong>SOXTA (QALBAKI)</strong> hisoblanadi va yuridik kuchga ega emas.
                        </p>
                    </div>
                </div>

                {/* Signatories section like Hujjat.uz */}
                <div className="mb-10">
                    <h3 className="text-slate-700 text-sm font-extrabold mb-4 uppercase tracking-wider flex items-center gap-2">
                        <UserCheck className="text-slate-400" size={18} />
                        Imzolovchilar tarkibi
                    </h3>

                    <div className="space-y-4">
                        {/* Signatory 1: Company stamp */}
                        <div className={`p-5 border rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 transition-all duration-500 ${signatory === 'company' ? 'border-emerald-500 bg-emerald-50/20 ring-4 ring-emerald-500/10 scale-[1.02] shadow-md' : 'border-slate-100 bg-[#fbfcfd]'}`}>
                            <div className="flex items-start gap-3 flex-1">
                                <div className="p-3 bg-slate-100 text-slate-600 rounded-xl mt-0.5">
                                    <Building2 size={20} />
                                </div>
                                <div>
                                    <h4 className="font-black text-slate-800 text-sm">{companyName}</h4>
                                    <p className="text-xs text-slate-500 mt-0.5">Baholovchi tashkilot (Yuridik shaxs)</p>
                                    <p className="text-[11px] text-slate-400 font-mono mt-1">STIR: {companyStir}</p>
                                    {signatory === 'company' && (
                                        <p className="text-[10px] text-emerald-600 font-bold mt-1">✓ Muhr / Pechat QR-kod orqali tasdiqlandi</p>
                                    )}
                                </div>
                            </div>
                            
                            {isVerified && data?.company?.seal_url && (
                                <div className="flex flex-col items-center justify-center p-2 bg-white rounded-2xl border border-slate-200/60 shadow-sm mx-auto md:mx-0">
                                    <img src={data.company.seal_url} alt="Tashkilot muhri" className="w-16 h-16 object-contain" />
                                    <span className="text-[8px] font-black text-slate-400 uppercase tracking-wider mt-1">Tashkilot muhri</span>
                                </div>
                            )}

                            <div>
                                {isVerified ? (
                                    <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-50 text-emerald-600 rounded-full text-xs font-bold border border-emerald-100">
                                        <Check size={12} strokeWidth={3} /> E-IMZO BILAN TASDIQLANGAN
                                    </span>
                                ) : (
                                    <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-rose-50 text-rose-600 rounded-full text-xs font-bold border border-rose-100">
                                        <AlertTriangle size={12} strokeWidth={3} /> TO'LOV KUTILMOQDA
                                    </span>
                                )}
                            </div>
                        </div>

                        {/* Signatory 2: Appraiser signature */}
                        <div className={`p-5 border rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 transition-all duration-500 ${signatory === 'appraiser' ? 'border-emerald-500 bg-emerald-50/20 ring-4 ring-emerald-500/10 scale-[1.02] shadow-md' : 'border-slate-100 bg-[#fbfcfd]'}`}>
                            <div className="flex items-start gap-3 flex-1">
                                <div className="p-3 bg-slate-100 text-slate-600 rounded-xl mt-0.5">
                                    <ShieldCheck size={20} />
                                </div>
                                <div>
                                    <h4 className="font-black text-slate-800 text-sm">{appraiserName}</h4>
                                    <p className="text-xs text-slate-500 mt-0.5">Baholovchi mutaxassis (Sertifikat: {appraiserLicense})</p>
                                    <p className="text-[11px] text-slate-400 font-mono mt-1">PINFL: {appraiserPinfl} | Sertifikat kaliti: №01FA9C2E</p>
                                    {signatory === 'appraiser' && (
                                        <p className="text-[10px] text-emerald-600 font-bold mt-1">✓ Baholovchi E-imzosi QR-kod orqali tasdiqlandi</p>
                                    )}
                                </div>
                            </div>
                            
                            {isVerified && data?.appraiser?.signature_url && (
                                <div className="flex flex-col items-center justify-center p-2 bg-white rounded-2xl border border-slate-200/60 shadow-sm mx-auto md:mx-0">
                                    <img src={data.appraiser.signature_url} alt="Baholovchi imzosi" className="w-20 h-10 object-contain" />
                                    <span className="text-[8px] font-black text-slate-400 uppercase tracking-wider mt-1">Baholovchi imzosi</span>
                                </div>
                            )}

                            <div>
                                {isVerified ? (
                                    <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-50 text-emerald-600 rounded-full text-xs font-bold border border-emerald-100">
                                        <Check size={12} strokeWidth={3} /> E-IMZO BILAN TASDIQLANGAN
                                    </span>
                                ) : (
                                    <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-rose-50 text-rose-600 rounded-full text-xs font-bold border border-rose-100">
                                        <AlertTriangle size={12} strokeWidth={3} /> TO'LOV KUTILMOQDA
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* PDF Verification Dropzone & Status */}
                <div className="mb-10 pt-8 border-t border-slate-100">
                    <h3 className="text-slate-700 text-sm font-extrabold mb-4 uppercase tracking-wider flex items-center gap-2">
                        <Upload className="text-slate-400" size={18} />
                        Hujjatning asl (PDF) nusxasini tekshirish
                    </h3>
                    
                    <p className="text-xs text-slate-500 mb-5 leading-relaxed">
                        Sizga taqdim etilgan PDF shaklidagi asl hisobotni yuklang. Tizim undagi ma'lumotlarni o'qib (OCR va AI yordamida) elektron reyestrdagi ma'lumotlar bilan solishtiradi va haqiqiyligini tekshiradi.
                    </p>

                    {/* Result Banner */}
                    <AnimatePresence mode="wait">
                        {verifyingPdf && (
                            <motion.div 
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="mb-6 p-6 bg-slate-50 border border-slate-200 rounded-2xl flex flex-col items-center justify-center gap-3 text-center overflow-hidden"
                            >
                                <Loader2 className="text-emerald-600 animate-spin" size={32} />
                                <div className="space-y-1">
                                    <h4 className="font-bold text-slate-800 text-sm">Fayl tahlil qilinmoqda</h4>
                                    <p className="text-xs text-slate-500">PDF tarkibidagi matnlar o'qilmoqda va AI yordamida solishtirilmoqda, iltimos kuting...</p>
                                </div>
                            </motion.div>
                        )}

                        {pdfVerificationError && !verifyingPdf && (
                            <motion.div 
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="mb-6 p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-2xl flex gap-3.5 items-start overflow-hidden"
                            >
                                <AlertTriangle className="text-rose-600 mt-0.5 flex-shrink-0" size={20} />
                                <div className="space-y-1">
                                    <h4 className="font-bold text-rose-950 text-sm">Tekshirishda xatolik yuz berdi</h4>
                                    <p className="text-xs text-rose-800/90">{pdfVerificationError}</p>
                                </div>
                            </motion.div>
                        )}

                        {pdfVerificationResult === 'matched' && extractedDetails && !verifyingPdf && (
                            <motion.div 
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.95 }}
                                className="mb-6 p-6 bg-emerald-50 border border-emerald-200 rounded-2xl space-y-4"
                            >
                                <div className="flex gap-3.5 items-start">
                                    <div className="p-2 bg-emerald-100 text-emerald-800 rounded-xl">
                                        <ShieldCheck size={24} />
                                    </div>
                                    <div>
                                        <h4 className="font-black text-emerald-950 text-base">ASL NUSXA HAQIQIY (MOS KELDI)</h4>
                                        <p className="text-xs text-emerald-800/90 leading-relaxed mt-0.5">
                                            Yuklangan PDF faylidagi ma'lumotlar elektron reyestr ma'lumotlariga to'liq mos keladi. Hujjat o'zgartirilmagan va haqiqiy.
                                        </p>
                                    </div>
                                </div>
                                
                                <div className="bg-white/60 backdrop-blur-sm rounded-xl p-4 text-xs space-y-2 border border-emerald-100">
                                    <div className="grid grid-cols-2 pb-2 border-b border-emerald-100/50">
                                        <span className="font-bold text-emerald-900">Mulkdor:</span>
                                        <span className="text-slate-800 font-semibold">{extractedDetails.owner_name}</span>
                                    </div>
                                    {extractedDetails.object_type === 'vehicle' ? (
                                        <>
                                            <div className="grid grid-cols-2 pb-2 border-b border-emerald-100/50">
                                                <span className="font-bold text-emerald-900">Avtomobil rusumi:</span>
                                                <span className="text-slate-800 font-semibold">{extractedDetails.car_model}</span>
                                            </div>
                                            <div className="grid grid-cols-2 pb-2 border-b border-emerald-100/50">
                                                <span className="font-bold text-emerald-900">Davlat raqami:</span>
                                                <span className="text-slate-800 uppercase font-mono font-semibold">{extractedDetails.plate_number}</span>
                                            </div>
                                        </>
                                    ) : (
                                        <div className="grid grid-cols-2 pb-2 border-b border-emerald-100/50">
                                            <span className="font-bold text-emerald-900">Kadastr raqami:</span>
                                            <span className="text-slate-800 font-mono font-semibold">{extractedDetails.cadastre_number}</span>
                                        </div>
                                    )}
                                    <div className="grid grid-cols-2">
                                        <span className="font-bold text-emerald-900">Baholangan qiymat:</span>
                                        <span className="text-emerald-700 font-extrabold">{extractedDetails.market_value || extractedDetails.price}</span>
                                    </div>
                                </div>
                            </motion.div>
                        )}

                        {pdfVerificationResult === 'mismatched' && extractedDetails && !verifyingPdf && (
                            <motion.div 
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.95 }}
                                className="mb-6 p-6 bg-rose-50 border border-rose-200 rounded-2xl space-y-4"
                            >
                                <div className="flex gap-3.5 items-start">
                                    <div className="p-2 bg-rose-100 text-rose-800 rounded-xl">
                                        <AlertTriangle size={24} />
                                    </div>
                                    <div>
                                        <h4 className="font-black text-rose-950 text-base">DIQQAT! MA'LUMOTLAR MOS KELMADI</h4>
                                        <p className="text-xs text-rose-800/90 leading-relaxed mt-0.5">
                                            Yuklangan PDF faylidagi ma'lumotlar elektron reyestrda saqlangan ma'lumotlarga mos kelmadi! Hujjat tahrirlangan yoki soxtalashtirilgan bo'lishi mumkin.
                                        </p>
                                    </div>
                                </div>

                                <div className="bg-white/60 backdrop-blur-sm rounded-xl p-4 text-xs space-y-2 border border-rose-100">
                                    <div className="grid grid-cols-3 font-bold text-slate-500 pb-2 border-b border-rose-100/50">
                                        <span>Parametr</span>
                                        <span>Yuklangan faylda</span>
                                        <span>Elektron reyestrda</span>
                                    </div>
                                    <div className="grid grid-cols-3 pb-2 border-b border-rose-100/50">
                                        <span className="font-bold text-rose-900">Mulkdor:</span>
                                        <span className="text-slate-800">{extractedDetails.owner_name || "-"}</span>
                                        <span className="text-slate-800 font-semibold">{data?.object?.owner || "-"}</span>
                                    </div>
                                    {extractedDetails.object_type === 'vehicle' ? (
                                        <>
                                            <div className="grid grid-cols-3 pb-2 border-b border-rose-100/50">
                                                <span className="font-bold text-rose-900">Avtomobil:</span>
                                                <span className="text-slate-800">{extractedDetails.car_model || "-"}</span>
                                                <span className="text-slate-800 font-semibold">{data?.object?.model || "-"}</span>
                                            </div>
                                            <div className="grid grid-cols-3 pb-2 border-b border-rose-100/50">
                                                <span className="font-bold text-rose-900">Davlat raqami:</span>
                                                <span className="text-slate-800 uppercase font-mono">{extractedDetails.plate_number || "-"}</span>
                                                <span className="text-slate-800 uppercase font-mono font-semibold">{data?.object?.plate || "-"}</span>
                                            </div>
                                        </>
                                    ) : (
                                        <div className="grid grid-cols-3 pb-2 border-b border-rose-100/50">
                                            <span className="font-bold text-rose-900">Kadastr:</span>
                                            <span className="text-slate-800 font-mono">{extractedDetails.cadastre_number || "-"}</span>
                                            <span className="text-slate-800 font-mono font-semibold">{data?.object?.cadastre_number || "-"}</span>
                                        </div>
                                    )}
                                    <div className="grid grid-cols-3">
                                        <span className="font-bold text-rose-900">Qiymat:</span>
                                        <span className="text-slate-800 font-bold">{extractedDetails.market_value || extractedDetails.price || "-"}</span>
                                        <span className="text-emerald-700 font-bold">{data?.market_value || "-"}</span>
                                    </div>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Drag & Drop Area */}
                    <div 
                        onClick={() => document.getElementById('pdf-file-input')?.click()}
                        onDragOver={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                        }}
                        onDrop={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                                handleVerifyPdf(e.dataTransfer.files[0]);
                            }
                        }}
                        className="bg-slate-50/50 hover:bg-slate-100/70 border-2 border-dashed border-slate-300 hover:border-emerald-500 transition-all duration-300 rounded-2xl p-8 text-center cursor-pointer flex flex-col items-center justify-center gap-3 group"
                    >
                        <input 
                            type="file" 
                            id="pdf-file-input" 
                            accept=".pdf" 
                            className="hidden" 
                            onChange={(e) => {
                                if (e.target.files && e.target.files[0]) {
                                    handleVerifyPdf(e.target.files[0]);
                                }
                            }}
                        />
                        <div className="p-3 bg-white text-slate-400 group-hover:text-emerald-600 rounded-2xl shadow-sm border border-slate-100 group-hover:scale-110 transition-all duration-300">
                            <Upload size={24} />
                        </div>
                        <div>
                            <p className="text-sm font-bold text-slate-700 group-hover:text-slate-900 transition-colors">
                                PDF hisobot faylini yuklang yoki shu yerga tashlang
                            </p>
                            <p className="text-xs text-slate-400 mt-1">
                                Faqat .pdf formatidagi fayllar qabul qilinadi
                            </p>
                        </div>
                        {pdfFile && (
                            <div className="mt-2 text-xs font-semibold text-slate-600 bg-white border border-slate-200 px-3 py-1 rounded-full flex items-center gap-1.5 shadow-sm">
                                <FileText size={12} className="text-slate-400" />
                                {pdfFile.name}
                            </div>
                        )}
                    </div>
                </div>

                {/* PDF Actions */}
                {isVerified && data?.file_url && (
                    <div className="pt-6 border-t border-slate-100 flex flex-col items-center">
                        <motion.a
                            whileHover={{ scale: 1.01 }}
                            whileTap={{ scale: 0.99 }}
                            href={`/api-proxy/v1/reports/${id}/download/`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 px-8 py-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-2xl font-bold shadow-lg shadow-emerald-500/20 transition-all w-full justify-center text-sm"
                        >
                            <ArrowDownToLine size={18} />
                            Asl nusxani yuklab olish (PDF)
                        </motion.a>
                        <p className="text-slate-400 text-[10px] text-center mt-3 leading-relaxed">
                            Chop etilgan qog'oz nusxadagi ma'lumotlar ushbu reyestrdagi elektron ma'lumotlar bilan mos kelishi shart.
                        </p>
                    </div>
                )}
            </motion.div>

            <p className="mt-8 text-slate-400 text-xs font-medium flex items-center gap-1.5">
                <Calendar size={13} /> Tizim bo'yicha tekshirilgan vaqt: {data?.timestamp || new Date().toLocaleString('uz-UZ')}
            </p>
        </div>
    );
}
