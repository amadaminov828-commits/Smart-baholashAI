"use client";

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Building2, Save, User, FileText, Camera, ShieldCheck, ArrowLeft, Settings2 } from 'lucide-react';
import Link from 'next/link';
import axios from 'axios';

// Set default auth headers from localStorage token
const getApi = () => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    return axios.create({
        baseURL: '/api-proxy/v1',
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    });
};

export default function SettingsPage() {
    const api = getApi();
    const [userForm, setUserForm] = useState({
        full_name: '',
        phone_number: '',
        license_number: '',
        pinfl: '',
        company: null as number | null
    });

    const [companyForm, setCompanyForm] = useState({
        name: '',
        stir: ''
    });

    const [logoFile, setLogoFile] = useState<File | null>(null);
    const [sealFile, setSealFile] = useState<File | null>(null);
    const [signatureFile, setSignatureFile] = useState<File | null>(null);
    const [hasCompany, setHasCompany] = useState(false);
    const [companyDetails, setCompanyDetails] = useState<any>(null);
    const [userDetails, setUserDetails] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const res = await api.get('/users/me/');
                setUserDetails(res.data);
                setUserForm({
                    full_name: res.data.full_name || '',
                    phone_number: res.data.phone_number || '',
                    license_number: res.data.license_number || '',
                    pinfl: res.data.pinfl || '',
                    company: res.data.company
                });
                
                if (res.data.company_details) {
                    setHasCompany(true);
                    setCompanyDetails(res.data.company_details);
                    setCompanyForm({
                        name: res.data.company_details.name || '',
                        stir: res.data.company_details.stir || ''
                    });
                }
            } catch (err) {
                console.error("Failed to load settings profile:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchProfile();
    }, []);

    const handleSaveProfile = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);
        setMessage(null);
        try {
            // Update User Profile with FormData to support file uploads (signature)
            const userFd = new FormData();
            userFd.append('full_name', userForm.full_name);
            userFd.append('phone_number', userForm.phone_number);
            userFd.append('license_number', userForm.license_number);
            userFd.append('pinfl', userForm.pinfl);
            if (signatureFile) {
                userFd.append('signature', signatureFile);
            }

            const userRes = await api.patch('/users/me/', userFd, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setUserDetails(userRes.data);

            // Create or Update Company Profile
            const fd = new FormData();
            fd.append('name', companyForm.name);
            fd.append('stir', companyForm.stir);
            if (logoFile) fd.append('logo', logoFile);
            if (sealFile) fd.append('seal', sealFile);

            if (hasCompany && userForm.company) {
                const compRes = await api.put(`/users/companies/${userForm.company}/`, fd, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });
                setCompanyDetails(compRes.data);
            } else {
                const compRes = await api.post('/users/companies/', fd, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });
                setHasCompany(true);
                setUserForm(prev => ({ ...prev, company: compRes.data.id }));
                setCompanyDetails(compRes.data);
            }

            setMessage({ text: "Sozlamalar muvaffaqiyatli saqlandi! ⚡", type: 'success' });
        } catch (err: any) {
            console.error(err);
            setMessage({ text: "Sozlamalarni saqlashda xatolik yuz berdi.", type: 'error' });
        } finally {
            setSubmitting(false);
            setTimeout(() => setMessage(null), 5000);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-[#0a0f1c] flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-blue-500/20 border-t-blue-600 rounded-full animate-spin"></div>
                    <p className="text-slate-400 font-bold text-sm animate-pulse">Sozlamalar yuklanmoqda...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#0a0f1c] text-slate-200 py-12 px-4 md:px-8 relative overflow-hidden font-sans">
            <div className="max-w-4xl mx-auto relative z-10">
                
                {/* Top Navigation */}
                <div className="flex justify-between items-center mb-10">
                    <Link href="/vehicles" className="inline-flex items-center gap-2 px-5 py-2.5 bg-slate-900 border border-white/5 rounded-xl text-slate-400 hover:text-white transition-all font-bold text-xs">
                        <ArrowLeft size={16} />
                        Bosh sahifaga qaytish
                    </Link>
                    <div className="flex items-center gap-2">
                        <Settings2 className="text-blue-500" size={22} />
                        <h1 className="text-2xl font-black text-white">SaaS Profil Sozlamalari</h1>
                    </div>
                </div>

                {message && (
                    <motion.div 
                        initial={{ opacity: 0, y: -10 }} 
                        animate={{ opacity: 1, y: 0 }}
                        className={`p-5 rounded-2xl border mb-8 font-bold text-sm text-left ${
                            message.type === 'success' ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-400' : 'bg-rose-950/20 border-rose-500/30 text-rose-400'
                        }`}
                    >
                        {message.text}
                    </motion.div>
                )}

                <form onSubmit={handleSaveProfile} className="space-y-8">
                    {/* Part 1: Appraiser Profile */}
                    <div className="bg-slate-900/40 p-8 rounded-[35px] border border-white/5 space-y-6">
                        <h2 className="text-lg font-black text-white flex items-center gap-2 border-b border-white/5 pb-4">
                            <User className="text-blue-500" size={20} />
                            Baholovchi mutaxassis profili (Shaxsiy)
                        </h2>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="text-[10px] font-black text-slate-500 uppercase ml-2 mb-1 block">To'liq ism-sharif (F.I.Sh)</label>
                                <input 
                                    type="text" 
                                    required
                                    value={userForm.full_name}
                                    onChange={(e) => setUserForm({ ...userForm, full_name: e.target.value })}
                                    className="w-full px-5 py-3.5 bg-slate-950 border border-slate-800 rounded-2xl focus:border-blue-500 outline-none font-bold"
                                    placeholder="Masalan: B.M.Mirzabekov"
                                />
                            </div>
                            
                            <div>
                                <label className="text-[10px] font-black text-slate-500 uppercase ml-2 mb-1 block">Telefon raqam</label>
                                <input 
                                    type="text" 
                                    value={userForm.phone_number}
                                    onChange={(e) => setUserForm({ ...userForm, phone_number: e.target.value })}
                                    className="w-full px-5 py-3.5 bg-slate-950 border border-slate-800 rounded-2xl focus:border-blue-500 outline-none font-bold"
                                    placeholder="+998901234567"
                                />
                            </div>

                            <div>
                                <label className="text-[10px] font-black text-slate-500 uppercase ml-2 mb-1 block">Baholovchi litsenziya/sertifikat raqami</label>
                                <input 
                                    type="text" 
                                    value={userForm.license_number}
                                    onChange={(e) => setUserForm({ ...userForm, license_number: e.target.value })}
                                    className="w-full px-5 py-3.5 bg-slate-950 border border-slate-800 rounded-2xl focus:border-blue-500 outline-none font-bold"
                                    placeholder="Masalan: №0244"
                                />
                            </div>

                            <div>
                                <label className="text-[10px] font-black text-slate-500 uppercase ml-2 mb-1 block">PINFL (14 ta raqamli kod)</label>
                                <input 
                                    type="text" 
                                    maxLength={14}
                                    value={userForm.pinfl}
                                    onChange={(e) => setUserForm({ ...userForm, pinfl: e.target.value })}
                                    className="w-full px-5 py-3.5 bg-slate-950 border border-slate-800 rounded-2xl focus:border-blue-500 outline-none font-bold"
                                    placeholder="31204901234567"
                                />
                            </div>
                        </div>

                        {/* Signature upload block */}
                        <div className="pt-6 border-t border-white/5 flex flex-col items-center justify-center">
                            <div className="p-6 bg-slate-950 rounded-2xl border border-white/5 flex flex-col items-center justify-center text-center w-full max-w-md">
                                <Camera size={24} className="text-slate-500 mb-3" />
                                <h4 className="text-sm font-bold mb-1">Baholovchi shaxsiy imzosi rasmi (Imzo)</h4>
                                <p className="text-[10px] text-slate-500 mb-4">PNG formatda (Fonisiz/Transparent bo'lishi tavsiya etiladi)</p>
                                {userDetails?.signature && (
                                    <img src={userDetails.signature} alt="Baholovchi imzosi" className="h-12 object-contain mb-4 rounded-xl border border-white/10 p-1 bg-white" />
                                )}
                                <input 
                                    type="file" 
                                    accept="image/*"
                                    onChange={(e) => setSignatureFile(e.target.files?.[0] || null)}
                                    className="text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-black file:bg-blue-600/10 file:text-blue-400 hover:file:bg-blue-600/20"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Part 2: Company settings */}
                    <div className="bg-slate-900/40 p-8 rounded-[35px] border border-white/5 space-y-6">
                        <h2 className="text-lg font-black text-white flex items-center gap-2 border-b border-white/5 pb-4">
                            <Building2 className="text-blue-500" size={20} />
                            Baholash tashkiloti profili (Yuridik shaxs)
                        </h2>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="text-[10px] font-black text-slate-500 uppercase ml-2 mb-1 block">Tashkilot/MCHJ to'liq nomi</label>
                                <input 
                                    type="text" 
                                    required
                                    value={companyForm.name}
                                    onChange={(e) => setCompanyForm({ ...companyForm, name: e.target.value })}
                                    className="w-full px-5 py-3.5 bg-slate-950 border border-slate-800 rounded-2xl focus:border-blue-500 outline-none font-bold"
                                    placeholder="Masalan: 'PERCEPTION VALUE' MCHJ"
                                />
                            </div>

                            <div>
                                <label className="text-[10px] font-black text-slate-500 uppercase ml-2 mb-1 block">Tashkilot STIR raqami (INN)</label>
                                <input 
                                    type="text" 
                                    required
                                    value={companyForm.stir}
                                    onChange={(e) => setCompanyForm({ ...companyForm, stir: e.target.value })}
                                    className="w-full px-5 py-3.5 bg-slate-950 border border-slate-800 rounded-2xl focus:border-blue-500 outline-none font-bold"
                                    placeholder="301234567"
                                />
                            </div>
                        </div>

                        {/* File Uploads (Logo & Stamp) */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
                            {/* Logo upload */}
                            <div className="p-6 bg-slate-950 rounded-2xl border border-white/5 flex flex-col items-center justify-center text-center">
                                <Camera size={24} className="text-slate-500 mb-3" />
                                <h4 className="text-sm font-bold mb-1">Tashkilot Logotipi</h4>
                                <p className="text-[10px] text-slate-500 mb-4">PNG, JPG formatlari (Mavjud bo'lsa)</p>
                                {companyDetails?.logo && (
                                    <img src={companyDetails.logo} alt="Company Logo" className="w-16 h-16 object-contain mb-4 rounded-xl border border-white/10 p-1 bg-white" />
                                )}
                                <input 
                                    type="file" 
                                    accept="image/*"
                                    onChange={(e) => setLogoFile(e.target.files?.[0] || null)}
                                    className="text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-black file:bg-blue-600/10 file:text-blue-400 hover:file:bg-blue-600/20"
                                />
                            </div>

                            {/* Seal/Stamp upload */}
                            <div className="p-6 bg-slate-950 rounded-2xl border border-white/5 flex flex-col items-center justify-center text-center">
                                <ShieldCheck size={24} className="text-slate-500 mb-3" />
                                <h4 className="text-sm font-bold mb-1">Dumaloq muhr (Pechat) rasmi</h4>
                                <p className="text-[10px] text-slate-500 mb-4">PNG formatda (Fonisiz/Transparent bo'lishi tavsiya etiladi)</p>
                                {companyDetails?.seal && (
                                    <img src={companyDetails.seal} alt="Company Seal" className="w-16 h-16 object-contain mb-4 rounded-xl border border-white/10 p-1 bg-white" />
                                )}
                                <input 
                                    type="file" 
                                    accept="image/*"
                                    onChange={(e) => setSealFile(e.target.files?.[0] || null)}
                                    className="text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-black file:bg-blue-600/10 file:text-blue-400 hover:file:bg-blue-600/20"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Submit Button */}
                    <button 
                        type="submit" 
                        disabled={submitting}
                        className="w-full py-5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-2xl font-black text-xl flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20 disabled:opacity-50 transition-all cursor-pointer"
                    >
                        <Save size={22} />
                        {submitting ? "SAQLANMOQDA..." : "SOZLAMALARNI SAQLASH"}
                    </button>
                </form>
            </div>
        </div>
    );
}
