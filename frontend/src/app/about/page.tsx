"use client";

import { motion } from 'framer-motion';
import { ShieldCheck, Cpu, Target, Award, ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function AboutPage() {
    const router = useRouter();

    return (
        <div className="min-h-screen bg-[#0a0f1c] text-slate-200 relative overflow-hidden font-sans">
            {/* Background Decor */}
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/10 blur-[120px] rounded-full pointer-events-none"></div>
            <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-600/10 blur-[120px] rounded-full pointer-events-none"></div>

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
                    <ArrowLeft size={16} /> Ortga qaytish
                </button>
            </header>

            <main className="max-w-4xl mx-auto px-6 py-20 relative z-10">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-20"
                >
                    <h2 className="text-4xl md:text-6xl font-black text-white mb-6 tracking-tighter">
                        Biz Haqimizda
                    </h2>
                    <p className="text-blue-400 text-xl font-bold uppercase tracking-[0.2em]">
                        Kelajak Baholash Tizimi
                    </p>
                </motion.div>

                <div className="grid gap-12">
                    {/* Mission */}
                    <motion.section
                        initial={{ opacity: 0, x: -20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        className="bg-slate-900/60 p-10 rounded-[40px] border border-white/5 backdrop-blur-md"
                    >
                        <div className="flex items-center gap-4 mb-6 text-blue-400">
                            <Target size={32} />
                            <h3 className="text-2xl font-black text-white">Bizning Missiyamiz</h3>
                        </div>
                        <p className="text-slate-400 text-lg leading-relaxed font-medium">
                            "Smart Baholash" - bu shunchaki dastur emas, balki baholash sohasidagi revolutsion yechimdir.
                            Bizning asosiy maqsadimiz - texnologiya va inson intellektini birlashtirib, aktivlarni
                            baholash jarayonini 10 barobar tezroq, aniqroq va shaffofroq qilishdir.
                            Biz har bir hisobot ortida xalqaro standartlar va eng so'nggi algoritmlar turishini ta'minlaymiz.
                        </p>
                    </motion.section>

                    {/* AI Section */}
                    <motion.section
                        initial={{ opacity: 0, x: 20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        className="bg-slate-900/60 p-10 rounded-[40px] border border-white/5 backdrop-blur-md relative overflow-hidden group"
                    >
                        <div className="absolute top-0 right-0 w-32 h-32 bg-purple-600/10 blur-3xl group-hover:bg-purple-600/20 transition-all"></div>
                        <div className="flex items-center gap-4 mb-6 text-purple-400">
                            <Cpu size={32} />
                            <h3 className="text-2xl font-black text-white">Sun'iy Intellekt Kuchi</h3>
                        </div>
                        <p className="text-slate-400 text-lg leading-relaxed font-medium">
                            Biz Google Gemini va NeuralCore kabi ilg'or neyron tarmoqlardan foydalanamiz.
                            Tizim hujjatlardagi ma'lumotlarni (OCR) xatosiz o'qiydi, bozordagi minglab analoglarni
                            soniyalar ichida tahlil qiladi va matematik modellarni real vaqt rejimida hisoblab chiqadi.
                            Bu inson omili tufayli yuzaga keladigan xatolarni deyarli nolga tushiradi.
                        </p>
                    </motion.section>

                    {/* Standards */}
                    <motion.section
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="bg-slate-900/60 p-10 rounded-[40px] border border-white/5 backdrop-blur-md"
                    >
                        <div className="flex items-center gap-4 mb-6 text-emerald-400">
                            <ShieldCheck size={32} />
                            <h3 className="text-2xl font-black text-white">Xalqaro Standartlar</h3>
                        </div>
                        <p className="text-slate-400 text-lg leading-relaxed font-medium">
                            Barcha hisobotlarimiz O'zbekiston Respublikasi va Xalqaro Baholash Standartlari (IVS)
                            talablariga to'liq javob beradi. QR-kod orqali tasdiqlash tizimi esa har bir hujjatning
                            haqqoniyligini butun dunyo bo'ylab tekshirish imkonini beradi.
                        </p>
                    </motion.section>
                </div>

                <div className="mt-20 text-center">
                    <Award className="mx-auto text-blue-500 mb-6 animate-bounce" size={48} />
                    <p className="text-slate-500 font-bold uppercase tracking-widest text-sm">
                        Smart Baholash — Ishonchli Kelajak Poydevori
                    </p>
                </div>
            </main>

            <footer className="py-10 text-center text-slate-600 text-[10px] font-black uppercase tracking-[0.3em] border-t border-white/5 mt-20">
                &copy; 2026 SMART BAHOLASH. BARCHA HUQUQLAR HIMOYA QILINGAN.
            </footer>
        </div>
    );
}
