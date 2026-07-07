"use client";

import { useState, useEffect } from 'react';
import { api } from '@/services/api';
import { motion, AnimatePresence } from 'framer-motion';
import { FileDown, Upload, Trash2, FileText, ArrowLeft, Plus, FileUp } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function TemplatesModule() {
    const router = useRouter();
    const [templates, setTemplates] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [name, setName] = useState('');
    const [objectType, setObjectType] = useState('vehicle');
    const [file, setFile] = useState<File | null>(null);

    const fetchTemplates = async () => {
        try {
            const res = await api.get('/templates/');
            setTemplates(res.data);
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        fetchTemplates();
    }, []);

    const handleUpload = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!file) return alert("Fayl tanlang!");
        setLoading(true);
        try {
            const fd = new FormData();
            fd.append('name', name);
            fd.append('object_type', objectType);
            fd.append('file', file);

            await api.post('/templates/', fd);
            alert("Andoza muvaffaqiyatli saqlandi!");
            setName('');
            setFile(null);
            fetchTemplates();
        } catch (err) {
            alert("Xatolik yuz berdi");
        }
        setLoading(false);
    };

    const handleDelete = async (id: number) => {
        if (!confirm("O'chirmoqchimisiz?")) return;
        try {
            await api.delete(`/templates/${id}/`);
            fetchTemplates();
        } catch (e) {
            alert("Xatolik");
        }
    }

    return (
        <div className="min-h-screen bg-[#0a0f1c] text-slate-200 py-12 px-6 relative overflow-hidden font-sans">
            {/* Background Neural Decorations */}
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/10 blur-[120px] rounded-full shadow-[0_0_100px_rgba(37,99,235,0.1)] pointer-events-none"></div>
            <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-600/10 blur-[120px] rounded-full pointer-events-none"></div>

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
                                Andozalar
                            </h1>
                            <p className="text-slate-400 mt-2 font-medium flex items-center gap-2">
                                <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
                                Microsoft Word (.docx) andozalar arxivi
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={() => router.push('/')}
                        className="flex items-center gap-2 px-6 py-3 bg-white/5 hover:bg-white/10 rounded-2xl border border-white/5 text-sm font-bold text-slate-400 transition-all"
                    >
                        <ArrowLeft size={16} /> Bosh sahifa
                    </button>
                </motion.div>

                <div className="grid lg:grid-cols-3 gap-10">
                    {/* Left: Upload Form */}
                    <motion.div
                        initial={{ opacity: 0, x: -30 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="lg:col-span-1 bg-slate-900/40 backdrop-blur-xl p-8 rounded-[40px] border border-white/5 shadow-2xl h-fit sticky top-12"
                    >
                        <h3 className="text-xl font-black text-white mb-8 flex items-center gap-3 uppercase tracking-tighter">
                            <div className="p-2 bg-blue-500/10 rounded-xl text-blue-400 border border-blue-500/10">
                                <Plus size={20} />
                            </div>
                            Yangi Andoza
                        </h3>
                        <form onSubmit={handleUpload} className="space-y-6">
                            <div>
                                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 block ml-2">Andoza nomi</label>
                                <input
                                    type="text"
                                    required
                                    value={name}
                                    onChange={e => setName(e.target.value)}
                                    className="w-full p-4 bg-slate-950 border border-slate-800 rounded-2xl text-white font-bold outline-none focus:ring-2 focus:ring-blue-500/50 transition-all shadow-inner"
                                    placeholder="Masalan: Garov uchun..."
                                />
                            </div>
                            <div>
                                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 block ml-2">Obyekt Turi</label>
                                <select
                                    value={objectType}
                                    onChange={e => setObjectType(e.target.value)}
                                    className="w-full p-4 bg-slate-950 border border-slate-800 rounded-2xl text-white font-bold outline-none focus:ring-2 focus:ring-blue-500/50 appearance-none cursor-pointer"
                                >
                                    <option value="vehicle">Mashina ($vehicle)</option>
                                    <option value="real_estate">Ko'chmas mulk ($re)</option>
                                </select>
                            </div>
                            <div className="relative group">
                                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 block ml-2">Docx Fayl</label>
                                <div className="border border-dashed border-slate-800 rounded-2xl p-6 bg-slate-950 text-center hover:border-blue-500/50 transition-all relative">
                                    <FileUp size={24} className="mx-auto text-slate-600 mb-2 group-hover:text-blue-400 transition-colors" />
                                    <span className="text-xs font-bold text-slate-500 truncate block px-2">
                                        {file ? file.name : "Faylni tanlang"}
                                    </span>
                                    <input
                                        type="file"
                                        required
                                        accept=".docx"
                                        onChange={e => setFile(e.target.files?.[0] || null)}
                                        className="absolute inset-0 opacity-0 cursor-pointer"
                                    />
                                </div>
                            </div>
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full py-4 bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-2xl shadow-xl font-black text-sm uppercase tracking-widest transition-all hover:-translate-y-1 active:scale-95 disabled:opacity-30"
                            >
                                {loading ? 'SAQLANMOQDA...' : 'SAQLASH'}
                            </button>
                        </form>
                    </motion.div>

                    {/* Right: Templates List */}
                    <motion.div
                        initial={{ opacity: 0, x: 30 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="lg:col-span-2 space-y-4"
                    >
                        <AnimatePresence>
                            {templates.map((t, idx) => (
                                <motion.div
                                    key={t.id}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, scale: 0.95 }}
                                    transition={{ delay: idx * 0.05 }}
                                    className="bg-slate-900/40 backdrop-blur-md p-6 rounded-[35px] border border-white/5 flex justify-between items-center group hover:bg-slate-900/60 hover:border-blue-500/30 transition-all duration-500 shadow-xl"
                                >
                                    <div className="flex items-center gap-6">
                                        <div className="w-14 h-14 bg-blue-600/10 rounded-2xl flex items-center justify-center text-blue-400 border border-blue-500/10 group-hover:bg-blue-600 group-hover:text-white transition-all duration-500 shadow-lg">
                                            <FileText size={28} />
                                        </div>
                                        <div>
                                            <h4 className="font-black text-xl text-white tracking-tight uppercase group-hover:text-blue-200 transition-colors">{t.name}</h4>
                                            <div className="flex items-center gap-3 mt-1">
                                                <span className="text-[10px] font-black text-blue-500/80 uppercase tracking-widest">{t.object_type}</span>
                                                <span className="w-1 h-1 bg-slate-700 rounded-full"></span>
                                                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{new Date(t.created_at).toLocaleDateString()}</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex gap-3">
                                        <a href={t.file} target="_blank" rel="noreferrer" className="w-10 h-10 flex items-center justify-center text-blue-400 bg-blue-500/5 hover:bg-blue-500 hover:text-white border border-blue-500/10 rounded-xl transition-all">
                                            <FileDown size={18} />
                                        </a>
                                        <button onClick={() => handleDelete(t.id)} className="w-10 h-10 flex items-center justify-center text-red-400 bg-red-500/5 hover:bg-red-500 hover:text-white border border-red-500/10 rounded-xl transition-all">
                                            <Trash2 size={18} />
                                        </button>
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                        {templates.length === 0 && (
                            <div className="text-center py-20 bg-slate-900/40 rounded-[40px] border border-dashed border-slate-800">
                                <p className="text-slate-500 font-bold uppercase tracking-widest text-sm italic">Andozalar arxivi bo'sh</p>
                            </div>
                        )}
                    </motion.div>
                </div>
            </div>
        </div>
    );
}
