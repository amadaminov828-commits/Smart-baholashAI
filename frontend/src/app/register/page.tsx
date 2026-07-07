"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/services/api';
import { Lock, User, Phone, Briefcase, UserCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { useTranslation } from '@/i18n/I18nProvider';
import { LanguageSwitcher } from '@/i18n/LanguageSwitcher';
import { ThemeToggle } from '@/components/ThemeToggle';

interface Appraiser {
    id: number;
    full_name: string;
    phone_number: string;
}

export default function RegisterPage() {
    const { t } = useTranslation();
    const router = useRouter();

    const [fullName, setFullName] = useState('');
    const [phone, setPhone] = useState('');
    const [role, setRole] = useState('assistant'); // default
    const [assignedAppraiser, setAssignedAppraiser] = useState('');

    const [appraisers, setAppraisers] = useState<Appraiser[]>([]);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);

    // Fetch appraisers
    useEffect(() => {
        const fetchAppraisers = async () => {
            try {
                const res = await api.get('/users/appraisers/');
                setAppraisers(res.data);
            } catch (err) {
                console.error("Failed to load appraisers", err);
            }
        };
        fetchAppraisers();
    }, []);

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const data = {
                username: phone, // using phone as username
                full_name: fullName,
                phone_number: phone,
                role: role,
                assigned_appraiser: role === 'assistant' && assignedAppraiser ? parseInt(assignedAppraiser, 10) : null
            };

            await api.post('/users/auth/register/', data);

            // On success, show pending approval message
            setIsSuccess(true);
        } catch (err: any) {
            console.error("Registration error:", err.response?.data);
            if (err.response?.data) {
                const errorData = err.response.data;
                if (typeof errorData === 'object' && errorData !== null) {
                    // Formatting the error object into a readable string
                    const errorMessages = Object.keys(errorData)
                        .map(key => `${key}: ${Array.isArray(errorData[key]) ? errorData[key].join(', ') : errorData[key]}`)
                        .join(' | ');
                    setError(errorMessages);
                } else {
                    // It might be a 500 HTML response or just a string
                    setError('Server xatoligi yuz berdi. Iltimos qayta urinib ko\'ring.');
                }
            } else {
                setError('Noma\'lum xatolik yuz berdi. Iltimos qayta urinib ko\'ring.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-slate-900 dark:to-[#0a0f1c] p-4 relative py-12 transition-colors duration-500">
            <div className="absolute top-6 right-6 z-50 flex items-center gap-2">
                <ThemeToggle />
                <LanguageSwitcher />
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="w-full max-w-md glass-panel dark:bg-slate-900/60 dark:border-white/10 rounded-2xl p-8 relative overflow-hidden shadow-2xl"
            >
                <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-blue-400 to-indigo-500"></div>
                <div className="text-center mb-10">
                    <h1 className="text-3xl font-bold text-gray-800 dark:text-white tracking-tight">Ro'yxatdan O'tish</h1>
                    <p className="text-gray-500 dark:text-slate-400 mt-2 text-sm">Akkaunt yarating va tizimga kiring</p>
                </div>

                {error && (
                    <motion.div
                        initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                        className="bg-red-50 text-red-500 p-3 rounded-xl mb-6 text-sm text-center border border-red-100"
                    >
                        {error}
                    </motion.div>
                )}

                {isSuccess ? (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="text-center py-8"
                    >
                        <div className="w-20 h-20 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6">
                            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                        </div>
                        <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-4">So'rov yuborildi!</h2>
                        <p className="text-gray-600 dark:text-gray-300 mb-8 leading-relaxed">
                            Sizning ro'yxatdan o'tish so'rovingiz administratorga yuborildi. So'rov tasdiqlanganidan so'ng, sizga tizimga kirish uchun Login va Parol taqdim etiladi.
                        </p>
                        <Link href="/login" className="inline-block py-3 px-8 bg-gray-800 dark:bg-slate-700 hover:bg-gray-900 dark:hover:bg-slate-600 text-white rounded-xl font-medium transition-colors">
                            Bosh sahifaga qaytish
                        </Link>
                    </motion.div>
                ) : (
                    <form onSubmit={handleRegister} className="space-y-5">
                        {/* F.I.SH. */}
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                                <User size={20} />
                            </div>
                            <input
                                type="text"
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                                className="w-full pl-10 pr-4 py-3 bg-white/50 dark:bg-slate-800/50 border border-gray-200 dark:border-slate-700/50 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all placeholder:text-gray-400 dark:placeholder:text-slate-500 dark:text-white"
                                placeholder="To'liq Ism (F.I.SH)"
                                required
                            />
                        </div>

                        {/* Telefon */}
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                                <Phone size={20} />
                            </div>
                            <input
                                type="text"
                                value={phone}
                                onChange={(e) => setPhone(e.target.value)}
                                className="w-full pl-10 pr-4 py-3 bg-white/50 dark:bg-slate-800/50 border border-gray-200 dark:border-slate-700/50 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all placeholder:text-gray-400 dark:placeholder:text-slate-500 dark:text-white"
                                placeholder="Telefon raqami (Masalan: 998901234567)"
                                required
                            />
                        </div>

                        {/* Role Selection */}
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                                <Briefcase size={20} />
                            </div>
                            <select
                                value={role}
                                onChange={(e) => setRole(e.target.value)}
                                className="w-full pl-10 pr-4 py-3 bg-white/50 dark:bg-slate-800/50 border border-gray-200 dark:border-slate-700/50 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all text-gray-700 dark:text-white appearance-none"
                                required
                            >
                                <option value="assistant">Yordamchi Baholovchi</option>
                                <option value="appraiser">Asosiy Baholovchi</option>
                            </select>
                        </div>

                        {/* Assigned Appraiser (Only if Assistant) */}
                        {role === 'assistant' && (
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                                    <UserCircle size={20} />
                                </div>
                                <select
                                    value={assignedAppraiser}
                                    onChange={(e) => setAssignedAppraiser(e.target.value)}
                                    className="w-full pl-10 pr-4 py-3 bg-white/50 dark:bg-slate-800/50 border border-gray-200 dark:border-slate-700/50 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all text-gray-700 dark:text-white appearance-none"
                                    required
                                >
                                    <option value="" disabled>Asosiy Baholovchini Tanlang</option>
                                    {appraisers.map((appraiser) => (
                                        <option key={appraiser.id} value={appraiser.id.toString()}>
                                            {appraiser.full_name || appraiser.phone_number}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        )}

                        <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            type="submit"
                            disabled={loading}
                            className={`w-full py-3 px-4 bg-gradient-to-r ${loading ? 'from-gray-400 to-gray-500' : 'from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700'} text-white rounded-xl font-medium shadow-lg shadow-blue-500/30 transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
                        >
                            {loading ? 'Yuborilmoqda...' : 'So\'rov Yuborish'}
                        </motion.button>

                        <div className="text-center mt-6">
                            <p className="text-gray-500 dark:text-slate-400 text-sm">
                                Oldin akkaunt ochganmisiz?{' '}
                                <Link href="/login" className="text-blue-600 dark:text-blue-400 font-semibold hover:underline">
                                    Tizimga Kirish
                                </Link>
                            </p>
                        </div>
                    </form>
                )}
            </motion.div>
        </div>
    );
}
