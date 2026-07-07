"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/services/api';
import { ShieldCheck, Clock, FileText, CheckCircle, XCircle, LogOut, ArrowLeft, Image as ImageIcon, Eye, Download } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { LanguageSwitcher } from '@/i18n/LanguageSwitcher';
import { ThemeToggle } from '@/components/ThemeToggle';

const getMediaUrl = (path: string | null | undefined) => {
    if (!path) return null;
    if (path.startsWith('http')) return path;
    const cleanPath = path.startsWith('/') ? path.substring(1) : path;
    return `/${cleanPath}`;
};

export default function ApprovalsPage() {
    const router = useRouter();
    const [me, setMe] = useState<any>(null);
    const [authLoading, setAuthLoading] = useState(true);
    const [valuations, setValuations] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'vehicle' | 'real-estate'>('vehicle');
    const [selectedReceipt, setSelectedReceipt] = useState<string | null>(null);

    useEffect(() => {
        const fetchMe = async () => {
            try {
                const res = await api.get(`users/me/`);
                if (res.data.role !== 'super_admin' && res.data.role !== 'admin') {
                    window.location.href = '/';
                } else {
                    setMe(res.data);
                }
            } catch (err) {
                window.location.href = '/login';
            } finally {
                setAuthLoading(false);
            }
        };
        fetchMe();
    }, []);

    const fetchVerifyingValuations = async () => {
        try {
            setLoading(true);
            // Fetch all valuations that are in 'verifying' or 'payment_pending' status
            const endpoint = activeTab === 'vehicle' ? '/vehicles/valuations/' : '/real-estate/valuations/';
            const res = await api.get(endpoint);
            // Filter only those that need verification (have receipt or in verifying status)
            const filtered = res.data.filter((v: any) => v.status === 'verifying' || v.status === 'payment_pending');
            setValuations(filtered);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (me) {
            fetchVerifyingValuations();
        }
    }, [me, activeTab]);

    const handleApprovePayment = async (id: number) => {
        if (!window.confirm("To'lov tasdiqlansinmi? Hisobot avtomatik ravishda tayyorlanadi.")) return;
        try {
            const prefix = activeTab === 'vehicle' ? 'vehicles' : 'real-estate';
            await api.patch(`/${prefix}/valuations/${id}/`, { status: 'approved' });
            // Also trigger the final approval/report generation if separate endpoint exists
            if (activeTab === 'real-estate') {
                await api.post(`/real-estate/valuations/${id}/approve/`);
            } else {
                await api.post(`/vehicles/valuations/${id}/approve/`);
            }
            fetchVerifyingValuations();
            alert("To'lov tasdiqlandi!");
        } catch (err) {
            alert("Xatolik yuz berdi");
        }
    };

    const handleRejectPayment = async (id: number) => {
        const reason = window.prompt("Rad etish sababi (Foydalanuvchiga ko'rinadi):");
        if (reason === null) return;
        try {
            const prefix = activeTab === 'vehicle' ? 'vehicles' : 'real-estate';
            await api.patch(`/${prefix}/valuations/${id}/`, { status: 'rejected' });
            fetchVerifyingValuations();
        } catch (err) {
            alert("Xatolik yuz berdi");
        }
    };

    if (authLoading) return <div className="min-h-screen flex justify-center items-center"><div className="animate-spin w-12 h-12 border-t-4 border-blue-500 rounded-full"></div></div>;

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-[#0a0f1c] text-slate-900 dark:text-slate-200">
            <header className="px-6 py-4 flex justify-between items-center bg-white/80 dark:bg-slate-900/40 backdrop-blur-xl border-b border-slate-200 dark:border-white/5 sticky top-0 z-50">
                <div className="flex items-center gap-4">
                    <button onClick={() => router.push('/')} className="p-2.5 mr-2 text-slate-500 hover:text-blue-600 bg-slate-100 dark:bg-slate-800/60 rounded-xl transition-colors">
                        <ArrowLeft size={20} />
                    </button>
                    <h1 className="text-2xl font-black bg-gradient-to-r from-blue-700 to-blue-500 dark:from-white dark:to-blue-400 bg-clip-text text-transparent tracking-tighter">
                        To'lovlar Nazorati
                    </h1>
                </div>
                <div className="flex items-center gap-4">
                    <ThemeToggle />
                    <LanguageSwitcher />
                    <div className="flex flex-col text-right border-l border-slate-200 dark:border-white/10 pl-6">
                        <span className="text-sm font-bold text-slate-800 dark:text-white">{me?.full_name}</span>
                        <span className="text-[10px] text-blue-600 dark:text-blue-400 font-black uppercase tracking-widest">{me?.role === 'super_admin' ? 'Egasi' : 'Admin'}</span>
                    </div>
                </div>
            </header>

            <main className="max-w-6xl mx-auto space-y-6 pt-10 px-6 pb-20">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
                    <div>
                        <h1 className="text-3xl font-black text-slate-800 dark:text-white tracking-tight flex items-center gap-3">
                            <ShieldCheck className="text-emerald-500" size={32} />
                            To'lov Tasdig'ini Kutayotganlar
                        </h1>
                        <p className="text-slate-500 dark:text-slate-400 mt-2">Foydalanuvchilar tomonidan yuklangan cheklarni tekshiring va tasdiqlang.</p>
                    </div>

                    <div className="flex bg-slate-200/50 dark:bg-white/5 p-1 rounded-2xl border border-slate-200 dark:border-white/5">
                        <button
                            onClick={() => setActiveTab('vehicle')}
                            className={`px-6 py-2 rounded-xl text-sm font-black uppercase tracking-wider transition-all ${activeTab === 'vehicle' ? 'bg-white dark:bg-slate-800 text-blue-600 shadow-sm' : 'text-slate-500'}`}
                        >
                            Avtomobillar
                        </button>
                        <button
                            onClick={() => setActiveTab('real-estate')}
                            className={`px-6 py-2 rounded-xl text-sm font-black uppercase tracking-wider transition-all ${activeTab === 'real-estate' ? 'bg-white dark:bg-slate-800 text-indigo-600 shadow-sm' : 'text-slate-500'}`}
                        >
                            Ko'chmas Mulk
                        </button>
                    </div>
                </div>

                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/5 rounded-[40px] shadow-sm overflow-hidden min-h-[400px]">
                    {loading ? (
                        <div className="p-20 flex justify-center"><div className="animate-spin w-10 h-10 border-t-4 border-emerald-500 rounded-full"></div></div>
                    ) : valuations.length === 0 ? (
                        <div className="p-20 text-center text-slate-500 dark:text-slate-400">
                            <Clock className="w-20 h-20 mx-auto mb-4 text-slate-200 dark:text-slate-700" />
                            <h3 className="text-xl font-black mb-2 italic">Hozircha to'lovlar yo'q</h3>
                            <p className="text-sm">Yangi to'lov cheklari yuklanganda bu yerda ko'rinadi.</p>
                        </div>
                    ) : (
                        <div className="p-6 grid grid-cols-1 gap-4">
                            {valuations.map((v, i) => (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: i * 0.05 }}
                                    key={v.id}
                                    className="p-6 bg-slate-50 dark:bg-white/[0.02] rounded-3xl border border-slate-100 dark:border-white/5 flex flex-col md:flex-row justify-between items-center gap-6"
                                >
                                    <div className="flex-1 flex gap-6 items-center">
                                        <div 
                                            className="w-24 h-24 bg-slate-200 dark:bg-slate-800 rounded-2xl overflow-hidden flex-shrink-0 cursor-pointer relative group"
                                            onClick={() => setSelectedReceipt(v.payment_receipt)}
                                        >
                                            {v.payment_receipt ? (
                                                <img src={getMediaUrl(v.payment_receipt)!} alt="Receipt" className="w-full h-full object-cover group-hover:scale-110 transition-transform" />
                                            ) : (
                                                <div className="w-full h-full flex items-center justify-center text-slate-400"><ImageIcon size={32} /></div>
                                            )}
                                            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center text-white transition-opacity">
                                                <Eye size={24} />
                                            </div>
                                        </div>
                                        <div>
                                            <div className="flex items-center gap-3 mb-2">
                                                <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider ${v.status === 'verifying' ? 'bg-amber-500/10 text-amber-500' : 'bg-blue-500/10 text-blue-500'}`}>
                                                    {v.status === 'verifying' ? "Tekshirilmoqda" : "To'lov kutilmoqda"}
                                                </span>
                                                <span className="text-xs text-slate-400 font-bold">ID: {v.id} | {new Date(v.created_at).toLocaleDateString()}</span>
                                            </div>
                                            <h3 className="text-xl font-black text-slate-800 dark:text-white">
                                                {activeTab === 'vehicle' ? `${v.car_model} (${v.year})` : `${v.cadastre_number}`}
                                            </h3>
                                            <p className="text-slate-500 font-bold text-sm">Foydalanuvchi: <span className="text-slate-800 dark:text-slate-300 font-black">User #{v.user}</span></p>
                                            <p className="text-emerald-500 font-black mt-1 text-lg">{Number(v.price_amount).toLocaleString()} so'm</p>
                                        </div>
                                    </div>

                                    <div className="flex gap-3">
                                        <button
                                            onClick={() => handleRejectPayment(v.id)}
                                            className="px-6 py-3 bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-300 dark:hover:bg-slate-700 rounded-2xl font-black text-sm transition-all flex items-center gap-2"
                                        >
                                            <XCircle size={20} /> Rad etish
                                        </button>
                                        <button
                                            onClick={() => handleApprovePayment(v.id)}
                                            disabled={!v.payment_receipt}
                                            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl font-black text-sm shadow-lg shadow-blue-500/30 transition-all flex items-center gap-2 disabled:opacity-50"
                                        >
                                            <CheckCircle size={20} /> To'lovni tasdiqlash
                                        </button>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    )}
                </div>
            </main>

            {/* Receipt Modal */}
            <AnimatePresence>
                {selectedReceipt && (
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md" onClick={() => setSelectedReceipt(null)}>
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                            className="max-w-4xl max-h-[90vh] relative"
                            onClick={e => e.stopPropagation()}
                        >
                            <img src={getMediaUrl(selectedReceipt)!} alt="Full Receipt" className="max-w-full max-h-[80vh] rounded-3xl shadow-2xl border-4 border-white/10" />
                            <div className="absolute -bottom-16 left-1/2 -translate-x-1/2 flex gap-4">
                                <a 
                                    href={getMediaUrl(selectedReceipt)!} 
                                    download 
                                    className="bg-white/10 hover:bg-white/20 backdrop-blur-md text-white px-6 py-3 rounded-2xl flex items-center gap-2 font-black transition-all"
                                >
                                    <Download size={20} /> Yuklab olish
                                </a>
                                <button 
                                    onClick={() => setSelectedReceipt(null)}
                                    className="bg-white text-black px-6 py-3 rounded-2xl font-black transition-all"
                                >
                                    Yopish
                                </button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
}
