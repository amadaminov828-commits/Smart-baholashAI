"use client";

import { motion } from 'framer-motion';
import { Phone, Mail, Send, MapPin, ArrowLeft, Globe } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function ContactPage() {
    const router = useRouter();

    const contactInfo = [
        {
            icon: <Phone size={24} />,
            label: "Telefon",
            value: "+998 (91) 699-61-79",
            desc: "Texnik qo'llab-quvvatlash uchun",
            color: "blue"
        },
        {
            icon: <Send size={24} />,
            label: "Telegram",
            value: "@SmartBaholash_AI",
            desc: "Tezkor muloqot va yangiliklar",
            color: "cyan"
        },
        {
            icon: <Mail size={24} />,
            label: "Email",
            value: "smartbaholashai@gmail.com",
            desc: "Hamkorlik va rasmiy so'rovlar",
            color: "indigo"
        },
        {
            icon: <MapPin size={24} />,
            label: "Manzil",
            value: "Farg'ona viloyati, Qo'qon shahar, Furqat ko'chasi, 100-uy.",
            desc: "Bosh ofis va tahlil markazi",
            color: "emerald"
        }
    ];

    return (
        <div className="min-h-screen bg-[#0a0f1c] text-slate-200 relative overflow-hidden font-sans">
            {/* Background Decor */}
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/10 blur-[120px] rounded-full pointer-events-none"></div>
            <div className="absolute top-[30%] right-[-10%] w-[30%] h-[30%] bg-emerald-500/5 blur-[120px] rounded-full pointer-events-none"></div>

            {/* Header */}
            <header className="relative z-50 px-6 py-4 flex justify-between items-center bg-slate-900/40 backdrop-blur-xl border-b border-white/5">
                <div className="flex items-center gap-6 cursor-pointer group" onClick={() => router.push('/')}>
                    <div className="relative cursor-pointer group" onClick={() => router.push('/')}>
                        <div className="w-24 h-24 rounded-full overflow-hidden border-[5px] border-slate-900 shadow-[0_0_15px_rgba(59,130,246,0.3)] bg-[#0a0f1c]">
                            <img
                                src="/logo.png?v=Neural"
                                alt="Smart Baholash"
                                className="w-full h-full object-cover scale-[1.45] group-hover:scale-[1.5] transition-transform duration-500"
                            />
                        </div>
                    </div>
                    <h1 className="text-xl font-black bg-gradient-to-r from-white to-blue-400 bg-clip-text text-transparent tracking-tighter">
                        Smart Baholash
                    </h1>
                </div>
                <button
                    onClick={() => router.push('/')}
                    className="flex items-center gap-2 text-sm font-bold text-slate-400 hover:text-white transition-colors"
                >
                    <ArrowLeft size={16} /> Bosh sahifa
                </button>
            </header>

            <main className="max-w-5xl mx-auto px-6 py-20 relative z-10">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-16"
                >
                    <h2 className="text-4xl md:text-6xl font-black text-white mb-6 tracking-tighter">
                        Bog'lanish
                    </h2>
                    <p className="text-slate-400 text-lg font-medium max-w-2xl mx-auto">
                        Savollaringiz bormi? Mutaxassislarimiz sizga 24/7 rejimida yordam berishga tayyor.
                        Baholash tizimi bo'yicha har qanday maslahat uchun murojaat qiling.
                    </p>
                </motion.div>

                <div className="grid md:grid-cols-2 gap-8">
                    {contactInfo.map((item, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.1 }}
                            whileHover={{ y: -5, scale: 1.02 }}
                            className="bg-slate-900/60 p-8 rounded-[35px] border border-white/5 backdrop-blur-md flex items-center gap-6 group hover:border-white/10 transition-all shadow-xl"
                        >
                            <div className={`w-16 h-16 bg-${item.color}-500/10 rounded-2xl flex items-center justify-center text-${item.color}-400 group-hover:bg-${item.color}-500 group-hover:text-white transition-all duration-500`}>
                                {item.icon}
                            </div>
                            <div className="flex-1">
                                <div className="text-[10px] font-black font-mono text-slate-500 uppercase tracking-widest mb-1">{item.label}</div>
                                <div className="text-xl font-black text-white tracking-tight mb-1">{item.value}</div>
                                <div className="text-xs text-slate-500 font-medium italic">{item.desc}</div>
                            </div>
                        </motion.div>
                    ))}
                </div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.5 }}
                    className="mt-16 bg-gradient-to-br from-blue-600/20 to-indigo-600/20 p-12 rounded-[50px] border border-blue-500/10 text-center relative overflow-hidden"
                >
                    <h3 className="text-3xl font-black text-white mb-6 tracking-tighter relative z-10">
                        Katta loyihalar bo'yicha hamkorlikmi?
                    </h3>
                    <p className="text-slate-300 max-w-xl mx-auto mb-10 font-medium leading-relaxed relative z-10">
                        Agarda sizda bank yoki yirik tashkilotlar uchun maxsus integratsiya yoki korporativ
                        baholash tizimi yaratish bo'yicha takliflar bo'lsa, biz rasmiy uchrashuvga tayyormiz.
                    </p>
                    <button className="bg-white text-slate-900 px-10 py-4 rounded-2xl font-black uppercase text-sm tracking-widest hover:bg-blue-400 hover:text-white transition-all relative z-10 shadow-2xl">
                        Taqdimot so'rash
                    </button>

                    <div className="absolute -bottom-20 -right-20 w-64 h-64 bg-white/5 blur-[80px] rounded-full pointer-events-none"></div>
                </motion.div>
            </main>

            <footer className="py-12 border-t border-white/5 mt-20 bg-slate-900/40">
                <div className="max-w-5xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
                    <div className="flex items-center gap-4 group">
                        <div className="w-12 h-12 rounded-full overflow-hidden border-[3px] border-slate-900 shadow-[0_0_10px_rgba(59,130,246,0.2)] bg-[#0a0f1c]">
                            <img
                                src="/logo.png?v=Neural"
                                alt="Logo"
                                className="w-full h-full object-cover scale-[1.45] group-hover:scale-[1.5] transition-transform duration-500"
                            />
                        </div>
                        <span className="text-xs font-black text-slate-600 tracking-widest uppercase">Smart Baholash 2026</span>
                    </div>
                    <div className="flex gap-8">
                        <Globe size={18} className="text-slate-700 hover:text-blue-400 transition-colors cursor-pointer" />
                        <Send size={18} className="text-slate-700 hover:text-blue-400 transition-colors cursor-pointer" />
                        <Mail size={18} className="text-slate-700 hover:text-blue-400 transition-colors cursor-pointer" />
                    </div>
                </div>
            </footer>
        </div>
    );
}
