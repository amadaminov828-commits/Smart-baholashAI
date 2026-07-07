"use client";

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Database, Search, Filter, Eye, ExternalLink, Trash2, Calendar, DollarSign, MapPin, Car, HelpCircle } from 'lucide-react';
import { api } from '@/services/api';
import { useTranslation } from '@/i18n/I18nProvider';
import { Navbar } from '@/components/Navbar';

interface Analog {
  id: number;
  source: string;
  model_name: string;
  year: number;
  engine_capacity: string;
  mileage: string;
  price: string;
  price_string: string;
  location: string;
  url: string;
  created_at: string;
}

export default function AnalogsPage() {
  const { t } = useTranslation();
  const [analogs, setAnalogs] = useState<Analog[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sourceFilter, setSourceFilter] = useState('all');

  useEffect(() => {
    fetchAnalogs();
  }, []);

  const fetchAnalogs = async () => {
    try {
      const res = await api.get('vehicles/global-analogs/');
      setAnalogs(res.data);
    } catch (err) {
      console.error("Global analogs fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Haqiqatdan ham ushbu analog ma'lumotni bazadan o'chirmoqchimisiz?")) return;
    try {
      await api.delete(`vehicles/global-analogs/${id}/`);
      setAnalogs(analogs.filter(a => a.id !== id));
    } catch (err) {
      console.error("Delete analog error:", err);
      alert("O'chirishda xatolik yuz berdi");
    }
  };

  const filteredAnalogs = analogs.filter(a => {
    const matchesSearch = 
      a.model_name.toLowerCase().includes(search.toLowerCase()) ||
      (a.location && a.location.toLowerCase().includes(search.toLowerCase()));
    const matchesSource = sourceFilter === 'all' || a.source.toLowerCase().includes(sourceFilter.toLowerCase());
    return matchesSearch && matchesSource;
  });

  return (
    <div className="min-h-screen bg-[#0a0f1c] text-white">
      <Navbar />

      <main className="max-w-7xl mx-auto px-6 py-12">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-12">
          <div>
            <h1 className="text-4xl font-black tracking-tighter mb-2 bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent uppercase flex items-center gap-3">
              <Database className="text-blue-400" size={36} />
              Analoglar Bazasi
            </h1>
            <p className="text-slate-400 font-medium">Bozordan sun'iy intellekt tomonidan baholash uchun to'plangan o'xshash avtovositlar ro'yxati</p>
          </div>

          <div className="flex items-center gap-3 w-full md:w-auto">
            <div className="relative flex-1 md:w-80">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
              <input 
                type="text" 
                placeholder="Model yoki manzil bo'yicha qidirish..." 
                className="w-full bg-white/5 border border-white/10 rounded-2xl py-3.5 pl-12 pr-4 text-sm focus:border-blue-500 outline-none transition-all"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-3 mb-10 overflow-x-auto pb-2 scrollbar-none">
          {[
            { id: 'all', name: 'Barchasi' },
            { id: 'olx', name: 'OLX.uz' },
            { id: 'avtoelon', name: 'Avtoelon.uz' },
            { id: 'manual', name: 'Qo\'lda kiritilgan' }
          ].map((src) => (
            <button
              key={src.id}
              onClick={() => setSourceFilter(src.id)}
              className={`px-6 py-2.5 rounded-full text-xs font-black uppercase tracking-widest transition-all border ${
                sourceFilter === src.id 
                  ? 'bg-blue-600 border-blue-500 shadow-lg shadow-blue-600/20' 
                  : 'bg-white/5 border-white/10 text-slate-400 hover:bg-white/10'
              }`}
            >
              {src.name}
            </button>
          ))}
        </div>

        {/* Analogs Table */}
        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="h-16 w-full bg-white/5 rounded-2xl animate-pulse"></div>
            ))}
          </div>
        ) : filteredAnalogs.length === 0 ? (
          <div className="text-center py-24 text-slate-600">
            <Car size={64} className="mx-auto mb-4 opacity-20" />
            <p className="font-bold text-lg">Hech qanday analog ma'lumot topilmadi</p>
            <p className="text-sm mt-2">Damas yoki Cobalt kabi avtomobillarni baholaganingizda, bu yerda o'xshash analoglar to'planadi.</p>
          </div>
        ) : (
          <div className="bg-white/5 border border-white/5 rounded-[30px] overflow-hidden shadow-2xl backdrop-blur-md">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-white/5 bg-white/[0.02]">
                    <th className="p-5 text-[10px] font-black uppercase tracking-wider text-slate-400">Avtomobil modeli</th>
                    <th className="p-5 text-[10px] font-black uppercase tracking-wider text-slate-400">Yili</th>
                    <th className="p-5 text-[10px] font-black uppercase tracking-wider text-slate-400">Dvigatel hajmi</th>
                    <th className="p-5 text-[10px] font-black uppercase tracking-wider text-slate-400">Bosgan masofasi</th>
                    <th className="p-5 text-[10px] font-black uppercase tracking-wider text-slate-400">Narxi</th>
                    <th className="p-5 text-[10px] font-black uppercase tracking-wider text-slate-400">Manba</th>
                    <th className="p-5 text-[10px] font-black uppercase tracking-wider text-slate-400">Joylashuv</th>
                    <th className="p-5 text-[10px] font-black uppercase tracking-wider text-slate-400 text-center">Amallar</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredAnalogs.map((analog) => (
                    <tr key={analog.id} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                      <td className="p-5 font-bold flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400">
                          <Car size={16} />
                        </div>
                        {analog.model_name}
                      </td>
                      <td className="p-5 font-medium text-slate-300">
                        <span className="flex items-center gap-1.5 text-xs">
                          <Calendar size={14} className="text-slate-500" />
                          {analog.year}-yil
                        </span>
                      </td>
                      <td className="p-5 text-sm font-semibold text-slate-400">{analog.engine_capacity || "Noma'lum"}</td>
                      <td className="p-5 text-sm font-semibold text-slate-400">{analog.mileage || "Noma'lum"}</td>
                      <td className="p-5 text-emerald-400 font-bold">
                        <span className="flex items-center gap-0.5 text-xs">
                          <DollarSign size={14} />
                          {parseFloat(analog.price).toLocaleString()} USD
                        </span>
                      </td>
                      <td className="p-5">
                        <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${
                          analog.source.toLowerCase().includes('olx') ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' :
                          analog.source.toLowerCase().includes('avtoelon') ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                          'bg-purple-500/10 text-purple-400 border border-purple-500/20'
                        }`}>
                          {analog.source}
                        </span>
                      </td>
                      <td className="p-5 text-slate-400 text-xs">
                        <span className="flex items-center gap-1.5">
                          <MapPin size={14} className="text-slate-500" />
                          {analog.location || "Noma'lum"}
                        </span>
                      </td>
                      <td className="p-5 text-center">
                        <div className="flex items-center justify-center gap-2">
                          {analog.url && (
                            <a 
                              href={analog.url} 
                              target="_blank" 
                              rel="noopener noreferrer" 
                              className="p-2 bg-white/5 hover:bg-white/10 rounded-lg text-slate-300 hover:text-white transition-all"
                              title="Asl e'lonni ko'rish"
                            >
                              <ExternalLink size={16} />
                            </a>
                          )}
                          <button 
                            onClick={() => handleDelete(analog.id)}
                            className="p-2 bg-red-500/10 hover:bg-red-500 hover:text-white border border-red-500/20 text-red-400 rounded-lg transition-all"
                            title="O'chirish"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
