"use client";

import { useState } from 'react';
import { api } from '@/services/api';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Sparkles,
    AlertTriangle,
    CheckCircle,
    X,
    User,
    Briefcase,
    RefreshCw,
    Download,
    FileText,
    Check,
    AlertCircle
} from 'lucide-react';

interface AIReviewPanelProps {
    reportId: string;
    onClose: () => void;
    onSuccess: () => void;
}

export default function AIReviewPanel({ reportId, onClose, onSuccess }: AIReviewPanelProps) {
    const [step, setStep] = useState<'select' | 'scanning' | 'results' | 'success'>('select');
    const [isPhysical, setIsPhysical] = useState<boolean>(true);
    const [healthScore, setHealthScore] = useState<number>(100);
    const [issues, setIssues] = useState<any[]>([]);
    const [selectedIssueIds, setSelectedIssueIds] = useState<string[]>([]);
    const [scanningError, setScanningError] = useState<string | null>(null);
    const [isApplying, setIsApplying] = useState<boolean>(false);

    // Run AI analysis
    const handleStartScan = async () => {
        setStep('scanning');
        setScanningError(null);
        try {
            const res = await api.post(`/reports/${reportId}/ai-review/`, {
                is_physical: isPhysical
            });
            
            if (res.data.error) {
                throw new Error(res.data.error);
            }
            
            setHealthScore(res.data.health_score || 100);
            const foundIssues = res.data.issues || [];
            setIssues(foundIssues);
            // Auto select all detected issues
            setSelectedIssueIds(foundIssues.map((issue: any) => issue.id));
            setStep('results');
        } catch (err: any) {
            console.error(err);
            setScanningError(err.response?.data?.error || err.message || "Tahlil jarayonida xatolik yuz berdi.");
            setStep('select');
        }
    };

    // Toggle individual correction
    const toggleIssueSelection = (id: string) => {
        if (selectedIssueIds.includes(id)) {
            setSelectedIssueIds(selectedIssueIds.filter(i => i !== id));
        } else {
            setSelectedIssueIds([...selectedIssueIds, id]);
        }
    };

    // Toggle all corrections
    const toggleAllIssues = () => {
        if (selectedIssueIds.length === issues.length) {
            setSelectedIssueIds([]);
        } else {
            setSelectedIssueIds(issues.map(i => i.id));
        }
    };

    // Apply selected fixes
    const handleApplyFixes = async () => {
        if (selectedIssueIds.length === 0) return;
        setIsApplying(true);
        try {
            const selectedCorrections = issues.filter(issue => selectedIssueIds.includes(issue.id));
            await api.post(`/reports/${reportId}/ai-review-apply/`, {
                corrections: selectedCorrections
            });
            setIsApplying(false);
            setStep('success');
            onSuccess(); // Refresh reports list in parent
        } catch (err: any) {
            console.error(err);
            alert("Tuzatishlarni qo'llashda xatolik yuz berdi: " + (err.response?.data?.error || err.message));
            setIsApplying(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
            <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.95, opacity: 0 }}
                className="bg-[#0f1626] border border-white/10 rounded-[32px] w-full max-w-2xl overflow-hidden shadow-2xl flex flex-col relative"
                style={{ maxHeight: '90vh' }}
            >
                {/* Header */}
                <div className="p-6 border-b border-white/5 flex justify-between items-center bg-gradient-to-r from-blue-900/10 to-indigo-900/10">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-400 border border-blue-500/20">
                            <Sparkles size={20} className="animate-pulse" />
                        </div>
                        <div>
                            <h3 className="font-black text-xl text-white tracking-tight">AI Tahrirchi Yordamchi</h3>
                            <p className="text-xs text-slate-400 font-medium">Hisobotdagi xatoliklarni tekshirish va tuzatish</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="w-10 h-10 rounded-xl bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white flex items-center justify-center transition-all"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6">
                    {scanningError && (
                        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-2xl flex items-start gap-3 text-sm font-medium">
                            <AlertCircle size={20} className="shrink-0 mt-0.5" />
                            <div>{scanningError}</div>
                        </div>
                    )}

                    {step === 'select' && (
                        <div className="flex flex-col items-center py-6">
                            <h4 className="text-lg font-bold text-white mb-6 text-center">
                                Hisobot kim uchun tayyorlangan?
                            </h4>
                            
                            <div className="grid grid-cols-2 gap-4 w-full max-w-md mb-8">
                                <button
                                    onClick={() => setIsPhysical(true)}
                                    className={`p-6 rounded-2xl border text-left transition-all flex flex-col items-start gap-4 ${
                                        isPhysical
                                            ? 'bg-blue-600/10 border-blue-500 text-white shadow-lg shadow-blue-500/10'
                                            : 'bg-white/5 border-white/5 hover:bg-white/10 text-slate-400'
                                    }`}
                                >
                                    <div className={`p-3 rounded-xl ${isPhysical ? 'bg-blue-500 text-white' : 'bg-white/5 text-slate-400'}`}>
                                        <User size={24} />
                                    </div>
                                    <div>
                                        <h5 className="font-bold text-base">Jismoniy Shaxs</h5>
                                        <p className="text-xs mt-1 opacity-70">Fuqaro, xususiy mulk egasi yoki shaxsiy pasportli mijozlar uchun</p>
                                    </div>
                                </button>

                                <button
                                    onClick={() => setIsPhysical(false)}
                                    className={`p-6 rounded-2xl border text-left transition-all flex flex-col items-start gap-4 ${
                                        !isPhysical
                                            ? 'bg-indigo-600/10 border-indigo-500 text-white shadow-lg shadow-indigo-500/10'
                                            : 'bg-white/5 border-white/5 hover:bg-white/10 text-slate-400'
                                    }`}
                                >
                                    <div className={`p-3 rounded-xl ${!isPhysical ? 'bg-indigo-500 text-white' : 'bg-white/5 text-slate-400'}`}>
                                        <Briefcase size={24} />
                                    </div>
                                    <div>
                                        <h5 className="font-bold text-base">Yuridik Shaxs</h5>
                                        <p className="text-xs mt-1 opacity-70">Kompaniyalar, MCHJ, davlat yoki xususiy tashkilotlar uchun</p>
                                    </div>
                                </button>
                            </div>

                            <button
                                onClick={handleStartScan}
                                className="w-full max-w-xs py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold rounded-2xl transition-all flex items-center justify-center gap-3 uppercase tracking-widest text-sm shadow-xl shadow-blue-500/20"
                            >
                                <Sparkles size={18} /> Tahlilni Boshlash
                            </button>
                        </div>
                    )}

                    {step === 'scanning' && (
                        <div className="flex flex-col items-center justify-center py-16">
                            <div className="relative mb-8">
                                <div className="w-20 h-20 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin"></div>
                                <div className="absolute inset-0 flex items-center justify-center text-blue-400">
                                    <Sparkles size={24} className="animate-pulse" />
                                </div>
                            </div>
                            <h4 className="text-lg font-bold text-white mb-2">Gemini AI hisobotni o'rganmoqda...</h4>
                            <p className="text-sm text-slate-400 text-center max-w-xs">
                                Matn tahlil qilinmoqda, jismoniy/yuridik shaxslar atamalari va grammatika tekshirilmoqda.
                            </p>
                        </div>
                    )}

                    {step === 'results' && (
                        <div>
                            {/* Score Card */}
                            <div className="p-6 bg-white/5 rounded-3xl border border-white/5 mb-6 flex items-center justify-between">
                                <div>
                                    <h5 className="font-black text-xl text-white mb-1">
                                        Hisobot Sifati: {healthScore}%
                                    </h5>
                                    <p className="text-xs text-slate-400 font-medium">
                                        {issues.length === 0 
                                            ? "Hech qanday xatolik topilmadi. Hisobotingiz mukammal holatda!" 
                                            : `Hisobotda ${issues.length} ta tuzatilishi tavsiya etilgan xatolik aniqlandi.`}
                                    </p>
                                </div>
                                <div className="relative flex items-center justify-center">
                                    <div className="w-16 h-16 rounded-full border-4 border-white/5 flex items-center justify-center">
                                        <span className={`text-lg font-black ${healthScore > 90 ? 'text-emerald-400' : healthScore > 70 ? 'text-yellow-400' : 'text-red-400'}`}>
                                            {healthScore}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            {issues.length > 0 && (
                                <>
                                    {/* Select All */}
                                    <div className="flex justify-between items-center mb-4 px-2">
                                        <span className="text-xs text-slate-400 font-black uppercase tracking-wider">Topilgan Xatolar</span>
                                        <button
                                            onClick={toggleAllIssues}
                                            className="text-xs text-blue-400 hover:text-blue-300 font-bold transition-all"
                                        >
                                            {selectedIssueIds.length === issues.length ? "Barchasini bekor qilish" : "Barchasini tanlash"}
                                        </button>
                                    </div>

                                    {/* Issues List */}
                                    <div className="grid gap-4 max-h-[350px] overflow-y-auto pr-1">
                                        {issues.map((issue) => (
                                            <div
                                                key={issue.id}
                                                onClick={() => toggleIssueSelection(issue.id)}
                                                className={`p-4 rounded-2xl border transition-all cursor-pointer flex gap-4 items-start ${
                                                    selectedIssueIds.includes(issue.id)
                                                        ? 'bg-blue-600/5 border-blue-500/40'
                                                        : 'bg-white/5 border-white/5 hover:bg-white/10'
                                                }`}
                                            >
                                                <input
                                                    type="checkbox"
                                                    checked={selectedIssueIds.includes(issue.id)}
                                                    onChange={() => {}} // Handled by div onClick
                                                    className="mt-1.5 accent-blue-500 rounded border-white/10"
                                                />
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center gap-2 mb-1.5">
                                                        <span className={`px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-widest ${
                                                            issue.severity === 'high' ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
                                                            issue.severity === 'medium' ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20' :
                                                            'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                                                        }`}>
                                                            {issue.severity === 'high' ? 'Jiddiy' : issue.severity === 'medium' ? 'O\'rta' : 'Yengil'}
                                                        </span>
                                                        <span className="text-xs font-bold text-slate-300">{issue.description}</span>
                                                    </div>
                                                    
                                                    {/* Side by side replacement */}
                                                    <div className="bg-slate-950/40 p-2.5 rounded-lg border border-white/5 text-xs font-mono mt-2 grid grid-cols-2 gap-4">
                                                        <div className="text-red-400/80 border-r border-white/5 pr-2 truncate">
                                                            <span className="block text-[9px] font-black text-slate-500 uppercase tracking-widest mb-0.5">Asl matn:</span>
                                                            <del className="no-underline line-through">{issue.target_text}</del>
                                                        </div>
                                                        <div className="text-emerald-400 pl-2 truncate">
                                                            <span className="block text-[9px] font-black text-slate-500 uppercase tracking-widest mb-0.5">Tuzatilgan:</span>
                                                            <span>{issue.suggested_text}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </>
                            )}
                        </div>
                    )}

                    {step === 'success' && (
                        <div className="flex flex-col items-center justify-center py-12 text-center">
                            <div className="w-16 h-16 bg-emerald-500/10 text-emerald-400 rounded-full flex items-center justify-center mb-6 border border-emerald-500/20">
                                <Check size={36} className="animate-bounce" />
                            </div>
                            <h4 className="text-2xl font-black text-white mb-2">Muvaffaqiyatli tuzatildi!</h4>
                            <p className="text-slate-400 max-w-sm mx-auto mb-8 font-medium">
                                AI tahrirchi barcha tanlangan tuzatishlarni Word hisobot hujjatiga to'g'ridan-to'g'ri kiritdi va yangi Word faylini saqladi.
                            </p>
                            <button
                                onClick={onClose}
                                className="px-8 py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-2xl transition-all"
                            >
                                Oynani Yopish
                            </button>
                        </div>
                    )}
                </div>

                {/* Footer Actions */}
                {step === 'results' && (
                    <div className="p-6 border-t border-white/5 flex gap-4 bg-slate-900/20">
                        <button
                            onClick={() => setStep('select')}
                            className="flex-1 py-3 bg-white/5 hover:bg-white/10 text-slate-300 font-bold rounded-2xl border border-white/5 transition-all uppercase tracking-wider text-xs"
                        >
                            Orqaga qaytish
                        </button>
                        <button
                            onClick={handleApplyFixes}
                            disabled={selectedIssueIds.length === 0 || isApplying}
                            className={`flex-[2] py-3 text-white font-bold rounded-2xl transition-all flex items-center justify-center gap-2 uppercase tracking-wider text-xs shadow-lg ${
                                selectedIssueIds.length === 0 || isApplying
                                    ? 'bg-slate-800 text-slate-500 border border-white/5 cursor-not-allowed'
                                    : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 shadow-emerald-500/10'
                            }`}
                        >
                            {isApplying ? (
                                <>
                                    <RefreshCw size={16} className="animate-spin" /> Tuzatilmoqda...
                                </>
                            ) : (
                                <>
                                    <CheckCircle size={16} /> {selectedIssueIds.length} ta tuzatishni qo'llash
                                </>
                            )}
                        </button>
                    </div>
                )}
            </motion.div>
        </div>
    );
}
