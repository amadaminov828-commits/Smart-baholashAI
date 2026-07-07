"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/services/api';
import { Lock, User } from 'lucide-react';
import { motion } from 'framer-motion';
import { useTranslation } from '@/i18n/I18nProvider';
import { LanguageSwitcher } from '@/i18n/LanguageSwitcher';
import { ThemeToggle } from '@/components/ThemeToggle';

export default function LoginPage() {
    const { t } = useTranslation();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const router = useRouter();

    useEffect(() => {
        const errParam = new URLSearchParams(window.location.search).get('err');
        if (errParam) {
            setError(decodeURIComponent(errParam));
        }
    }, []);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const cleanUsername = username.trim();
            const cleanPassword = password.trim();
            const res = await api.post('users/auth/login', { username: cleanUsername, password: cleanPassword });
            localStorage.setItem('access_token', res.data.access);
            localStorage.setItem('refresh_token', res.data.refresh);
            window.location.href = '/';
        } catch (err: any) {
            const serverMsg = err.response?.data?.detail || err.response?.data?.non_field_errors?.[0];
            setError(serverMsg || t.login_error);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-slate-900 dark:to-[#0a0f1c] p-4 relative transition-colors duration-500">
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
                    <h1 className="text-3xl font-bold text-gray-800 dark:text-white tracking-tight">{t.login_title}</h1>
                    <p className="text-gray-500 dark:text-slate-400 mt-2 text-sm">{t.login_subtitle}</p>
                </div>

                {error && (
                    <motion.div
                        initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                        className="bg-red-50 text-red-500 p-3 rounded-xl mb-6 text-sm text-center border border-red-100"
                    >
                        {error}
                    </motion.div>
                )}

                <form onSubmit={handleLogin} className="space-y-6">
                    <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                            <User size={20} />
                        </div>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="w-full pl-10 pr-4 py-3 bg-white/50 dark:bg-slate-800/50 border border-gray-200 dark:border-slate-700/50 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all placeholder:text-gray-400 dark:placeholder:text-slate-500 dark:text-white"
                            placeholder={t.username}
                            required
                        />
                    </div>

                    <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                            <Lock size={20} />
                        </div>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full pl-10 pr-4 py-3 bg-white/50 dark:bg-slate-800/50 border border-gray-200 dark:border-slate-700/50 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all placeholder:text-gray-400 dark:placeholder:text-slate-500 dark:text-white"
                            placeholder={t.password}
                            required
                        />
                    </div>

                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        type="submit"
                        className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl font-medium shadow-lg shadow-blue-500/30 transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                        {t.login_btn || 'Kirish'}
                    </motion.button>

                    <div className="text-center mt-6">
                        <p className="text-gray-500 dark:text-slate-400 text-sm">
                            Hali akkauntingiz yo'qmi?{' '}
                            <Link href="/register" className="text-blue-600 dark:text-blue-400 font-semibold hover:underline">
                                Ro'yxatdan o'tish
                            </Link>
                        </p>
                    </div>
                </form>
            </motion.div>
        </div>
    );
}
