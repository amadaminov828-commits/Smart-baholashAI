"use client";

import { useState, useEffect } from 'react';
import { api } from '@/services/api';
import { motion, AnimatePresence } from 'framer-motion';
import { Calculator, TrendingUp, Landmark, Zap, Save, RefreshCw, ChevronDown, ChevronUp } from 'lucide-react';

interface CalculationEditorProps {
    valuationId: number;
    initialData: any;
    onSave: (data: any) => void;
}

export default function CalculationEditor({ valuationId, initialData, onSave }: CalculationEditorProps) {
    const [method, setMethod] = useState<'qiyosiy' | 'xarajat' | 'daromad'>(initialData?.method || 'qiyosiy');
    const defaultCalcData = {
        cost: { base_cost: 4500000, indexation: 1.15, normative_life: 100, profit_rate: 0.15, land_value: 80000000 },
        income: { unit_rent: 60000, vacancy_rate: 0.07, opex_rate: 0.15, cap_rate: 0.12 },
        comparative: { base_price_m2: 8500000, location_adj: 1.0, repair_adj: 1.0, floor_adj: 1.0 }
    };
    const raw = initialData?.calculation_data;
    const [calcData, setCalcData] = useState<any>({
        cost: { ...defaultCalcData.cost, ...(raw?.cost || {}) },
        income: { ...defaultCalcData.income, ...(raw?.income || {}) },
        comparative: { ...defaultCalcData.comparative, ...(raw?.comparative || {}) }
    });
    const [aiResults, setAiResults] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [expandedStage, setExpandedStage] = useState<string | null>(null);

    const fetchAiCalculation = async () => {
        setLoading(true);
        try {
            // Send current parameters to backend for "ipidan-ignasigacha" calculation
            const response = await api.post(`/real-estate/valuations/${valuationId}/ai-calculate-approaches/`, {
                ...calcData.cost, ...calcData.income, ...calcData.comparative
            });
            setAiResults(response.data);
            // Sync current method's final value if needed
        } catch (error) {
            console.error("AI Calculation failed", error);
        }
        setLoading(false);
    };

    const handleSave = () => {
        onSave({ method, calculation_data: calcData, ai_results: aiResults });
    };

    const StatusCard = ({ title, value, steps, icon: Icon, color }: any) => (
        <div className={`p-6 rounded-[32px] border bg-slate-900/40 backdrop-blur-xl transition-all duration-500 hover:scale-[1.02] ${color === 'blue' ? 'border-blue-500/30 shadow-blue-500/10' : color === 'emerald' ? 'border-emerald-500/30' : 'border-purple-500/30'}`}>
            <div className="flex justify-between items-start mb-4">
                <div className={`p-3 rounded-2xl ${color === 'blue' ? 'bg-blue-600/20 text-blue-400' : color === 'emerald' ? 'bg-emerald-600/20 text-emerald-400' : 'bg-purple-600/20 text-purple-400'}`}>
                    <Icon size={24} />
                </div>
                <div className="text-right">
                    <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">{title}</p>
                    <h4 className="text-2xl font-black text-white tracking-tighter mt-1">{value?.toLocaleString()} so'm</h4>
                </div>
            </div>
            <div className="space-y-2 pt-4 border-t border-white/5">
                {steps?.map((step: string, i: number) => (
                    <div key={i} className="flex items-center gap-2 text-[11px] font-medium text-slate-400">
                        <div className={`w-1 h-1 rounded-full ${color === 'blue' ? 'bg-blue-500' : color === 'emerald' ? 'bg-emerald-500' : 'bg-purple-500'}`} />
                        {step}
                    </div>
                ))}
            </div>
        </div>
    );

    return (
        <div className="space-y-12">
            {/* Approach Selector */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                    { id: 'qiyosiy', label: 'Qiyosiy', desc: 'Bozor narxi', icon: Calculator, color: 'blue' },
                    { id: 'xarajat', label: 'Xarajat', desc: 'Tiklanish xarajatlari', icon: Landmark, color: 'purple' },
                    { id: 'daromad', label: 'Daromad', desc: 'Investitsion joziba', icon: TrendingUp, color: 'emerald' }
                ].map((m) => (
                    <motion.button
                        key={m.id}
                        whileHover={{ y: -4 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setMethod(m.id as any)}
                        className={`p-8 rounded-[40px] border-2 text-left transition-all duration-500 relative overflow-hidden group ${method === m.id
                            ? (m.color === 'blue' ? 'bg-blue-600/10 border-blue-500/50 shadow-blue-500/10' : m.color === 'purple' ? 'bg-purple-600/10 border-purple-500/50' : 'bg-emerald-600/10 border-emerald-500/50')
                            : 'bg-slate-900/40 border-slate-800'}`}
                    >
                        {method === m.id && (
                            <motion.div layoutId="activeDot" className="absolute top-6 right-6 w-3 h-3 rounded-full bg-current shadow-[0_0_15px_rgba(255,255,255,0.5)]" />
                        )}
                        <m.icon className={`mb-4 ${method === m.id ? 'text-white' : 'text-slate-500'}`} size={32} />
                        <h3 className="text-xl font-black text-white uppercase tracking-tight">{m.label}</h3>
                        <p className="text-slate-500 text-xs font-bold mt-1 uppercase tracking-widest">{m.desc}</p>
                    </motion.button>
                ))}
            </div>

            {/* AI Results Banner */}
            {aiResults && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
                    <StatusCard title="Qiyosiy Qiymat" value={aiResults.comparative.final_value} steps={aiResults.comparative.steps} icon={Calculator} color="blue" />
                    <StatusCard title="Xarajat Qiymati" value={aiResults.cost.final_value} steps={aiResults.cost.steps} icon={Landmark} color="purple" />
                    <StatusCard title="Daromad Qiymati" value={aiResults.income.final_value} steps={aiResults.income.steps} icon={TrendingUp} color="emerald" />
                </div>
            )}

            {/* Interactive Form Panel */}
            <div className="bg-slate-900/40 backdrop-blur-3xl rounded-[48px] border border-white/5 p-10 shadow-2xl overflow-hidden relative">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-blue-500/30 to-transparent" />

                <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-10 gap-6">
                    <div>
                        <h2 className="text-2xl font-black text-white uppercase tracking-tight flex items-center gap-3">
                            <Zap size={24} className="text-yellow-400" />
                            {method === 'qiyosiy' ? 'Qiyosiy Tuzatishlar Matritsasi' : method === 'xarajat' ? 'Tiklanish va Eskirish Hisobi' : 'NOI va Kapitallashtirish Zanjiri'}
                        </h2>
                        <p className="text-slate-500 text-sm mt-1 font-medium">Barcha parametrlarni "ipidan-ignasigacha" tahrirlashingiz mumkin</p>
                    </div>
                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={fetchAiCalculation}
                        disabled={loading}
                        className="flex items-center gap-3 px-6 py-3 bg-blue-600 rounded-2xl text-white font-black text-xs uppercase tracking-widest shadow-lg shadow-blue-500/20 disabled:opacity-50"
                    >
                        <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                        {loading ? 'Hisoblanmoqda...' : 'AI Bilan Hisobla'}
                    </motion.button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {method === 'xarajat' && (
                        <>
                            {[
                                { k: 'base_cost', l: 'ShNQ Narxi (m2/m3)', p: '4 500 000' },
                                { k: 'indexation', l: 'Indeksatsiya koeff.', p: '1.15' },
                                { k: 'normative_life', l: 'Normativ yosh (yil)', p: '100' },
                                { k: 'profit_rate', l: 'Tadbirkorlik foydasi %', p: '0.15' },
                                { k: 'land_value', l: 'Yer qiymati', p: '80 000 000' }
                            ].map(f => (
                                <div key={f.k} className="space-y-2">
                                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">{f.l}</label>
                                    <input
                                        type="text"
                                        value={calcData.cost[f.k]}
                                        onChange={(e) => setCalcData({ ...calcData, cost: { ...calcData.cost, [f.k]: e.target.value } })}
                                        className="w-full px-5 py-4 bg-slate-950/50 border border-white/5 rounded-2xl text-white font-bold outline-none focus:border-purple-500/50 transition-all"
                                        placeholder={f.p}
                                    />
                                </div>
                            ))}
                        </>
                    )}

                    {method === 'daromad' && (
                        <>
                            {[
                                { k: 'unit_rent', l: 'Ijara stavkasi (m2)', p: '60 000' },
                                { k: 'vacancy_rate', l: 'Bo\'sh qolish xavfi %', p: '0.07' },
                                { k: 'opex_rate', l: 'Operatsion xarajat %', p: '0.15' },
                                { k: 'cap_rate', l: 'Kapitalizatsiya %', p: '0.12' }
                            ].map(f => (
                                <div key={f.k} className="space-y-2">
                                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">{f.l}</label>
                                    <input
                                        type="text"
                                        value={calcData.income[f.k]}
                                        onChange={(e) => setCalcData({ ...calcData, income: { ...calcData.income, [f.k]: e.target.value } })}
                                        className="w-full px-5 py-4 bg-slate-950/50 border border-white/5 rounded-2xl text-white font-bold outline-none focus:border-emerald-500/50 transition-all"
                                        placeholder={f.p}
                                    />
                                </div>
                            ))}
                        </>
                    )}

                    {method === 'qiyosiy' && (
                        <>
                            {[
                                { k: 'base_price_m2', l: 'Baza m2 narxi', p: '8 500 000' },
                                { k: 'location_adj', l: 'Joylashuv (koeff)', p: '1.0' },
                                { k: 'repair_adj', l: 'Holat (koeff)', p: '1.0' },
                                { k: 'floor_adj', l: 'Qavat (koeff)', p: '1.0' }
                            ].map(f => (
                                <div key={f.k} className="space-y-2">
                                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">{f.l}</label>
                                    <input
                                        type="text"
                                        value={calcData.comparative[f.k]}
                                        onChange={(e) => setCalcData({ ...calcData, comparative: { ...calcData.comparative, [f.k]: e.target.value } })}
                                        className="w-full px-5 py-4 bg-slate-950/50 border border-white/5 rounded-2xl text-white font-bold outline-none focus:border-blue-500/50 transition-all"
                                        placeholder={f.p}
                                    />
                                </div>
                            ))}
                        </>
                    )}
                </div>

                {/* Final Submission Button */}
                <div className="mt-12 pt-8 border-t border-white/5 flex justify-end">
                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={handleSave}
                        className="flex items-center gap-3 px-10 py-5 bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-[24px] font-black text-lg uppercase tracking-tight shadow-xl shadow-blue-500/20"
                    >
                        <Save size={24} />
                        MA'LUMOTLARNI SAQLASH
                    </motion.button>
                </div>
            </div>
        </div>
    );
}
