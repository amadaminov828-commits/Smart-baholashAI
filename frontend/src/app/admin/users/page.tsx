"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/services/api';
import { Key, UserCheck, ShieldCheck, UserPlus, Trash2, Edit2, RefreshCw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface ManagedUser {
    id: number;
    username: string;
    full_name: string;
    phone_number: string;
    role: string;
    last_name: string; // Used to store plain password as requested
    is_active: boolean;
}

export default function AdminUsersPage() {
    const router = useRouter();

    const [me, setMe] = useState<any>(null);
    const [authLoading, setAuthLoading] = useState(true);
    const [users, setUsers] = useState<ManagedUser[]>([]);
    const [loading, setLoading] = useState(true);
    
    // Create/Edit Modal State
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingUser, setEditingUser] = useState<ManagedUser | null>(null);
    const [formData, setFormData] = useState({
        username: '',
        full_name: '',
        phone_number: '',
        role: 'user',
        password: ''
    });

    const [submitting, setSubmitting] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    useEffect(() => {
        const fetchMe = async () => {
            try {
                const res = await api.get(`users/me/`);
                if (res.data.role !== 'super_admin' && res.data.role !== 'admin') {
                    window.location.href = '/';
                } else {
                    setMe(res.data);
                }
            } catch (err) {
                window.location.href = '/login';
            } finally {
                setAuthLoading(false);
            }
        };
        fetchMe();
    }, []);

    const fetchUsers = async () => {
        try {
            setLoading(true);
            const res = await api.get('/users/manage/');
            setUsers(res.data);
        } catch (err) {
            console.error(err);
            setMessage({ type: 'error', text: "Foydalanuvchilarni yuklashda xatolik" });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (me) {
            fetchUsers();
        }
    }, [me]);

    const handleOpenCreate = () => {
        setEditingUser(null);
        setFormData({ username: '', full_name: '', phone_number: '', role: 'user', password: '' });
        setIsModalOpen(true);
    };

    const handleOpenEdit = (user: ManagedUser) => {
        setEditingUser(user);
        setFormData({
            username: user.username,
            full_name: user.full_name || '',
            phone_number: user.phone_number || '',
            role: user.role,
            password: '' // Keep empty unless changing
        });
        setIsModalOpen(true);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);
        try {
            if (editingUser) {
                await api.put(`/users/manage/${editingUser.id}/`, formData);
                setMessage({ type: 'success', text: "Foydalanuvchi yangilandi" });
            } else {
                await api.post(`/users/manage/`, formData);
                setMessage({ type: 'success', text: "Yangi foydalanuvchi yaratildi" });
            }
            setIsModalOpen(false);
            fetchUsers();
        } catch (err: any) {
            setMessage({ type: 'error', text: err.response?.data?.username?.[0] || "Xatolik yuz berdi" });
        } finally {
            setSubmitting(false);
            setTimeout(() => setMessage(null), 3000);
        }
    };

    const handleDelete = async (id: number) => {
        if (!window.confirm("Foydalanuvchini o'chirishni tasdiqlaysizmi?")) return;
        try {
            await api.delete(`/users/manage/${id}/`);
            setMessage({ type: 'success', text: "Foydalanuvchi o'chirildi" });
            fetchUsers();
        } catch (err) {
            setMessage({ type: 'error', text: "O'chirishda xatolik (Balki ruxsat yo'qdir)" });
        }
    };

    if (authLoading || !me) return <div className="p-10 flex justify-center"><div className="animate-spin w-8 h-8 rounded-full border-t-2 border-b-2 border-blue-500"></div></div>;

    return (
        <div className="max-w-7xl mx-auto space-y-6">
            <AnimatePresence>
                {message && (
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className={`p-4 rounded-xl text-white font-bold mb-4 shadow-lg ${message.type === 'success' ? 'bg-emerald-500 shadow-emerald-500/20' : 'bg-rose-500 shadow-rose-500/20'}`}
                    >
                        {message.text}
                    </motion.div>
                )}
            </AnimatePresence>

            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-3xl font-black text-slate-800 dark:text-white tracking-tight flex items-center gap-3">
                        <ShieldCheck className="text-blue-500" size={32} />
                        Foydalanuvchilarni Boshqarish
                    </h1>
                    <p className="text-slate-500 dark:text-slate-400 mt-2">
                        {me.role === 'super_admin' ? 'Tizimdagi barcha foydalanuvchilar va adminlarni nazorat qilish.' : 'Siz yaratgan foydalanuvchilar ro\'yxati.'}
                    </p>
                </div>
                <button
                    onClick={handleOpenCreate}
                    className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-2xl font-black shadow-lg shadow-blue-500/30 transition-all active:scale-95"
                >
                    <UserPlus size={20} /> Yangi Foydalanuvchi
                </button>
            </div>

            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/5 rounded-[40px] shadow-sm overflow-hidden min-h-[400px]">
                {loading ? (
                    <div className="p-20 flex justify-center"><RefreshCw className="animate-spin w-10 h-10 text-blue-500" /></div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-slate-50 dark:bg-white/5 border-b border-slate-200 dark:border-white/5 text-slate-500 dark:text-slate-400 text-[10px] font-black uppercase tracking-[0.15em]">
                                    <th className="p-6">Foydalanuvchi / Login</th>
                                    <th className="p-6">Telefon</th>
                                    <th className="p-6">Roli</th>
                                    <th className="p-6">Paroli</th>
                                    <th className="p-6 text-right">Amallar</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100 dark:divide-white/5">
                                {users.filter(u => u.id !== me.id).map((u, i) => (
                                    <motion.tr
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: i * 0.05 }}
                                        key={u.id}
                                        className="hover:bg-slate-50/50 dark:hover:bg-white/[0.02] transition-colors"
                                    >
                                        <td className="p-6">
                                            <div>
                                                <p className="font-black text-slate-800 dark:text-white">{u.full_name || 'Ismsiz'}</p>
                                                <p className="text-xs text-slate-400 font-mono">@{u.username}</p>
                                            </div>
                                        </td>
                                        <td className="p-6 text-sm text-slate-500 dark:text-slate-400">{u.phone_number || '-'}</td>
                                        <td className="p-6">
                                            <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${
                                                u.role === 'super_admin' ? 'bg-rose-500/10 text-rose-500' : 
                                                u.role === 'admin' ? 'bg-amber-500/10 text-amber-500' : 
                                                'bg-emerald-500/10 text-emerald-500'
                                            }`}>
                                                {u.role === 'super_admin' ? 'Super Admin' : u.role === 'admin' ? 'Admin' : 'Foydalanuvchi'}
                                            </span>
                                        </td>
                                        <td className="p-6">
                                            <code className="px-2 py-1 bg-slate-100 dark:bg-black/40 text-blue-600 dark:text-blue-400 rounded font-mono text-sm border border-slate-200 dark:border-white/10">
                                                {u.last_name || '********'}
                                            </code>
                                        </td>
                                        <td className="p-6 text-right">
                                            <div className="flex justify-end gap-2">
                                                <button onClick={() => handleOpenEdit(u)} className="p-2 text-slate-400 hover:text-blue-500 hover:bg-blue-500/10 rounded-xl transition-all">
                                                    <Edit2 size={18} />
                                                </button>
                                                <button onClick={() => handleDelete(u.id)} className="p-2 text-slate-400 hover:text-rose-500 hover:bg-rose-500/10 rounded-xl transition-all">
                                                    <Trash2 size={18} />
                                                </button>
                                            </div>
                                        </td>
                                    </motion.tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Create/Edit Modal */}
            <AnimatePresence>
                {isModalOpen && (
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.9, y: 20 }}
                            className="bg-white dark:bg-slate-900 rounded-[40px] shadow-2xl w-full max-w-lg overflow-hidden border border-slate-200 dark:border-white/10"
                        >
                            <div className="p-8 border-b border-slate-100 dark:border-white/5 bg-slate-50 dark:bg-white/[0.02]">
                                <h3 className="text-2xl font-black text-slate-800 dark:text-white">{editingUser ? "Tahrirlash" : "Yangi Foydalanuvchi"}</h3>
                                <p className="text-slate-500 text-sm mt-1">Ma'lumotlarni kiriting va saqlash tugmasini bosing.</p>
                            </div>

                            <form onSubmit={handleSubmit} className="p-8 space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="col-span-2">
                                        <label className="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 ml-1">F.I.SH.</label>
                                        <input
                                            type="text"
                                            required
                                            value={formData.full_name}
                                            onChange={e => setFormData({...formData, full_name: e.target.value})}
                                            className="w-full px-5 py-4 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-2xl focus:border-blue-500 outline-none transition-all text-slate-800 dark:text-white font-bold"
                                            placeholder="Masalan: Eshonov Nodirbek"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 ml-1">Username (Login)</label>
                                        <input
                                            type="text"
                                            required
                                            value={formData.username}
                                            onChange={e => setFormData({...formData, username: e.target.value})}
                                            className="w-full px-5 py-4 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-2xl focus:border-blue-500 outline-none transition-all text-slate-800 dark:text-white font-bold"
                                            placeholder="nodir_99"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 ml-1">Telefon</label>
                                        <input
                                            type="text"
                                            value={formData.phone_number}
                                            onChange={e => setFormData({...formData, phone_number: e.target.value})}
                                            className="w-full px-5 py-4 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-2xl focus:border-blue-500 outline-none transition-all text-slate-800 dark:text-white font-bold"
                                            placeholder="+998901234567"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 ml-1">Roli</label>
                                        <select
                                            value={formData.role}
                                            onChange={e => setFormData({...formData, role: e.target.value})}
                                            className="w-full px-5 py-4 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-2xl focus:border-blue-500 outline-none transition-all text-slate-800 dark:text-white font-bold appearance-none"
                                        >
                                            <option value="user">Foydalanuvchi</option>
                                            {me.role === 'super_admin' && <option value="admin">Admin</option>}
                                            {me.role === 'super_admin' && <option value="super_admin">Super Admin</option>}
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 ml-1">Parol</label>
                                        <input
                                            type="text"
                                            required={!editingUser}
                                            value={formData.password}
                                            onChange={e => setFormData({...formData, password: e.target.value})}
                                            className="w-full px-5 py-4 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-2xl focus:border-blue-500 outline-none transition-all text-slate-800 dark:text-white font-bold"
                                            placeholder={editingUser ? "O'zgartirmaslik uchun bo'sh qoldiring" : "Kamida 6 ta belgi"}
                                        />
                                    </div>
                                </div>

                                <div className="flex gap-4 pt-6">
                                    <button
                                        type="button"
                                        onClick={() => setIsModalOpen(false)}
                                        className="flex-1 py-4 px-6 bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-slate-400 rounded-2xl font-black transition-all"
                                    >
                                        Bekor qilish
                                    </button>
                                    <button
                                        type="submit"
                                        disabled={submitting}
                                        className="flex-3 py-4 px-10 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl font-black shadow-lg shadow-blue-500/30 transition-all disabled:opacity-50"
                                    >
                                        {submitting ? "Saqlanmoqda..." : editingUser ? "Yangilash" : "Yaratish"}
                                    </button>
                                </div>
                            </form>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
}
