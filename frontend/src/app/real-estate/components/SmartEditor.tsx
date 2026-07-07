"use client";

import { useState, useEffect } from 'react';
import { api } from '@/services/api';
import { motion, AnimatePresence } from 'framer-motion';
import {
    FileText, Check, AlertCircle, TrendingUp, Map as MapIcon, DollarSign,
    BarChart3, History, Save, Send, UserCheck, Lock, User, CreditCard,
    Home, Info, Calculator, Zap, ArrowRight, Layout, Fingerprint, Calendar, Building
} from 'lucide-react';
import CalculationEditor from './CalculationEditor';

interface SmartEditorProps {
    valuationId: number;
    initialData: any;
    userRole: 'assistant' | 'appraiser' | 'user' | 'admin' | 'super_admin';
    onComplete: () => void;
}

export default function SmartEditor({ valuationId, initialData, userRole, onComplete }: SmartEditorProps) {
    const [data, setData] = useState(initialData);
    const [confirmedFields, setConfirmedFields] = useState<Record<string, boolean>>(initialData.confirmed_fields || {});
    const [saving, setSaving] = useState(false);

    const handleConfirmField = async (fieldName: string) => {
        if (confirmedFields[fieldName]) return;
        try {
            await api.post(`/real-estate/valuations/${valuationId}/confirm-field/`, { field_name: fieldName });
            setConfirmedFields(prev => ({ ...prev, [fieldName]: true }));
        } catch (e) {
            console.error("Field confirmation error", e);
        }
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            await api.patch(`/real-estate/valuations/${valuationId}/`, data);
            alert("Ma'lumotlar saqlandi");
        } catch (e) {
            alert("Saqlashda xatolik");
        } finally {
            setSaving(false);
        }
    };

    const handleContinue = async () => {
        setSaving(true);
        try {
            await api.patch(`/real-estate/valuations/${valuationId}/`, data);
            onComplete();
        } catch (e) {
            alert("Xatolik yuz berdi");
            setSaving(false);
        }
    };

    const isFieldConfirmed = (name: string) => confirmedFields[name] === true;

    return (
        <div className="max-w-6xl mx-auto flex flex-col gap-10 pb-20 mt-10">
            {/* Header: Status & Info */}
            <div className="bg-slate-900/40 backdrop-blur-3xl rounded-[40px] border border-white/5 p-8 flex flex-col md:flex-row items-center justify-between shadow-2xl gap-6">
                <div className="flex items-center gap-6">
                    <div className="w-16 h-16 bg-blue-500/10 rounded-2xl flex items-center justify-center text-blue-400 border border-blue-500/20">
                        <Home size={32} />
                    </div>
                    <div>
                        <h2 className="text-3xl font-black text-white uppercase tracking-tighter italic">Ko'chmas Mulk Tahlili</h2>
                        <div className="flex items-center gap-3 mt-1">
                            <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest px-3 py-1 bg-white/5 rounded-full border border-white/5 font-sans">Smart Editor v2.0</span>
                            <div className="flex items-center gap-2 px-3 py-1 bg-emerald-500/10 rounded-full border border-emerald-500/10">
                                <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse"></div>
                                <span className="text-[9px] font-black text-emerald-400 uppercase tracking-widest font-sans">AI Vision Optimized</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <button onClick={handleSave} disabled={saving} className="px-6 py-4 bg-white/5 hover:bg-white/10 text-slate-300 rounded-2xl text-xs font-black uppercase tracking-widest border border-white/5 transition-all">
                        {saving ? '...' : 'Saqlash'}
                    </button>
                    <button onClick={handleContinue} disabled={saving} className="px-8 py-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-2xl text-xs font-black uppercase tracking-widest shadow-xl flex items-center gap-3 transition-all active:scale-95">
                        Davom etish <ArrowRight size={16} />
                    </button>
                </div>
            </div>

            {/* Two Column Layout for Identity and Property */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Column 1: Identity & Personal */}
                <div className="bg-slate-900/40 backdrop-blur-3xl rounded-[40px] border border-white/5 p-10 space-y-8 shadow-xl">
                    <div className="flex items-center gap-4 mb-2">
                        <div className="p-3 bg-blue-500/10 rounded-2xl text-blue-400">
                            <Fingerprint size={24} />
                        </div>
                        <h3 className="text-xl font-black text-white uppercase tracking-tighter">Mulkdor va Shaxs</h3>
                    </div>

                    <div className="space-y-6 pt-4 border-t border-white/5">
                        <InputField label="F.I.Sh. (Mulkdor)" value={data.owner_name} onChange={(v: string) => setData({ ...data, owner_name: v })} icon={<User size={14} />} confirmed={isFieldConfirmed('owner_name')} onFocus={() => handleConfirmField('owner_name')} />
                        <div className="grid grid-cols-2 gap-6">
                            <InputField label="Pasport Seriya" value={data.passport_serial} onChange={(v: string) => setData({ ...data, passport_serial: v })} icon={<Lock size={14} />} placeholder="AA1234567" confirmed={isFieldConfirmed('passport_serial')} onFocus={() => handleConfirmField('passport_serial')} />
                            <InputField label="JShShIR" value={data.passport_jshshir} onChange={(v: string) => setData({ ...data, passport_jshshir: v })} icon={<UserCheck size={14} />} placeholder="14 raqam" confirmed={isFieldConfirmed('passport_jshshir')} onFocus={() => handleConfirmField('passport_jshshir')} />
                        </div>
                        <InputField label="Pasport Berilgan Joyi" value={data.passport_given_by} onChange={(v: string) => setData({ ...data, passport_given_by: v })} icon={<MapIcon size={14} />} confirmed={isFieldConfirmed('passport_given_by')} onFocus={() => handleConfirmField('passport_given_by')} />
                    </div>
                </div>

                {/* Column 2: Property Technical Data */}
                <div className="bg-slate-900/40 backdrop-blur-3xl rounded-[40px] border border-white/5 p-10 space-y-8 shadow-xl">
                    <div className="flex items-center gap-4 mb-2">
                        <div className="p-3 bg-purple-500/10 rounded-2xl text-purple-400">
                            <Building size={24} />
                        </div>
                        <h3 className="text-xl font-black text-white uppercase tracking-tighter">Mulk Tafsilotlari</h3>
                    </div>

                    <div className="space-y-6 pt-4 border-t border-white/5">
                        <InputField label="Kadastr Raqami" value={data.cadastre_number} onChange={(v: string) => setData({ ...data, cadastre_number: v })} icon={<CreditCard size={14} />} confirmed={isFieldConfirmed('cadastre_number')} onFocus={() => handleConfirmField('cadastre_number')} />
                        <div className="grid grid-cols-2 gap-6">
                            <InputField label="Umumiy Maydon" value={data.total_area} onChange={(v: string) => setData({ ...data, total_area: v })} icon={<Layout size={14} />} suffix="m²" confirmed={isFieldConfirmed('total_area')} onFocus={() => handleConfirmField('total_area')} />
                            <InputField label="Qurilgan Yili" value={data.built_year} onChange={(v: string) => setData({ ...data, built_year: v })} icon={<Calendar size={14} />} confirmed={isFieldConfirmed('built_year')} onFocus={() => handleConfirmField('built_year')} />
                        </div>
                        <InputField label="Mulk Manzili" value={data.location} onChange={(v: string) => setData({ ...data, location: v })} icon={<MapIcon size={14} />} confirmed={isFieldConfirmed('location')} onFocus={() => handleConfirmField('location')} />
                    </div>
                </div>
            </div>

            {/* Calculations Module */}
            <div className="bg-slate-900/40 backdrop-blur-3xl rounded-[40px] border border-white/5 p-10 shadow-xl">
                <div className="flex items-center gap-4 mb-8">
                    <div className="p-3 bg-indigo-500/10 rounded-2xl text-indigo-400">
                        <Calculator size={24} />
                    </div>
                    <h3 className="text-2xl font-black text-white uppercase tracking-tighter italic text-indigo-400">Qiymatni Baholash</h3>
                </div>

                <CalculationEditor
                    valuationId={valuationId}
                    initialData={data}
                    onSave={(calcResults) => {
                        setData({ ...data, ...calcResults });
                    }}
                />
            </div>

            <div className="flex justify-center pt-10">
                <button onClick={handleContinue} disabled={saving} className="px-20 py-8 bg-emerald-600 hover:bg-emerald-500 text-white rounded-[35px] font-black text-2xl uppercase tracking-widest shadow-[0_20px_50px_rgba(16,185,129,0.3)] flex items-center gap-6 transition-all hover:scale-[1.02] active:scale-95">
                    KEYINGI BOSQICHGA <ArrowRight size={32} />
                </button>
            </div>
        </div>
    );
}

function InputField({ label, value, onChange, icon, suffix, placeholder, confirmed, onFocus }: any) {
    return (
        <div className="group">
            <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-3 block ml-1 font-sans">{label}</label>
            <div className="relative">
                <div className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-600 group-focus-within:text-emerald-400 transition-colors">
                    {icon}
                </div>
                <input
                    type="text"
                    value={value || ''}
                    placeholder={placeholder}
                    onChange={(e) => onChange(e.target.value)}
                    onFocus={onFocus}
                    className={`w-full bg-slate-950/50 border border-white/5 p-5 pl-14 rounded-2xl text-white font-bold outline-none transition-all placeholder:text-slate-700 ${!confirmed ? 'border-emerald-500/30 bg-emerald-500/5 shadow-[0_0_20px_rgba(16,185,129,0.05)]' : 'focus:border-blue-500/40 focus:bg-slate-950'}`}
                />
                {suffix && <span className="absolute right-5 top-1/2 -translate-y-1/2 text-[10px] font-black text-slate-600 uppercase tracking-widest font-sans">{suffix}</span>}
                {!confirmed && (
                    <div className="absolute -top-2 right-4 flex items-center gap-1.5 px-2 py-0.5 bg-emerald-500 rounded-full shadow-lg">
                        <Zap size={8} className="text-black fill-black" />
                        <span className="text-[7px] font-black text-black font-sans">AI FILLED</span>
                    </div>
                )}
            </div>
        </div>
    );
}
