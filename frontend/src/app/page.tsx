"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Car, Building, LogOut, ShieldCheck, BarChart3, Book, Users, CreditCard, FileText, Database } from 'lucide-react';
import { api } from '@/services/api';
import { useTranslation } from '@/i18n/I18nProvider';
import { LanguageSwitcher } from '@/i18n/LanguageSwitcher';
import { ThemeToggle } from '@/components/ThemeToggle';

export default function Dashboard() {
  const router = useRouter();
  const { t } = useTranslation();
  const [user, setUser] = useState<{ full_name: string, role: string } | null>(null);
  const [adminStats, setAdminStats] = useState<{ total_users: number, total_reports: number, total_payments: number } | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await api.get(`users/me?t=${Date.now()}`);
        const userData = res.data;
        setUser(userData);
        
        if (userData.role === 'super_admin' || userData.role === 'admin') {
          const statsRes = await api.get('users/admin-stats/');
          setAdminStats(statsRes.data);
        }
      } catch (err: any) {
        const errDetails = `${err.name}: ${err.message} (Code: ${err.code})`;
        window.location.href = '/login?err=' + encodeURIComponent(errDetails);
      }
    };
    fetchUser();
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  };

  if (!user) return <div className="min-h-screen flex items-center justify-center">{t.loading}</div>;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#0a0f1c] text-slate-900 dark:text-slate-200 relative overflow-hidden font-sans transition-colors duration-300">
      {/* Background Neural Decorations */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/5 dark:bg-blue-600/10 blur-[120px] rounded-full shadow-[0_0_100px_rgba(37,99,235,0.1)] pointer-events-none transition-colors duration-300"></div>
      <div className="absolute top-[20%] right-[-10%] w-[30%] h-[30%] bg-purple-600/5 dark:bg-purple-600/10 blur-[120px] rounded-full pointer-events-none transition-colors duration-300"></div>
      <div className="absolute bottom-[-10%] left-[20%] w-[30%] h-[30%] bg-emerald-500/5 blur-[100px] rounded-full pointer-events-none"></div>
      <div className="absolute top-[40%] right-[30%] w-[20%] h-[20%] bg-cyan-500/5 blur-[80px] rounded-full pointer-events-none"></div>

      {/* Header */}
      <header className="relative z-50 px-6 py-4 flex justify-between items-center bg-white/80 dark:bg-slate-900/40 backdrop-blur-xl border-b border-slate-200 dark:border-white/5 transition-colors duration-300">
        <div className="flex items-center gap-4">
          <div className="relative flex items-center justify-center mr-4">
            <div className="w-32 h-32 rounded-full overflow-hidden border-[6px] border-white dark:border-slate-900 shadow-[0_0_25px_rgba(59,130,246,0.2)] dark:shadow-[0_0_25px_rgba(59,130,246,0.4)] bg-slate-100 dark:bg-[#0a0f1c] transition-colors duration-300">
              <img
                src="/logo.png?v=Neural"
                alt="Smart Baholash"
                className="w-full h-full object-cover scale-[1.45] hover:scale-[1.5] transition-transform duration-500"
              />
            </div>
          </div>
          <h1 className="text-4xl font-black bg-gradient-to-r from-blue-700 via-blue-500 to-blue-400 dark:from-white dark:via-blue-200 dark:to-blue-500 bg-clip-text text-transparent tracking-tighter">
            Smart Baholash
          </h1>
        </div>

        {/* Navigation Links */}
        <nav className="hidden lg:flex items-center gap-8 px-8 py-2 bg-slate-100/50 dark:bg-white/5 rounded-full border border-slate-200 dark:border-white/5 backdrop-blur-md transition-colors duration-300">
          {user.role === 'super_admin' || user.role === 'admin' ? (
            <>
              <a href="/admin/users" className="text-sm font-bold text-slate-800 dark:text-white hover:text-blue-500 flex items-center gap-2"><Users size={16} /> Foydalanuvchilar</a>
              <a href="/approvals" className="text-sm font-bold text-slate-800 dark:text-white hover:text-emerald-500 flex items-center gap-2"><CreditCard size={16} /> To'lovlar</a>
            </>
          ) : (
            <>
              <a href="/" className="text-sm font-bold text-slate-800 dark:text-white hover:text-blue-500 dark:hover:text-blue-400 transition-colors">{t.nav.home}</a>
              <a href="/settings" className="text-sm font-bold text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white transition-colors">Sozlamalar</a>
              <a href="/about" className="text-sm font-bold text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white transition-colors">{t.nav.about}</a>
              <a href="/contact" className="text-sm font-bold text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white transition-colors">{t.nav.contact}</a>
            </>
          )}
        </nav>

        <div className="flex items-center gap-3 md:gap-6 text-slate-600 dark:text-slate-300">
          <ThemeToggle />
          <LanguageSwitcher />
          <div className="hidden md:flex flex-col text-right border-l border-slate-200 dark:border-white/10 pl-6 transition-colors duration-300">
            <span className="text-sm font-bold text-slate-800 dark:text-white tracking-wide">{user.full_name}</span>
            <span className={`text-[10px] font-black uppercase tracking-widest ${user.role === 'super_admin' ? 'text-rose-500' : 'text-blue-600 dark:text-blue-400'}`}>
              {user.role === 'super_admin' ? 'Egasi' : user.role === 'admin' ? 'Admin' : 'Foydalanuvchi'}
            </span>
          </div>
          <button
            onClick={handleLogout}
            className="p-2.5 text-slate-400 hover:text-red-500 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 rounded-xl transition-all border border-transparent hover:border-red-200 dark:hover:border-red-500/20"
          >
            <LogOut size={20} />
          </button>
        </div>
      </header>

      {/* Main Content Component Selection */}
      <main className="max-w-6xl mx-auto px-6 py-12 relative z-10">
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-black text-slate-900 dark:text-white mb-4 tracking-tighter drop-shadow-sm dark:drop-shadow-lg transition-colors duration-300">
            {user.role === 'admin' ? t.admin_panel : user.role === 'appraiser' ? t.appraiser_desk : t.select_module}
          </h2>
          <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto text-lg font-medium flex items-center justify-center gap-3 transition-colors duration-300">
            <span className="w-3 h-3 bg-blue-500 rounded-full animate-pulse shadow-[0_0_10px_rgba(37,99,235,0.4)] dark:shadow-[0_0_10px_rgba(37,99,235,0.8)]"></span>
            {(user.role === 'super_admin' || user.role === 'admin') ? t.admin_desc : user.role === 'appraiser' ? t.appraiser_desc : t.module_desc}
          </p>
        </motion.div>

        {/* ================= ADMIN QUICK STATS ================= */}
        {(user.role === 'super_admin' || user.role === 'admin') && adminStats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }} 
              animate={{ opacity: 1, scale: 1 }}
              whileHover={{ y: -5, scale: 1.02 }}
              onClick={() => router.push('/admin/users')}
              className="bg-white/60 dark:bg-slate-900/40 backdrop-blur-md p-6 rounded-3xl border border-slate-200 dark:border-white/5 shadow-sm cursor-pointer group transition-all duration-300 hover:border-blue-500/50"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-blue-500/10 rounded-2xl flex items-center justify-center text-blue-500 group-hover:bg-blue-500 group-hover:text-white transition-all">
                  <Users size={24} />
                </div>
                <div>
                  <div className="text-2xl font-black text-slate-900 dark:text-white group-hover:text-blue-500 transition-colors">{adminStats.total_users}</div>
                  <div className="text-[10px] font-black uppercase tracking-wider text-slate-500">Foydalanuvchilar</div>
                </div>
              </div>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }} 
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
              whileHover={{ y: -5, scale: 1.02 }}
              onClick={() => router.push('/reports')}
              className="bg-white/60 dark:bg-slate-900/40 backdrop-blur-md p-6 rounded-3xl border border-slate-200 dark:border-white/5 shadow-sm cursor-pointer group transition-all duration-300 hover:border-emerald-500/50"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-emerald-500/10 rounded-2xl flex items-center justify-center text-emerald-500 group-hover:bg-emerald-500 group-hover:text-white transition-all">
                  <FileText size={24} />
                </div>
                <div>
                  <div className="text-2xl font-black text-slate-900 dark:text-white group-hover:text-emerald-500 transition-colors">{adminStats.total_reports}</div>
                  <div className="text-[10px] font-black uppercase tracking-wider text-slate-500">Jami Hisobotlar</div>
                </div>
              </div>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }} 
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              whileHover={{ y: -5, scale: 1.02 }}
              onClick={() => router.push('/approvals')}
              className="bg-white/60 dark:bg-slate-900/40 backdrop-blur-md p-6 rounded-3xl border border-slate-200 dark:border-white/5 shadow-sm cursor-pointer group transition-all duration-300 hover:border-amber-500/50"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-amber-500/10 rounded-2xl flex items-center justify-center text-amber-500 group-hover:bg-amber-500 group-hover:text-white transition-all">
                  <CreditCard size={24} />
                </div>
                <div>
                  <div className="text-2xl font-black text-slate-900 dark:text-white group-hover:text-amber-500 transition-colors">{adminStats.total_payments}</div>
                  <div className="text-[10px] font-black uppercase tracking-wider text-slate-500">Tasdiqlangan To'lovlar</div>
                </div>
              </div>
            </motion.div>
          </div>
        )}

        {/* ================= ADMIN VIEW ================= */}
        {(user.role === 'super_admin' || user.role === 'admin') && (
          <div className="max-w-4xl mx-auto">
            {/* Admin Users Module Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              whileHover={{ y: -8, scale: 1.02 }}
              onClick={() => router.push('/admin/users')}
              className="bg-white/80 dark:bg-slate-900/60 backdrop-blur-md rounded-[35px] p-8 border border-slate-200 dark:border-white/5 hover:border-amber-400 dark:hover:border-amber-500/40 cursor-pointer group transition-all duration-700 relative overflow-hidden shadow-xl dark:shadow-2xl hover:shadow-[0_20px_50px_rgba(245,158,11,0.15)] dark:hover:shadow-[0_20px_50px_rgba(245,158,11,0.1)]"
            >
              <div className="absolute top-0 right-0 w-40 h-40 bg-amber-100/50 dark:bg-amber-600/10 blur-[40px] rounded-full -mr-10 -mt-10 group-hover:bg-amber-200/50 dark:group-hover:bg-amber-600/20 transition-all duration-700"></div>
              <div className="w-16 h-16 bg-amber-50 dark:bg-amber-600/10 rounded-2xl flex items-center justify-center text-amber-600 dark:text-amber-400 border border-amber-200 dark:border-amber-500/20 mb-6 group-hover:bg-amber-600 group-hover:text-white transition-all duration-500 shadow-sm dark:shadow-lg">
                <ShieldCheck size={32} />
              </div>
              <h3 className="text-2xl font-black text-slate-900 dark:text-white mb-3 tracking-tight group-hover:text-amber-600 dark:group-hover:text-amber-200 transition-colors uppercase">{t.manage_users}</h3>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed mb-8 font-medium transition-colors duration-300">
                {t.manage_users_desc}
              </p>
              <div className="text-xs font-black text-amber-600 dark:text-amber-500 group-hover:text-amber-800 dark:group-hover:text-amber-300 uppercase tracking-[0.2em] flex items-center gap-2 border-t border-slate-100 dark:border-white/5 pt-5 transition-colors">
                {t.manage} <span aria-hidden="true" className="group-hover:translate-x-2 transition-transform">&rarr;</span>
              </div>
            </motion.div>
          </div>
        )}

        {/* ================= MAIN MODULES (Valuation & Tools) ================= */}
        {user && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* Vehicle Module Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              whileHover={{ y: -8, scale: 1.02 }}
              onClick={() => router.push('/vehicles')}
              className="bg-white/80 dark:bg-slate-900/60 backdrop-blur-md rounded-[35px] p-8 border border-slate-200 dark:border-white/5 hover:border-blue-400 dark:hover:border-blue-500/40 cursor-pointer group transition-all duration-700 relative overflow-hidden shadow-xl dark:shadow-2xl hover:shadow-[0_20px_50px_rgba(37,99,235,0.15)] dark:hover:shadow-[0_20px_50px_rgba(37,99,235,0.1)]"
            >
              <div className="absolute top-0 right-0 w-40 h-40 bg-blue-100/50 dark:bg-blue-600/10 blur-[40px] rounded-full -mr-10 -mt-10 group-hover:bg-blue-200/50 dark:group-hover:bg-blue-600/20 transition-all duration-700"></div>
              <div className="w-16 h-16 bg-blue-50 dark:bg-blue-600/10 rounded-2xl flex items-center justify-center text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-500/20 mb-6 group-hover:bg-blue-600 group-hover:text-white transition-all duration-500 shadow-sm dark:shadow-lg">
                <Car size={32} />
              </div>
              <h3 className="text-2xl font-black text-slate-900 dark:text-white mb-3 tracking-tight group-hover:text-blue-600 dark:group-hover:text-blue-200 transition-colors uppercase">{t.auto_valuation}</h3>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed mb-8 font-medium transition-colors duration-300">
                {t.auto_desc}
              </p>
              <div className="text-xs font-black text-blue-600 dark:text-blue-500 group-hover:text-blue-800 dark:group-hover:text-blue-300 uppercase tracking-[0.2em] flex items-center gap-2 border-t border-slate-100 dark:border-white/5 pt-5 transition-colors">
                {t.start} <span aria-hidden="true" className="group-hover:translate-x-2 transition-transform">&rarr;</span>
              </div>
            </motion.div>

            {/* Real Estate Module Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
              whileHover={{ y: -8, scale: 1.02 }}
              onClick={() => router.push('/real-estate')}
              className="bg-white/80 dark:bg-slate-900/60 backdrop-blur-md rounded-[35px] p-8 border border-slate-200 dark:border-white/5 hover:border-indigo-400 dark:hover:border-indigo-500/40 cursor-pointer group transition-all duration-700 relative overflow-hidden shadow-xl dark:shadow-2xl hover:shadow-[0_20px_50px_rgba(99,102,241,0.15)] dark:hover:shadow-[0_20px_50px_rgba(99,102,241,0.1)]"
            >
              <div className="absolute top-0 right-0 w-40 h-40 bg-indigo-100/50 dark:bg-indigo-600/10 blur-[40px] rounded-full -mr-10 -mt-10 group-hover:bg-indigo-200/50 dark:group-hover:bg-indigo-600/20 transition-all duration-700"></div>
              <div className="w-16 h-16 bg-indigo-50 dark:bg-indigo-600/10 rounded-2xl flex items-center justify-center text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/20 mb-6 group-hover:bg-indigo-600 group-hover:text-white transition-all duration-500 shadow-sm dark:shadow-lg">
                <Building size={32} />
              </div>
              <h3 className="text-2xl font-black text-slate-900 dark:text-white mb-3 tracking-tight group-hover:text-indigo-600 dark:group-hover:text-indigo-200 transition-colors uppercase">{t.real_estate}</h3>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed mb-8 font-medium transition-colors duration-300">
                {t.real_estate_desc}
              </p>
              <div className="text-xs font-black text-indigo-600 dark:text-indigo-500 group-hover:text-indigo-800 dark:group-hover:text-indigo-300 uppercase tracking-[0.2em] flex items-center gap-2 border-t border-slate-100 dark:border-white/5 pt-5 transition-colors">
                {t.start} <span aria-hidden="true" className="group-hover:translate-x-2 transition-transform">&rarr;</span>
              </div>
            </motion.div>

            {/* Appraiser Inbox View (Admins Only) */}
            {(user.role === 'super_admin' || user.role === 'admin') && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                whileHover={{ y: -8, scale: 1.02 }}
                onClick={() => router.push('/approvals')}
                className="bg-white/80 dark:bg-slate-900/60 backdrop-blur-md rounded-[35px] p-8 border border-slate-200 dark:border-white/5 hover:border-red-400 dark:hover:border-red-500/40 cursor-pointer group transition-all duration-700 relative overflow-hidden shadow-xl dark:shadow-2xl hover:shadow-[0_20px_50px_rgba(239,68,68,0.15)] dark:hover:shadow-[0_20px_50px_rgba(239,68,68,0.1)]"
              >
                <div className="absolute top-0 right-0 w-40 h-40 bg-red-100/50 dark:bg-red-600/10 blur-[40px] rounded-full -mr-10 -mt-10 group-hover:bg-red-200/50 dark:group-hover:bg-red-600/20 transition-all duration-700"></div>
                <div className="w-16 h-16 bg-red-50 dark:bg-red-600/10 rounded-2xl flex items-center justify-center text-red-600 dark:text-red-400 border border-red-200 dark:border-red-500/20 mb-6 group-hover:bg-red-600 group-hover:text-white transition-all duration-500 shadow-sm dark:shadow-lg">
                  <ShieldCheck size={32} />
                </div>
                <h3 className="text-2xl font-black text-slate-900 dark:text-white mb-3 tracking-tight group-hover:text-red-600 dark:group-hover:text-red-200 transition-colors uppercase">{t.pending_reports}</h3>
                <p className="text-slate-600 dark:text-slate-400 leading-relaxed mb-8 font-medium transition-colors duration-300">
                  {t.pending_reports_desc}
                </p>
                <div className="text-xs font-black text-red-600 dark:text-red-500 group-hover:text-red-800 dark:group-hover:text-red-300 uppercase tracking-[0.2em] flex items-center gap-2 border-t border-slate-100 dark:border-white/5 pt-5 transition-colors">
                  {t.view} <span aria-hidden="true" className="group-hover:translate-x-2 transition-transform">&rarr;</span>
                </div>
              </motion.div>
            )}

            {/* Reports History */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.25 }}
              whileHover={{ y: -8, scale: 1.02 }}
              onClick={() => router.push('/reports')}
              className="bg-white/80 dark:bg-slate-900/60 backdrop-blur-md rounded-[35px] p-8 border border-slate-200 dark:border-white/5 hover:border-emerald-400 dark:hover:border-emerald-500/40 cursor-pointer group transition-all duration-700 relative overflow-hidden shadow-xl dark:shadow-2xl hover:shadow-[0_20px_50px_rgba(16,185,129,0.15)] dark:hover:shadow-[0_20px_50px_rgba(16,185,129,0.1)]"
            >
              <div className="absolute top-0 right-0 w-40 h-40 bg-emerald-100/50 dark:bg-emerald-600/10 blur-[40px] rounded-full -mr-10 -mt-10 group-hover:bg-emerald-200/50 dark:group-hover:bg-emerald-600/20 transition-all duration-700"></div>
              <div className="w-16 h-16 bg-emerald-50 dark:bg-emerald-600/10 rounded-2xl flex items-center justify-center text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20 mb-6 group-hover:bg-emerald-600 group-hover:text-white transition-all duration-500 shadow-sm dark:shadow-lg">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
              </div>
              <h3 className="text-2xl font-black text-slate-900 dark:text-white mb-3 tracking-tight group-hover:text-emerald-600 dark:group-hover:text-emerald-200 transition-colors uppercase">{t.my_reports}</h3>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed mb-8 font-medium transition-colors duration-300">
                {t.my_reports_desc}
              </p>
              <div className="text-xs font-black text-emerald-600 dark:text-emerald-500 group-hover:text-emerald-800 dark:group-hover:text-emerald-300 uppercase tracking-[0.2em] flex items-center gap-2 border-t border-slate-100 dark:border-white/5 pt-5 transition-colors">
                {t.enter} <span aria-hidden="true" className="group-hover:translate-x-2 transition-transform">&rarr;</span>
              </div>
            </motion.div>

            {/* Statistics */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              whileHover={{ y: -8, scale: 1.02 }}
              onClick={() => router.push('/statistics')}
              className="bg-white/80 dark:bg-slate-900/60 backdrop-blur-md rounded-[35px] p-8 border border-slate-200 dark:border-white/5 hover:border-amber-400 dark:hover:border-amber-500/40 cursor-pointer group transition-all duration-700 relative overflow-hidden shadow-xl dark:shadow-2xl hover:shadow-[0_20px_50px_rgba(245,158,11,0.15)] dark:hover:shadow-[0_20px_50px_rgba(245,158,11,0.1)]"
            >
              <div className="absolute top-0 right-0 w-40 h-40 bg-amber-100/50 dark:bg-amber-600/10 blur-[40px] rounded-full -mr-10 -mt-10 group-hover:bg-amber-200/50 dark:group-hover:bg-amber-600/20 transition-all duration-700"></div>
              <div className="w-16 h-16 bg-amber-50 dark:bg-amber-600/10 rounded-2xl flex items-center justify-center text-amber-600 dark:text-amber-400 border border-amber-200 dark:border-amber-500/20 mb-6 group-hover:bg-amber-600 group-hover:text-white transition-all duration-500 shadow-sm dark:shadow-lg">
                <BarChart3 size={32} />
              </div>
              <h3 className="text-2xl font-black text-slate-900 dark:text-white mb-3 tracking-tight group-hover:text-amber-600 dark:group-hover:text-amber-200 transition-colors uppercase">{t.bozor_stats}</h3>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed mb-8 font-medium transition-colors duration-300">
                {t.bozor_stats_full}
              </p>
              <div className="text-xs font-black text-amber-600 dark:text-amber-500 group-hover:text-amber-800 dark:group-hover:text-amber-300 uppercase tracking-[0.2em] flex items-center gap-2 border-t border-slate-100 dark:border-white/5 pt-5 transition-colors">
                {t.manage} <span aria-hidden="true" className="group-hover:translate-x-2 transition-transform">&rarr;</span>
              </div>
            </motion.div>

            {/* Analogs Database */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.35 }}
              whileHover={{ y: -8, scale: 1.02 }}
              onClick={() => router.push('/analogs')}
              className="bg-white/80 dark:bg-slate-900/60 backdrop-blur-md rounded-[35px] p-8 border border-slate-200 dark:border-white/5 hover:border-blue-400 dark:hover:border-blue-500/40 cursor-pointer group transition-all duration-700 relative overflow-hidden shadow-xl dark:shadow-2xl hover:shadow-[0_20px_50px_rgba(59,130,246,0.15)] dark:hover:shadow-[0_20px_50px_rgba(59,130,246,0.1)]"
            >
              <div className="absolute top-0 right-0 w-40 h-40 bg-blue-100/50 dark:bg-blue-600/10 blur-[40px] rounded-full -mr-10 -mt-10 group-hover:bg-blue-200/50 dark:group-hover:bg-blue-600/20 transition-all duration-700"></div>
              <div className="w-16 h-16 bg-blue-50 dark:bg-blue-600/10 rounded-2xl flex items-center justify-center text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-500/20 mb-6 group-hover:bg-blue-600 group-hover:text-white transition-all duration-500 shadow-sm dark:shadow-lg">
                <Database size={32} />
              </div>
              <h3 className="text-2xl font-black text-slate-900 dark:text-white mb-3 tracking-tight group-hover:text-blue-600 dark:group-hover:text-blue-200 transition-colors uppercase">{t.analogs_db}</h3>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed mb-8 font-medium transition-colors duration-300">
                {t.analogs_db_desc}
              </p>
              <div className="text-xs font-black text-blue-600 dark:text-blue-500 group-hover:text-blue-800 dark:group-hover:text-blue-300 uppercase tracking-[0.2em] flex items-center gap-2 border-t border-slate-100 dark:border-white/5 pt-5 transition-colors">
                {t.enter} <span aria-hidden="true" className="group-hover:translate-x-2 transition-transform">&rarr;</span>
              </div>
            </motion.div>

            {/* Library (Kutubxona) */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.35 }}
              whileHover={{ y: -8, scale: 1.02 }}
              onClick={() => router.push('/library')}
              className="bg-white/80 dark:bg-slate-900/60 backdrop-blur-md rounded-[35px] p-8 border border-slate-200 dark:border-white/5 hover:border-emerald-400 dark:hover:border-emerald-500/40 cursor-pointer group transition-all duration-700 relative overflow-hidden shadow-xl dark:shadow-2xl hover:shadow-[0_20px_50px_rgba(16,185,129,0.15)] dark:hover:shadow-[0_20px_50px_rgba(16,185,129,0.1)]"
            >
              <div className="absolute top-0 right-0 w-40 h-40 bg-emerald-100/50 dark:bg-emerald-600/10 blur-[40px] rounded-full -mr-10 -mt-10 group-hover:bg-emerald-200/50 dark:group-hover:bg-emerald-600/20 transition-all duration-700"></div>
              <div className="w-16 h-16 bg-emerald-50 dark:bg-emerald-600/10 rounded-2xl flex items-center justify-center text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20 mb-6 group-hover:bg-emerald-600 group-hover:text-white transition-all duration-500 shadow-sm dark:shadow-lg">
                <Book size={32} />
              </div>
              <h3 className="text-2xl font-black text-slate-900 dark:text-white mb-3 tracking-tight group-hover:text-emerald-600 dark:group-hover:text-emerald-200 transition-colors uppercase">{t.library_title}</h3>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed mb-8 font-medium transition-colors duration-300">
                {t.library_desc_full}
              </p>
              <div className="text-xs font-black text-emerald-600 dark:text-emerald-500 group-hover:text-emerald-800 dark:group-hover:text-emerald-300 uppercase tracking-[0.2em] flex items-center gap-2 border-t border-slate-100 dark:border-white/5 pt-5 transition-colors">
                {t.enter} <span aria-hidden="true" className="group-hover:translate-x-2 transition-transform">&rarr;</span>
              </div>
            </motion.div>
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="relative z-50 mt-20 border-t border-slate-200 dark:border-white/5 bg-white/60 dark:bg-slate-900/40 backdrop-blur-xl py-12 transition-colors duration-300">
        <div className="max-w-6xl mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-12">
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center gap-8 mb-10">
              <div className="w-24 h-24 rounded-full overflow-hidden border-[5px] border-white dark:border-slate-900 shadow-[0_0_15px_rgba(59,130,246,0.1)] dark:shadow-[0_0_15px_rgba(59,130,246,0.3)] bg-slate-50 dark:bg-[#0a0f1c] transition-colors duration-300">
                <img
                  src="/logo.png?v=Neural"
                  alt="Smart Baholash Logo"
                  className="w-full h-full object-cover scale-[1.45] hover:scale-[1.5] transition-transform duration-500"
                />
              </div>
              <h3 className="text-4xl font-black text-slate-900 dark:text-white tracking-tighter transition-colors duration-300">Smart Baholash</h3>
            </div>
            <p className="text-slate-600 dark:text-slate-500 max-w-sm font-medium leading-relaxed transition-colors duration-300">
              {t.footer.desc}
            </p>
          </div>

          <div>
            <h4 className="text-slate-800 dark:text-white font-black uppercase tracking-widest text-xs mb-6 transition-colors duration-300">{t.footer.sections}</h4>
            <ul className="space-y-4 text-slate-600 dark:text-slate-500 text-sm font-medium transition-colors duration-300">
              <li><a href="/" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">{t.nav.home}</a></li>
              <li><a href="/vehicles" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">{t.footer.auto}</a></li>
              <li><a href="/real-estate" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">{t.footer.re}</a></li>
              <li><a href="/reports" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">{t.footer.reports}</a></li>
            </ul>
          </div>

          <div>
            <h4 className="text-slate-800 dark:text-white font-black uppercase tracking-widest text-xs mb-6 transition-colors duration-300">{t.nav.contact}</h4>
            <ul className="space-y-4 text-slate-600 dark:text-slate-500 text-sm font-medium transition-colors duration-300">
              <li className="flex items-center gap-2 italic">smartbaholashai@gmail.com</li>
              <li className="flex items-center gap-2">+998 (91) 699-61-79</li>
              <li className="text-[10px] uppercase tracking-tighter border-t border-slate-200 dark:border-white/5 pt-4 transition-colors duration-300">
                Farg'ona viloyati, Qo'qon shahar, Furqat ko'chasi, 100-uy.
              </li>
            </ul>
          </div>
        </div>

        <div className="max-w-6xl mx-auto px-6 mt-12 pt-8 border-t border-slate-200 dark:border-white/5 flex flex-col md:flex-row justify-between items-center gap-4 text-[10px] font-black uppercase tracking-[0.3em] text-slate-500 dark:text-slate-600 transition-colors duration-300">
          <div>&copy; 2026 SMART BAHOLASH TIZIMI. {t.footer.rights}</div>
          <div className="flex gap-6">
            <span className="hover:text-slate-700 dark:hover:text-slate-400 cursor-pointer transition-colors duration-300">{t.footer.privacy}</span>
            <span className="hover:text-slate-700 dark:hover:text-slate-400 cursor-pointer transition-colors duration-300">{t.footer.terms}</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
