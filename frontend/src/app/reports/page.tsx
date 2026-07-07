"use client";

import { useState, useEffect } from 'react';
import { api } from '@/services/api';
import { motion, AnimatePresence } from 'framer-motion';
import {
    FileText,
    FileDown,
    Search,
    ArrowLeft,
    Calendar,
    FileSearch,
    ChevronRight,
    TrendingUp,
    Sparkles
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import AIReviewPanel from '@/components/AIReviewPanel';

export default function ReportsHistoryPage() {
    const router = useRouter();
    const [reports, setReports] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeReviewReportId, setActiveReviewReportId] = useState<string | null>(null);

    useEffect(() => {
        api.get('/reports/')
            .then(res => {
                setReports(res.data);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    return (
        <div className="min-h-screen bg-[#0a0f1c] text-slate-200 py-12 px-6 relative overflow-hidden font-sans">
            {/* Background Neural Decorations */}
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/10 blur-[120px] rounded-full shadow-[0_0_100px_rgba(37,99,235,0.1)] pointer-events-none"></div>
            <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-indigo-600/10 blur-[120px] rounded-full pointer-events-none"></div>

            <div className="max-w-5xl mx-auto relative z-10">
                {/* Header Section */}
                <motion.div
                    initial={{ y: -20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    className="flex flex-col md:flex-row justify-between items-center mb-16 gap-6"
                >
                    <div className="text-center md:text-left flex items-center gap-8">
                        <div className="relative cursor-pointer group" onClick={() => router.push('/')}>
                            <div className="w-24 h-24 rounded-full overflow-hidden border-[5px] border-slate-900 shadow-[0_0_15px_rgba(59,130,246,0.3)] bg-[#0a0f1c]">
                                <img
                                    src="/logo.png?v=Neural"
                                    alt="Logo"
                                    className="w-full h-full object-cover scale-[1.45] group-hover:scale-[1.5] transition-transform duration-500"
                                />
                            </div>
                        </div>
                        <div>
                            <h1 className="text-5xl font-black bg-gradient-to-r from-white via-blue-200 to-indigo-400 bg-clip-text text-transparent tracking-tighter">
                                Mening Hisobotlarim
                            </h1>
                            <p className="text-slate-400 mt-2 font-medium flex items-center gap-2">
                                <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
                                Barcha yaratilgan baholash hujjatlari arxivi
                            </p>
                        </div>
                    </div>
                    <div className="flex flex-wrap gap-4">
                        <button
                            onClick={() => router.push('/reports/upload-manual')}
                            className="flex items-center gap-2 px-6 py-3 bg-emerald-600/20 hover:bg-emerald-600/35 text-emerald-400 rounded-2xl border border-emerald-500/20 text-sm font-bold transition-all shadow-[0_0_15px_rgba(16,185,129,0.1)]"
                        >
                            <Sparkles size={16} /> Tashqi hisobot yuklash (QR & Shtamp)
                        </button>
                        <button
                            onClick={() => router.push('/')}
                            className="flex items-center gap-2 px-6 py-3 bg-white/5 hover:bg-white/10 rounded-2xl border border-white/5 text-sm font-bold text-slate-400 transition-all"
                        >
                            <ArrowLeft size={16} /> Bosh sahifa
                        </button>
                    </div>
                </motion.div>

                {loading ? (
                    <div className="flex justify-center py-40">
                        <div className="flex flex-col items-center gap-6">
                            <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                            <p className="text-slate-500 font-black tracking-widest uppercase text-xs">Arxiv yuklanmoqda...</p>
                        </div>
                    </div>
                ) : reports.length === 0 ? (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="bg-slate-900/40 backdrop-blur-xl p-20 rounded-[60px] border border-white/5 shadow-2xl text-center"
                    >
                        <div className="w-24 h-24 bg-blue-500/10 text-blue-400 rounded-[35px] flex items-center justify-center mx-auto mb-10 border border-blue-500/20">
                            <FileSearch size={48} />
                        </div>
                        <h3 className="text-3xl font-black text-white mb-4 tracking-tighter uppercase">Hali hisobotlar yo'q</h3>
                        <p className="text-slate-400 max-w-sm mx-auto mb-12 font-medium">Siz hali birorta ham baholash hisobotini yaratmagansiz.</p>
                        <Link href="/" className="inline-block px-10 py-5 bg-gradient-to-r from-blue-600 to-indigo-700 text-white font-black rounded-2xl shadow-2xl hover:-translate-y-1 transition-all uppercase tracking-widest text-sm">
                            Yangi Hisobot Yaratish
                        </Link>
                    </motion.div>
                ) : (
                    <div className="grid gap-6">
                        <AnimatePresence>
                            {reports.map((report, idx) => (
                                <motion.div
                                    key={report.id}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: idx * 0.05 }}
                                    className="bg-slate-900/40 backdrop-blur-md p-8 rounded-[40px] border border-white/5 flex flex-col lg:flex-row lg:items-center justify-between group hover:bg-slate-900/60 hover:border-blue-500/30 transition-all duration-500 shadow-xl"
                                >
                                    <div className="flex items-center gap-8 mb-6 lg:mb-0">
                                        <div className="w-16 h-16 bg-blue-600/10 rounded-[24px] flex items-center justify-center text-blue-400 border border-blue-500/10 group-hover:bg-blue-600 group-hover:text-white transition-all duration-500 shadow-lg">
                                            <FileText size={32} />
                                        </div>
                                        <div>
                                            <h3 className="font-black text-2xl text-white tracking-tight uppercase group-hover:text-blue-200 transition-colors mb-2">
                                                {report.title ? report.title : `Hisobot #${report.id.substring(0, 6)}`}
                                            </h3>
                                            <div className="flex flex-wrap items-center gap-4">
                                                <span className="flex items-center gap-2 bg-white/5 px-4 py-1.5 rounded-full border border-white/5 text-[10px] font-black text-slate-400 uppercase tracking-widest">
                                                    <Calendar size={14} className="text-blue-500" /> {new Date(report.created_at).toLocaleDateString()}
                                                </span>
                                                <span className="flex items-center gap-2 bg-white/5 px-4 py-1.5 rounded-full border border-white/5 text-[10px] font-black text-slate-400 uppercase tracking-widest">
                                                    <TrendingUp size={14} className="text-emerald-500" /> {report.type === 'Mashina' ? 'Mashina' : 'Ko\'chmas mulk'}
                                                </span>
                                                {report.price && (
                                                    <span className="flex items-center gap-2 bg-emerald-500/10 px-4 py-1.5 rounded-full border border-emerald-500/20 text-[10px] font-black text-emerald-400 uppercase tracking-widest">
                                                        {report.price}
                                                    </span>
                                                )}

                                                                {/* STATUS BADGES */}
                                                                {(() => {
                                                                    let finalStatus = report.valuation_status || report.status || 'draft';
                                                                    if (finalStatus === 'draft' && report.valuation_id) {
                                                                        finalStatus = 'pending'; // Backend bug fallback
                                                                    }
                                                                    return (
                                                                        <>
                                                                            {finalStatus === 'approved' ? (
                                                                                <span className="flex items-center gap-2 bg-blue-500/10 px-4 py-1.5 rounded-full border border-blue-500/20 text-[10px] font-black text-blue-400 uppercase tracking-widest">
                                                                                    Tasdiqlangan
                                                                                </span>
                                                                            ) : (
                                                                                <div className="flex flex-col gap-2">
                                                                                    <span className="flex items-center gap-2 bg-red-500/10 px-4 py-1.5 rounded-full border border-red-500/20 text-[10px] font-black text-red-400 uppercase tracking-widest">
                                                                                        Tasdiqlanmagan
                                                                                    </span>
                                                                                    {finalStatus === 'rejected' && report.feedback && (
                                                                                        <div className="text-[11px] font-medium text-red-300 bg-red-950/40 px-3 py-2 rounded-lg border border-red-500/20 w-fit max-w-[250px]">
                                                                                            <span className="font-bold text-red-400 block mb-0.5">Izoh:</span>
                                                                                            {report.feedback}
                                                                                        </div>
                                                                                    )}
                                                                                </div>
                                                                            )}
                                                                        </>
                                                                    );
                                                                })()}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex flex-wrap items-center gap-4 mt-4 lg:mt-0">
                                        {(() => {
                                            let finalStatus = report.valuation_status || report.status || 'draft';
                                            if (finalStatus === 'draft' && report.valuation_id) {
                                                finalStatus = 'pending';
                                            }
                                            // Only approved reports should show PDF, everything else gets TAHRIRLASH so they can edit or view status
                                            return (finalStatus !== 'approved') && report.valuation_id ? (
                                                <a href={`/vehicles?edit=${report.valuation_id}`} className="flex-1 lg:flex-none px-8 py-4 bg-orange-500/10 text-orange-400 hover:bg-orange-500 hover:text-white border border-orange-500/20 rounded-2xl font-black text-sm transition-all flex items-center justify-center gap-3 uppercase tracking-widest">
                                                    <FileText size={20} /> TAHRIRLASH
                                                </a>
                                            ) : (
                                                <>
                                                    {report.docx_url && (
                                                        <>
                                                            <button 
                                                                onClick={() => setActiveReviewReportId(report.id)}
                                                                className="flex-1 lg:flex-none px-8 py-4 bg-purple-600/10 text-purple-400 hover:bg-purple-600 hover:text-white border border-purple-500/20 rounded-2xl font-black text-sm transition-all flex items-center justify-center gap-3 uppercase tracking-widest"
                                                            >
                                                                <Sparkles size={20} /> AI TAHRIRCHI
                                                            </button>
                                                            <a href={report.docx_url} download={`Hisobot_${report.id.substring(0, 6)}.docx`} className="flex-1 lg:flex-none px-8 py-4 bg-blue-600/10 text-blue-400 hover:bg-blue-600 hover:text-white border border-blue-500/20 rounded-2xl font-black text-sm transition-all flex items-center justify-center gap-3 uppercase tracking-widest">
                                                                <FileText size={20} /> WORD
                                                            </a>
                                                        </>
                                                    )}
                                                    {report.file_url && (
                                                        <a href={report.file_url} target="_blank" rel="noreferrer" className="flex-1 lg:flex-none px-8 py-4 bg-emerald-600/10 text-emerald-400 hover:bg-emerald-600 hover:text-white border border-emerald-500/20 rounded-2xl font-black text-sm transition-all flex items-center justify-center gap-3 uppercase tracking-widest">
                                                            <FileDown size={20} /> PDF
                                                        </a>
                                                    )}
                                                    <a href={`/verify-report/${report.id}`} target="_blank" rel="noreferrer" className="flex-1 lg:flex-none px-8 py-4 bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white border border-white/5 rounded-2xl font-black text-sm transition-all flex items-center justify-center gap-3 uppercase tracking-widest group/btn">
                                                        <Search size={20} /> QR / TEKSHIRISH
                                                    </a>
                                                </>
                                            );
                                        })()}
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    </div>
                )}
            </div>

            <AnimatePresence>
                {activeReviewReportId && (
                    <AIReviewPanel 
                        reportId={activeReviewReportId}
                        onClose={() => setActiveReviewReportId(null)}
                        onSuccess={() => {
                            api.get('/reports/').then(res => setReports(res.data));
                        }}
                    />
                )}
            </AnimatePresence>
        </div>
    );
}
