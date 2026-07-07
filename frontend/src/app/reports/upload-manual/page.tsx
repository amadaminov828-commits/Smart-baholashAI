"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/services/api';
import { motion, AnimatePresence } from 'framer-motion';
import { 
    Upload, 
    FileText, 
    ArrowLeft, 
    CheckCircle, 
    AlertTriangle, 
    ChevronRight, 
    Car, 
    Home, 
    Download, 
    Eye, 
    Sparkles,
    Settings
} from 'lucide-react';

export default function UploadManualReportPage() {
    const router = useRouter();
    
    // Form States
    const [objectType, setObjectType] = useState<'vehicle' | 'real_estate'>('vehicle');
    const [file, setFile] = useState<File | null>(null);
    const [ownerName, setOwnerName] = useState('');
    
    // Vehicle fields
    const [carModel, setCarModel] = useState('');
    const [plateNumber, setPlateNumber] = useState('');
    const [year, setYear] = useState('');
    
    // Real estate fields
    const [cadastreNumber, setCadastreNumber] = useState('');
    const [totalArea, setTotalArea] = useState('');
    const [location, setLocation] = useState('');
    
    // Advanced options
    const [stampPage, setStampPage] = useState<'first' | 'last'>('last');
    const [stampPosition, setStampPosition] = useState<string>('bottom_left');
    const [showAdvanced, setShowAdvanced] = useState(false);
    
    // Flow States
    const [loading, setLoading] = useState(false);
    const [parsing, setParsing] = useState(false);
    const [parsingSuccess, setParsingSuccess] = useState(false);
    const [error, setError] = useState('');
    const [successData, setSuccessData] = useState<any>(null);
    const [dragActive, setDragActive] = useState(false);

    const processFile = async (selected: File) => {
        if (selected.type !== 'application/pdf') {
            setError("Faqatgina PDF formatidagi hujjatlarni yuklash mumkin.");
            setFile(null);
            return;
        }
        
        setError('');
        setFile(selected);
        
        // Trigger AI auto-fill
        setParsing(true);
        setParsingSuccess(false);
        const formData = new FormData();
        formData.append('file', selected);
        try {
            const res = await api.post('/reports/extract-metadata/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            const parsed = res.data;
            
            if (parsed.object_type) {
                setObjectType(parsed.object_type);
            }
            if (parsed.owner_name) {
                setOwnerName(parsed.owner_name);
            }
            if (parsed.object_type === 'vehicle') {
                if (parsed.car_model) setCarModel(parsed.car_model);
                if (parsed.plate_number) setPlateNumber(parsed.plate_number);
                if (parsed.year) setYear(String(parsed.year));
            } else {
                if (parsed.cadastre_number) setCadastreNumber(parsed.cadastre_number);
                if (parsed.total_area) setTotalArea(String(parsed.total_area));
                if (parsed.location) setLocation(parsed.location);
            }
            setParsingSuccess(true);
        } catch (err: any) {
            console.error("AI parsing error:", err);
            // Do not block the user, let them fill manually
        } finally {
            setParsing(false);
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            processFile(e.target.files[0]);
        }
    };

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            processFile(e.dataTransfer.files[0]);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!file) {
            setError("Iltimos, PDF hisobot faylini yuklang.");
            return;
        }
        if (!ownerName.trim()) {
            setError("Iltimos, mulkdor F.I.Sh. kiriting.");
            return;
        }

        setLoading(true);
        setError('');

        const formData = new FormData();
        formData.append('file', file);
        formData.append('object_type', objectType);
        formData.append('owner_name', ownerName);
        formData.append('stamp_page', stampPage);
        formData.append('stamp_position', stampPosition);

        if (objectType === 'vehicle') {
            formData.append('car_model', carModel || "Noma'lum");
            formData.append('plate_number', plateNumber || "Noma'lum");
            formData.append('year', year || '0');
        } else {
            formData.append('cadastre_number', cadastreNumber || "Noma'lum");
            formData.append('total_area', totalArea || '0');
            formData.append('location', location || "Noma'lum");
        }

        try {
            const res = await api.post('/reports/upload-manual/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            setSuccessData(res.data);
        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.error || "Hisobotni yuklashda xatolik yuz berdi. Iltimos qayta urinib ko'ring.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#0a0f1c] text-slate-200 py-12 px-6 relative overflow-hidden font-sans">
            {/* Neural Background decor */}
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-600/10 blur-[120px] rounded-full pointer-events-none"></div>
            <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-600/10 blur-[120px] rounded-full pointer-events-none"></div>

            <div className="max-w-3xl mx-auto relative z-10">
                {/* Header */}
                <div className="flex justify-between items-center mb-12">
                    <button
                        onClick={() => router.push('/reports')}
                        className="flex items-center gap-2 px-5 py-2.5 bg-white/5 hover:bg-white/10 rounded-xl border border-white/5 text-sm font-bold text-slate-400 transition-all"
                    >
                        <ArrowLeft size={16} /> Hisobotlarga qaytish
                    </button>
                    
                    <span className="text-sm font-black tracking-tight text-slate-500 uppercase select-none">
                        Tashqi hujjatlar reyestri
                    </span>
                </div>

                <AnimatePresence mode="wait">
                    {!successData ? (
                        <motion.div
                            initial={{ opacity: 0, y: 15 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -15 }}
                            className="bg-slate-900/40 backdrop-blur-xl border border-white/5 rounded-[40px] p-6 md:p-10 shadow-2xl"
                        >
                            <div className="flex items-center gap-4 mb-8">
                                <div className="w-12 h-12 bg-emerald-500/10 text-emerald-400 rounded-2xl flex items-center justify-center border border-emerald-500/20">
                                    <Sparkles size={24} />
                                </div>
                                <div>
                                    <h1 className="text-3xl font-black text-white tracking-tight">Tashqi hisobot yuklash</h1>
                                    <p className="text-slate-400 text-xs mt-1">Qo'lda yozilgan PDF hisobotga QR va E-imzo shtampini bosish</p>
                                </div>
                            </div>

                            {error && (
                                <div className="mb-6 p-4 bg-rose-500/10 border border-rose-500/20 rounded-2xl flex items-start gap-3 text-rose-300 text-sm">
                                    <AlertTriangle className="mt-0.5 shrink-0" size={18} />
                                    <span>{error}</span>
                                </div>
                            )}

                            <form onSubmit={handleSubmit} className="space-y-6">
                                {/* Object Type Selector */}
                                <div className="grid grid-cols-2 gap-4">
                                    <button
                                        type="button"
                                        onClick={() => { setObjectType('vehicle'); setError(''); }}
                                        className={`p-5 rounded-2xl border flex flex-col items-center gap-3 transition-all duration-300 ${objectType === 'vehicle' ? 'bg-blue-600/10 border-blue-500/40 text-blue-400' : 'bg-white/5 border-white/5 hover:bg-white/10 text-slate-400'}`}
                                    >
                                        <Car size={32} />
                                        <span className="font-black text-sm uppercase tracking-wider">Avtotransport</span>
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => { setObjectType('real_estate'); setError(''); }}
                                        className={`p-5 rounded-2xl border flex flex-col items-center gap-3 transition-all duration-300 ${objectType === 'real_estate' ? 'bg-emerald-600/10 border-emerald-500/40 text-emerald-400' : 'bg-white/5 border-white/5 hover:bg-white/10 text-slate-400'}`}
                                    >
                                        <Home size={32} />
                                        <span className="font-black text-sm uppercase tracking-wider">Ko'chmas mulk</span>
                                    </button>
                                </div>

                                {/* PDF Dropzone */}
                                <div>
                                    <label className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-2.5">PDF Hujjat fayli</label>
                                    <label
                                        onDragEnter={handleDrag}
                                        onDragOver={handleDrag}
                                        onDragLeave={handleDrag}
                                        onDrop={handleDrop}
                                        className={`relative block border-2 border-dashed rounded-3xl p-8 text-center transition-all bg-white/2 cursor-pointer group ${dragActive ? 'border-emerald-500 bg-emerald-500/5' : 'border-white/10 hover:border-emerald-500/30'}`}
                                    >
                                        <input
                                            type="file"
                                            accept=".pdf"
                                            onChange={handleFileChange}
                                            className="hidden"
                                        />
                                        <div className="flex flex-col items-center gap-3">
                                            <div className="w-14 h-14 bg-white/5 text-slate-400 group-hover:text-emerald-400 rounded-2xl flex items-center justify-center transition-colors">
                                                {parsing ? (
                                                    <div className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
                                                ) : (
                                                    <Upload size={28} />
                                                )}
                                            </div>
                                            {parsing ? (
                                                <div>
                                                    <p className="text-emerald-400 font-bold text-sm animate-pulse">AI hujjatni o'qimoqda...</p>
                                                    <p className="text-slate-500 text-xs mt-1">Maydonlar avtomatik to'ldiriladi</p>
                                                </div>
                                            ) : file ? (
                                                <div>
                                                    <p className="text-white font-bold text-sm">{file.name}</p>
                                                    <p className="text-slate-500 text-xs mt-1">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                                                    {parsingSuccess && (
                                                        <span className="inline-block mt-2 text-[10px] bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-black px-2.5 py-1 rounded-full uppercase tracking-wider">
                                                            ✓ AI maydonlarni to'ldirdi
                                                        </span>
                                                    )}
                                                </div>
                                            ) : (
                                                <div>
                                                    <p className="text-slate-300 font-bold text-sm">PDF faylni sudrab o'tkazing yoki tanlang</p>
                                                    <p className="text-slate-500 text-xs mt-1">Ruxsat etilgan maksimal hajm: 50MB</p>
                                                </div>
                                            )}
                                        </div>
                                    </label>
                                </div>


                                {/* Common Metadata Fields */}
                                <div className="grid md:grid-cols-2 gap-6">
                                    <div className="col-span-2">
                                        <label className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-2.5">Mulkdor F.I.Sh.</label>
                                        <input
                                            type="text"
                                            value={ownerName}
                                            onChange={(e) => setOwnerName(e.target.value)}
                                            placeholder="Masalan: BOLTABOYEV AVAZBEK ERKINJONOVICH"
                                            className="w-full bg-white/5 border border-white/5 rounded-2xl px-5 py-4 focus:outline-none focus:border-emerald-500/40 text-white placeholder-slate-600 font-medium"
                                            required
                                        />
                                    </div>

                                    {/* Conditional Metadata fields */}
                                    {objectType === 'vehicle' ? (
                                        <>
                                            <div>
                                                <label className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-2.5">Avtomobil rusumi</label>
                                                <input
                                                    type="text"
                                                    value={carModel}
                                                    onChange={(e) => setCarModel(e.target.value)}
                                                    placeholder="Masalan: CHEVROLET COBALT"
                                                    className="w-full bg-white/5 border border-white/5 rounded-2xl px-5 py-4 focus:outline-none focus:border-emerald-500/40 text-white placeholder-slate-600 font-medium"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-2.5">Davlat raqami</label>
                                                <input
                                                    type="text"
                                                    value={plateNumber}
                                                    onChange={(e) => setPlateNumber(e.target.value)}
                                                    placeholder="Masalan: 40O205PA"
                                                    className="w-full bg-white/5 border border-white/5 rounded-2xl px-5 py-4 focus:outline-none focus:border-emerald-500/40 text-white placeholder-slate-600 font-medium uppercase"
                                                />
                                            </div>
                                            <div className="col-span-2">
                                                <label className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-2.5">Ishlab chiqarilgan yili</label>
                                                <input
                                                    type="number"
                                                    value={year}
                                                    onChange={(e) => setYear(e.target.value)}
                                                    placeholder="Masalan: 2023"
                                                    className="w-full bg-white/5 border border-white/5 rounded-2xl px-5 py-4 focus:outline-none focus:border-emerald-500/40 text-white placeholder-slate-600 font-medium"
                                                />
                                            </div>
                                        </>
                                    ) : (
                                        <>
                                            <div>
                                                <label className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-2.5">Kadastr raqami</label>
                                                <input
                                                    type="text"
                                                    value={cadastreNumber}
                                                    onChange={(e) => setCadastreNumber(e.target.value)}
                                                    placeholder="Masalan: 15:11:41:01:01:1259"
                                                    className="w-full bg-white/5 border border-white/5 rounded-2xl px-5 py-4 focus:outline-none focus:border-emerald-500/40 text-white placeholder-slate-600 font-medium"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-2.5">Umumiy maydon (kv.m)</label>
                                                <input
                                                    type="text"
                                                    value={totalArea}
                                                    onChange={(e) => setTotalArea(e.target.value)}
                                                    placeholder="Masalan: 79.4"
                                                    className="w-full bg-white/5 border border-white/5 rounded-2xl px-5 py-4 focus:outline-none focus:border-emerald-500/40 text-white placeholder-slate-600 font-medium"
                                                />
                                            </div>
                                            <div className="col-span-2">
                                                <label className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-2.5">Joylashuv (Manzil)</label>
                                                <input
                                                    type="text"
                                                    value={location}
                                                    onChange={(e) => setLocation(e.target.value)}
                                                    placeholder="Masalan: Farg'ona viloyati, Bog'dod tumani"
                                                    className="w-full bg-white/5 border border-white/5 rounded-2xl px-5 py-4 focus:outline-none focus:border-emerald-500/40 text-white placeholder-slate-600 font-medium"
                                                />
                                            </div>
                                        </>
                                    )}
                                </div>

                                {/* Advanced Options Accordion */}
                                <div className="border border-white/5 rounded-2xl overflow-hidden bg-white/1">
                                    <button
                                        type="button"
                                        onClick={() => setShowAdvanced(!showAdvanced)}
                                        className="w-full px-5 py-4 flex items-center justify-between hover:bg-white/2 text-left transition-all"
                                    >
                                        <span className="flex items-center gap-2 text-xs font-black text-slate-400 uppercase tracking-widest">
                                            <Settings size={14} /> Muhr (Shtamp) sozlamalari
                                        </span>
                                        <ChevronRight size={16} className={`text-slate-400 transition-transform ${showAdvanced ? 'rotate-90' : ''}`} />
                                    </button>

                                    {showAdvanced && (
                                        <div className="p-5 border-t border-white/5 space-y-4 grid md:grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">Shtamp sahifasi</label>
                                                <select
                                                    value={stampPage}
                                                    onChange={(e) => setStampPage(e.target.value as any)}
                                                    className="w-full bg-slate-900 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-500/40 text-white"
                                                >
                                                    <option value="last">Oxirgi sahifaga</option>
                                                    <option value="first">Birinchi sahifaga</option>
                                                </select>
                                            </div>

                                            <div>
                                                <label className="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">Shtamp joylashuvi (Burchak)</label>
                                                <select
                                                    value={stampPosition}
                                                    onChange={(e) => setStampPosition(e.target.value)}
                                                    className="w-full bg-slate-900 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-500/40 text-white"
                                                >
                                                    <option value="bottom_left">Pastki chap burchak</option>
                                                    <option value="bottom_right">Pastki o'ng burchak</option>
                                                    <option value="top_left">Yuqori chap burchak</option>
                                                    <option value="top_right">Yuqori o'ng burchak</option>
                                                </select>
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {/* Submit button */}
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full py-5 bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-500 hover:to-teal-600 disabled:opacity-50 text-white font-black rounded-2xl shadow-xl hover:-translate-y-0.5 transition-all uppercase tracking-widest text-sm flex items-center justify-center gap-3"
                                >
                                    {loading ? (
                                        <>
                                            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                            <span>Shtamp bosilmoqda...</span>
                                        </>
                                    ) : (
                                        <>
                                            <Sparkles size={18} />
                                            <span>Tasdiqlash va Shtamp bosish</span>
                                        </>
                                    )}
                                </button>
                            </form>
                        </motion.div>
                    ) : (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="bg-slate-900/40 backdrop-blur-xl border border-white/5 rounded-[60px] p-8 md:p-12 shadow-2xl text-center"
                        >
                            <div className="w-20 h-20 bg-emerald-500/10 text-emerald-400 rounded-[30px] flex items-center justify-center mx-auto mb-8 border border-emerald-500/20 shadow-lg">
                                <CheckCircle size={40} />
                            </div>

                            <h2 className="text-3xl font-black text-white mb-2 tracking-tight uppercase">Muvaffaqiyatli ro'yxatdan o'tdi!</h2>
                            <p className="text-slate-400 max-w-md mx-auto mb-10 text-sm">
                                Hujjat muvaffaqiyatli yuklandi hamda yashil Elektron Imzo shtampi va QR-kodi bilan muhrlandi.
                            </p>

                            {/* QR and Verification block */}
                            <div className="bg-slate-950/40 border border-white/5 rounded-3xl p-6 mb-10 max-w-sm mx-auto flex flex-col items-center gap-4">
                                {successData.qr_url && (
                                    <div className="p-3 bg-white rounded-2xl shadow-inner">
                                        <img
                                            src={successData.qr_url}
                                            alt="Verification QR"
                                            className="w-40 h-40"
                                        />
                                    </div>
                                )}
                                <div className="text-center">
                                    <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Skanerlash havolasi</p>
                                    <a 
                                        href={successData.verify_url} 
                                        target="_blank" 
                                        rel="noreferrer"
                                        className="text-xs text-emerald-400 font-semibold underline block mt-1 break-all hover:text-emerald-300"
                                    >
                                        {successData.verify_url}
                                    </a>
                                </div>
                            </div>

                            {/* Action Buttons */}
                            <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
                                <a
                                    href={successData.file_url}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="flex-1 py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-black rounded-2xl shadow-lg transition-all flex items-center justify-center gap-2 text-sm uppercase tracking-wider"
                                >
                                    <Download size={18} />
                                    PDF yuklab olish
                                </a>
                                <a
                                    href={successData.verify_url}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="flex-1 py-4 bg-slate-800 hover:bg-slate-700 text-slate-300 font-black rounded-2xl border border-white/5 transition-all flex items-center justify-center gap-2 text-sm uppercase tracking-wider"
                                >
                                    <Eye size={18} />
                                    Reyestrni ko'rish
                                </a>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}
