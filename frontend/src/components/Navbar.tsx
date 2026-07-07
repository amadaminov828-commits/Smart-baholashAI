"use client";

import { LogOut, Book, Users, CreditCard, Home, Settings } from 'lucide-react';
import { useTranslation } from '@/i18n/I18nProvider';
import { LanguageSwitcher } from '@/i18n/LanguageSwitcher';
import { ThemeToggle } from '@/components/ThemeToggle';
import { useEffect, useState } from 'react';
import { api } from '@/services/api';

export function Navbar() {
  const { t } = useTranslation();
  const [user, setUser] = useState<{ full_name: string, role: string } | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await api.get('users/me');
        setUser(res.data);
      } catch (err) {
        console.error("Navbar fetch user error", err);
      }
    };
    fetchUser();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  };

  const isAdmin = user && (user.role === 'super_admin' || user.role === 'admin');

  return (
    <header className="relative z-50 px-6 py-4 flex justify-between items-center bg-white/80 dark:bg-slate-900/40 backdrop-blur-xl border-b border-slate-200 dark:border-white/5 transition-colors duration-300">
      <div className="flex items-center gap-4 cursor-pointer" onClick={() => window.location.href = '/'}>
        <div className="relative flex items-center justify-center mr-4">
          <div className="w-12 h-12 rounded-full overflow-hidden border-2 border-white dark:border-slate-900 shadow-lg bg-slate-100 dark:bg-[#0a0f1c]">
            <img
              src="/logo.png"
              alt="Smart Baholash"
              className="w-full h-full object-cover scale-125"
            />
          </div>
        </div>
        <h1 className="text-xl font-black bg-gradient-to-r from-blue-700 to-blue-400 dark:from-white dark:to-blue-500 bg-clip-text text-transparent tracking-tighter">
          Smart Baholash
        </h1>
      </div>

      <nav className="hidden lg:flex items-center gap-4 px-6 py-2 bg-slate-100/50 dark:bg-white/5 rounded-full border border-slate-200 dark:border-white/5 backdrop-blur-md transition-colors duration-300">
        <a href="/" className="text-[10px] font-black uppercase tracking-widest text-slate-800 dark:text-white hover:text-blue-500 transition-colors flex items-center gap-2">
          <Home size={14} /> Bosh sahifa
        </a>
        
        {isAdmin && (
          <>
            <a href="/admin/users" className="text-[10px] font-black uppercase tracking-widest text-slate-800 dark:text-white hover:text-blue-500 transition-colors flex items-center gap-2">
              <Users size={14} /> Foydalanuvchilar
            </a>
            <a href="/approvals" className="text-[10px] font-black uppercase tracking-widest text-slate-800 dark:text-white hover:text-emerald-500 transition-colors flex items-center gap-2">
              <CreditCard size={14} /> To'lovlar
            </a>
          </>
        )}

        <a href="/library" className="text-[10px] font-black uppercase tracking-widest text-blue-500 transition-colors flex items-center gap-2">
           <Book size={14} /> Kutubxona
        </a>

        <a href="/settings" className="text-[10px] font-black uppercase tracking-widest text-slate-800 dark:text-white hover:text-blue-500 transition-colors flex items-center gap-2">
           <Settings size={14} /> Sozlamalar
        </a>
      </nav>

      <div className="flex items-center gap-3 md:gap-6 text-slate-600 dark:text-slate-300">
        <ThemeToggle />
        <LanguageSwitcher />
        {user && (
          <div className="hidden md:flex flex-col text-right border-l border-slate-200 dark:border-white/10 pl-6">
            <span className="text-sm font-bold text-slate-800 dark:text-white tracking-wide">{user.full_name}</span>
            <span className={`text-[10px] font-black uppercase tracking-widest ${user.role === 'super_admin' ? 'text-rose-500' : 'text-blue-600 dark:text-blue-400'}`}>
              {user.role === 'super_admin' ? 'Egasi' : user.role === 'admin' ? 'Admin' : 'Foydalanuvchi'}
            </span>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="p-2.5 text-slate-400 hover:text-red-500 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 rounded-xl transition-all border border-transparent hover:border-red-200 dark:hover:border-red-500/20"
        >
          <LogOut size={20} />
        </button>
      </div>
    </header>
  );
}
