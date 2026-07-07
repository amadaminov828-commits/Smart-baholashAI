"use client";

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
    TrendingUp, TrendingDown, Users, Car, Building,
    MapPin, Calendar, ArrowUpRight, BarChart3,
    ChevronRight, Search, Filter, Globe, X,
    ArrowRight, Tag, Info, Download, History,
    LayoutGrid, List as ListIcon
} from 'lucide-react';
import { api } from '@/services/api';
import { useTranslation } from '@/i18n/I18nProvider';
import { useRouter } from 'next/navigation';

export default function StatisticsPage() {
    const router = useRouter();
    const { t, lang } = useTranslation();
    const [activeTab, setActiveTab] = useState<'vehicles' | 'real_estate'>('vehicles');
    const [selectedRegion, setSelectedRegion] = useState('Barchasi');
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedDetail, setSelectedDetail] = useState<{ type: 'region' | 'category' | 'listings' | 'archive', value: any } | null>(null);
    const [viewMode, setViewMode] = useState<'overview' | 'detailed'>('overview');
    const [listFilter, setListFilter] = useState<'all' | 'new'>('all');

    const [loadingRegion, setLoadingRegion] = useState(false);

    const fetchRegionData = async (region: string) => {
        setLoadingRegion(true);
        try {
            const endpoint = activeTab === 'vehicles' ? 'statistics/vehicles/' : 'statistics/real_estate/';
            const res = await api.get(`${endpoint}?region=${encodeURIComponent(region)}&lang=${lang}`);
            // Update the selected detail with fresh data from backend
            setSelectedDetail(prev => {
                if (!prev) return null;
                return { ...prev, value: { ...prev.value, items: res.data.new_listings_details } };
            });
        } catch (err) {
            console.error("Region fetch error", err);
        } finally {
            setLoadingRegion(false);
        }
    };

    const handleRegionClick = (reg: any) => {
        setSelectedDetail({ type: 'region', value: reg });
        fetchRegionData(reg.name);
    };

    const handleDownloadPDF = (title: string) => {
        const jsPdfScript = document.createElement('script');
        jsPdfScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';

        const autoTableScript = document.createElement('script');
        autoTableScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.28/jspdf.plugin.autotable.min.js';

        jsPdfScript.onload = () => {
            document.head.appendChild(autoTableScript);
        };

        autoTableScript.onload = () => {
            try {
                const { jsPDF } = (window as any).jspdf;
                const doc = new jsPDF();

                // Add Logo/Header
                doc.setFillColor(30, 41, 59); // Slate-800
                doc.rect(0, 0, 210, 40, 'F');

                doc.setFontSize(24);
                doc.setTextColor(255, 255, 255);
                doc.text(t.stats.pdf.report_title, 20, 25);

                doc.setFontSize(10);
                doc.text(`${t.stats.pdf.date}: ${new Date().toLocaleDateString(lang === 'uz' ? 'uz-UZ' : 'en-US')} | ${t.stats.pdf.platform}`, 20, 33);

                // Section 1: Overview
                doc.setFontSize(16);
                doc.setTextColor(30, 41, 59);
                doc.text(t.stats.pdf.section_1, 20, 55);

                (doc as any).autoTable({
                    startY: 60,
                    head: [[t.stats.pdf.table_header_indicator, t.stats.pdf.table_header_value]],
                    body: [
                        [t.stats.pdf.avg_price, stats?.avg_price || stats?.avg_price_m2 || 'N/A'],
                        [t.stats.pdf.listings_weekly, stats?.new_listings || 'N/A'],
                        [t.stats.pdf.demand_index, `${stats?.demand_index || 0}%`],
                        [t.stats.pdf.main_segment, activeTab === 'vehicles' ? t.stats.pdf.vehicles : t.stats.pdf.real_estate]
                    ],
                    theme: 'striped',
                    headStyles: { fillColor: [37, 99, 235] }
                });

                // Section 2: Model/Type Trends
                const nextY = (doc as any).lastAutoTable.finalY + 20;
                doc.text(t.stats.pdf.section_2.replace('{type}', activeTab === 'vehicles' ? t.stats.pdf.vehicles : t.stats.pdf.real_estate), 20, nextY);

                const modelData = (activeTab === 'vehicles' ? stats?.top_models : stats?.top_types) || [];
                (doc as any).autoTable({
                    startY: nextY + 5,
                    head: [[activeTab === 'vehicles' ? t.stats.pdf.model_name : t.stats.pdf.type_name, t.stats.pdf.count, t.stats.pdf.trend]],
                    body: modelData.map((m: any) => [m.name, m.count, m.trend]),
                    theme: 'grid',
                    headStyles: { fillColor: [15, 23, 42] }
                });

                // Section 3: Regional Distribution
                const regionY = (doc as any).lastAutoTable.finalY + 20;
                doc.text(t.stats.pdf.section_3, 20, regionY);

                const regionData = stats?.regions || [];
                (doc as any).autoTable({
                    startY: regionY + 5,
                    head: [[t.stats.pdf.region_name, t.stats.pdf.total_ads, t.stats.pdf.weekly_change]],
                    body: regionData.map((r: any) => [r.name, r.count, r.weekly_change]),
                    theme: 'striped',
                    headStyles: { fillColor: [51, 65, 85] }
                });

                // Section 4: Descriptive Analysis
                const analysisY = (doc as any).lastAutoTable.finalY + 20;
                if (analysisY < 250) {
                    doc.text(t.stats.pdf.section_4, 20, analysisY);
                    doc.setFontSize(10);
                    doc.setTextColor(71, 85, 105);
                    const splitText = doc.splitTextToSize(
                        t.stats.pdf.analysis_desc
                            .replace('{type}', activeTab === 'vehicles' ? t.stats.pdf.vehicles.toLowerCase() : t.stats.pdf.real_estate.toLowerCase())
                            .replace('{trend}', (stats?.demand_index || 0) + '%'),
                        170
                    );
                    doc.text(splitText, 20, analysisY + 10);
                }

                // Footer
                const pageCount = (doc as any).internal.getNumberOfPages();
                for (let i = 1; i <= pageCount; i++) {
                    doc.setPage(i);
                    doc.setFontSize(8);
                    doc.setTextColor(148, 163, 184);
                    doc.text(`${t.stats.pdf.platform} - ${t.stats.pdf.report_title} | ${t.stats.pdf.date}: ${new Date().toLocaleDateString(lang === 'uz' ? 'uz-UZ' : 'en-US')}`, 105, 285, { align: 'center' });
                }

                doc.save(`${title.replace(/\s+/g, '_')}_Full_Report.pdf`);
            } catch (err) {
                console.error("PDF Professional error:", err);
            }
        };
        document.head.appendChild(jsPdfScript);
    };

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await api.get(`statistics/general/?lang=${lang}`);
            setData(res.data);
        } catch (err: any) {
            console.error("Stats fetch error:", err);
            setError(err.message || "Backend serverga ulanishda xatolik yuz berdi. Iltimos, backend server ishlayotganini tekshiring.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [lang]);

    const stats = activeTab === 'vehicles' ? data?.vehicles : data?.real_estate;

    if (loading) {
        return (
            <div className="min-h-screen bg-[#0a0f1c] flex items-center justify-center">
                <div className="w-16 h-16 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-[#0a0f1c] flex flex-col items-center justify-center p-6 text-center">
                <div className="w-20 h-20 bg-red-500/10 text-red-500 rounded-full flex items-center justify-center mb-8 border border-red-500/20">
                    <TrendingDown size={40} />
                </div>
                <h2 className="text-3xl font-black text-white mb-4 uppercase tracking-tighter">{t.login_error.split('.')[0]}</h2>
                <p className="text-slate-400 max-w-md mb-10 font-medium">
                    {error} <br />
                    Backend server (port 8000) offline.
                </p>
                <button
                    onClick={fetchData}
                    className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-black rounded-2xl transition-all shadow-xl shadow-blue-500/20 active:scale-95 uppercase tracking-widest text-xs"
                >
                    {t.login_btn}
                </button>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#0a0f1c] text-white pt-6 pb-20 relative overflow-hidden">
            {/* Background Neural Decorations */}
            <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-600/10 blur-[120px] rounded-full pointer-events-none"></div>
            <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-purple-600/5 blur-[120px] rounded-full pointer-events-none"></div>

            {/* Header */}
            <header className="relative z-50 max-w-7xl mx-auto px-6 mb-12 flex justify-between items-center bg-slate-900/40 backdrop-blur-xl border border-white/5 py-4 rounded-3xl">
                <div className="flex items-center gap-4">
                    <a href="/" className="text-2xl font-black bg-gradient-to-r from-white via-blue-200 to-blue-500 bg-clip-text text-transparent tracking-tighter hover:opacity-80 transition-opacity">
                        Smart Baholash
                    </a>
                </div>

                <div className="flex items-center gap-6">
                    <nav className="hidden md:flex items-center gap-6 mr-4">
                        <a href="/" className="text-sm font-bold text-slate-400 hover:text-white transition-colors">{t.nav?.home || 'Bosh sahifa'}</a>
                    </nav>

                    {/* Language Switcher Component */}
                    <div className="bg-white/5 border border-white/10 rounded-xl px-2 py-1 flex items-center">
                        <Globe size={16} className="text-slate-400 mr-2" />
                        <select
                            value={lang}
                            onChange={(e) => {
                                // Assuming setLanguage or similar is passed from useTranslation, or handled by a router push
                                // Since we don't have setLanguage exposed in useTranslation here, we use a simple window reload for now with the query param
                                const newLang = e.target.value;
                                localStorage.setItem('lang', newLang);
                                window.location.search = `?lang=${newLang}`;
                            }}
                            className="bg-transparent text-sm font-bold text-white outline-none cursor-pointer appearance-none uppercase"
                        >
                            <option value="uz" className="bg-slate-900">UZ</option>
                            <option value="ru" className="bg-slate-900">RU</option>
                            <option value="kk" className="bg-slate-900">KK</option>
                            <option value="en" className="bg-slate-900">EN</option>
                        </select>
                    </div>
                </div>
            </header>

            {/* Details Modal */}
            {selectedDetail && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 pb-20">
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        onClick={() => setSelectedDetail(null)}
                        className="absolute inset-0 bg-slate-950/80 backdrop-blur-md"
                    ></motion.div>

                    <motion.div
                        initial={{ opacity: 0, scale: 0.9, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        className={`relative w-full ${viewMode === 'detailed' ? 'max-w-6xl h-[85vh]' : 'max-w-2xl'} bg-slate-900/90 border border-white/10 rounded-[40px] shadow-3xl overflow-hidden p-8 md:p-12 transition-all duration-500 flex flex-col`}
                    >
                        <button
                            onClick={() => setSelectedDetail(null)}
                            className="absolute top-6 right-6 p-2 bg-white/5 hover:bg-white/10 rounded-full transition-colors"
                        >
                            <X size={20} />
                        </button>

                        <div className="mb-10 flex justify-between items-start">
                            <div>
                                <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-blue-500/10 text-blue-400 rounded-full text-[10px] font-black uppercase tracking-widest border border-blue-500/20 mb-6 font-sans">
                                    {selectedDetail.type === 'region' ? t.stats.region_analysis : selectedDetail.type === 'category' ? t.stats.category_analysis : t.stats.new_listings_title}
                                </div>
                                <h2 className="text-4xl font-black tracking-tighter text-white uppercase italic">
                                    {(typeof selectedDetail.value === 'string')
                                        ? selectedDetail.value
                                        : (selectedDetail.value?.name || selectedDetail.value?.title || (selectedDetail.type === 'listings' ? t.stats.new_listings_title : selectedDetail.type))}
                                </h2>
                            </div>

                            {selectedDetail.type !== 'listings' && (
                                <div className="flex bg-white/5 p-1 rounded-xl border border-white/5">
                                    <button
                                        onClick={() => setViewMode('overview')}
                                        className={`p-2 rounded-lg transition-all ${viewMode === 'overview' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-500 hover:text-white'}`}
                                    >
                                        <LayoutGrid size={16} />
                                    </button>
                                    <button
                                        onClick={() => setViewMode('detailed')}
                                        className={`p-2 rounded-lg transition-all ${viewMode === 'detailed' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-500 hover:text-white'}`}
                                    >
                                        <ListIcon size={16} />
                                    </button>
                                </div>
                            )}
                        </div>

                        <div className="flex-1 overflow-y-auto pr-4 custom-scrollbar space-y-8">
                            {selectedDetail.type === 'region' && (
                                <>
                                    {viewMode === 'overview' ? (
                                        <>
                                            <div className="grid grid-cols-2 gap-6">
                                                <motion.div
                                                    whileHover={{ scale: 1.02, backgroundColor: "rgba(255,255,255,0.08)" }}
                                                    whileTap={{ scale: 0.98 }}
                                                    onClick={() => { setListFilter('all'); setViewMode('detailed'); }}
                                                    className="p-6 bg-white/5 rounded-3xl border border-white/5 cursor-pointer transition-colors"
                                                >
                                                    <p className="text-slate-500 text-[10px] font-black uppercase tracking-wider mb-2 font-sans">{t.stats.total_listings}</p>
                                                    <p className="text-3xl font-black text-white">{selectedDetail.value.count}</p>
                                                    <div className="mt-4 flex items-center gap-2 text-[10px] font-bold text-blue-400 uppercase tracking-tighter">
                                                        {t.stats.view_list} <ArrowUpRight size={12} />
                                                    </div>
                                                </motion.div>
                                                <motion.div
                                                    whileHover={{ scale: 1.02, backgroundColor: "rgba(255,255,255,0.08)" }}
                                                    whileTap={{ scale: 0.98 }}
                                                    onClick={() => { setListFilter('new'); setViewMode('detailed'); }}
                                                    className="p-6 bg-white/5 rounded-3xl border border-white/5 cursor-pointer transition-colors"
                                                >
                                                    <p className="text-slate-500 text-[10px] font-black uppercase tracking-wider mb-2 font-sans">{t.stats.weekly_change}</p>
                                                    <p className="text-3xl font-black text-emerald-400">{selectedDetail.value.weekly_change}</p>
                                                    <div className="mt-4 flex items-center gap-2 text-[10px] font-bold text-emerald-400 uppercase tracking-tighter">
                                                        {t.stats.view_new} <ArrowUpRight size={12} />
                                                    </div>
                                                </motion.div>
                                            </div>
                                            <div className="p-8 bg-blue-600/10 rounded-3xl border border-blue-500/20">
                                                <h4 className="font-bold mb-4 flex items-center gap-2 text-blue-300">
                                                    <Info size={16} /> {t.stats.region_analysis}
                                                </h4>
                                                <p className="text-slate-400 text-sm leading-relaxed">
                                                    {selectedDetail.value.name} {activeTab === 'vehicles' ? t.stats.conclusion_vehicles : t.stats.conclusion_real_estate}
                                                </p>
                                            </div>
                                        </>
                                    ) : (
                                        <div className="space-y-4">
                                            <div className="flex justify-between items-end mb-6">
                                                <h4 className="text-[10px] font-black uppercase tracking-widest text-slate-500 font-sans">
                                                    {listFilter === 'all' ? `${t.stats.total_listings} (${selectedDetail.value.count})` : `${t.stats.new_listings_title} (${selectedDetail.value.weekly_change})`}
                                                </h4>
                                                <div className="flex gap-2">
                                                    <button onClick={() => setListFilter('all')} className={`px-3 py-1 text-[10px] font-black rounded-lg border transition-all ${listFilter === 'all' ? 'bg-blue-600 border-blue-600 text-white' : 'border-white/10 text-slate-500'}`}>{t.stats.all_filter}</button>
                                                    <button onClick={() => setListFilter('new')} className={`px-3 py-1 text-[10px] font-black rounded-lg border transition-all ${listFilter === 'new' ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-white/10 text-slate-500'}`}>{t.stats.new_filter}</button>
                                                </div>
                                            </div>
                                            <div className="grid md:grid-cols-2 gap-4">
                                                {loadingRegion ? (
                                                    <div className="col-span-2 py-20 flex flex-col items-center justify-center text-slate-500">
                                                        <div className="w-10 h-10 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin mb-4"></div>
                                                        <p className="text-xs font-bold animate-pulse uppercase tracking-widest">Real ma'lumotlar yuklanmoqda...</p>
                                                    </div>
                                                ) : (() => {
                                                    const allListings = selectedDetail.value.items || data?.[activeTab]?.new_listings_details || [];
                                                    const filteredListings = allListings.filter((item: any) => {
                                                        if (selectedDetail.type === 'region') {
                                                            return item.region.toLowerCase().includes(selectedDetail.value.name.toLowerCase()) || 
                                                                   selectedDetail.value.name.toLowerCase().includes(item.region.toLowerCase());
                                                        }
                                                        return true;
                                                    });

                                                    // Use filtered if available, otherwise show all as "Market Fallback"
                                                    const listingsToDisplay = filteredListings.length > 0 ? filteredListings : allListings.slice(0, 15);
                                                    const isFallback = filteredListings.length === 0 && allListings.length > 0;

                                                    return (
                                                        <>
                                                            {isFallback && (
                                                                <div className="col-span-2 p-4 bg-amber-500/10 border border-amber-500/20 rounded-2xl mb-4 text-amber-400 text-[10px] font-black uppercase tracking-widest flex items-center gap-2">
                                                                    <Info size={14} /> Ushbu hudud bo'yicha kam ma'lumot topildi. Umumiy bozor tahlili ko'rsatilmoqda.
                                                                </div>
                                                            )}
                                                            
                                                {listingsToDisplay.map((list: any, idx: number) => (
                                                    <motion.div
                                                        key={idx}
                                                        onClick={() => {
                                                            const path = activeTab === 'vehicles' ? '/vehicles' : '/real-estate';
                                                            router.push(`${path}?import_url=${encodeURIComponent(list.url)}`);
                                                        }}
                                                        initial={{ opacity: 0, y: 10 }}
                                                        animate={{ opacity: 1, y: 0 }}
                                                        transition={{ delay: (idx % 10) * 0.05 }}
                                                        className="p-6 bg-white/5 rounded-[30px] border border-white/5 flex justify-between items-center group hover:bg-blue-600/10 transition-all hover:border-blue-500/30 cursor-pointer"
                                                    >
                                                        <div className="flex items-center gap-4">
                                                            <div className="w-12 h-12 bg-white/5 rounded-2xl flex items-center justify-center text-slate-500 group-hover:text-blue-400 transition-colors">
                                                                {activeTab === 'vehicles' ? <Car size={20} /> : <Building size={20} />}
                                                            </div>
                                                            <div>
                                                                <p className="font-bold text-white group-hover:text-blue-400 transition-colors">
                                                                    {list.title}
                                                                </p>
                                                                <p className="text-[10px] text-slate-500 uppercase tracking-widest mt-1 flex items-center gap-2">
                                                                    <MapPin size={10} /> {isFallback ? `${selectedDetail.value.name} (Bozor)` : list.region} <span className="text-white/10">|</span> {list.date}
                                                                </p>
                                                            </div>
                                                        </div>
                                                        <div className="text-right">
                                                            <p className="text-xl font-black text-blue-400 tabular-nums">{list.price}</p>
                                                            <div className="mt-1 flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                                                <span className="text-[8px] font-black text-blue-400 uppercase">Baholashni boshlash</span>
                                                                <ArrowRight size={10} className="text-blue-400" />
                                                            </div>
                                                        </div>
                                                    </motion.div>
                                                ))}

                                                            {listingsToDisplay.length === 0 && (
                                                                <div className="col-span-2 py-20 text-center text-slate-600">
                                                                    <Info size={48} className="mx-auto mb-4 opacity-20" />
                                                                    <p>Hozircha hech qanday real e'lonlar topilmadi.</p>
                                                                </div>
                                                            )}
                                                        </>
                                                    );
                                                })()}
                                            </div>
                                        </div>
                                    )}
                                </>
                            )}

                            {selectedDetail.type === 'category' && (
                                <>
                                    {data?.[activeTab]?.category_details?.[selectedDetail.value] ? (
                                        <>
                                            {viewMode === 'overview' ? (
                                                <>
                                                    <div className="p-8 bg-indigo-600/10 rounded-3xl border border-indigo-500/20">
                                                        <h4 className="font-bold mb-4 text-indigo-300">Haftalik Tahlil</h4>
                                                        <p className="text-slate-300 text-sm leading-relaxed italic">
                                                            "{data[activeTab].category_details[selectedDetail.value].weekly_analysis}"
                                                        </p>
                                                    </div>
                                                    <div>
                                                        <h4 className="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-4 font-sans">Ommabop turlar</h4>
                                                        <div className="flex flex-wrap gap-2">
                                                            {data[activeTab].category_details[selectedDetail.value].top_types?.map((type: string, i: number) => (
                                                                <span key={i} className="px-3 py-1.5 bg-white/5 border border-white/5 rounded-lg text-xs font-bold">{type}</span>
                                                            )) || data[activeTab].category_details[selectedDetail.value].top_models?.map((model: string, i: number) => (
                                                                <span key={i} className="px-3 py-1.5 bg-white/5 border border-white/5 rounded-lg text-xs font-bold">{model}</span>
                                                            ))}
                                                        </div>
                                                    </div>
                                                </>
                                            ) : (
                                                <div className="space-y-4">
                                                    <h4 className="text-[10px] font-black uppercase tracking-widest text-slate-500 font-sans">Kategoriyadagi yangi e'lonlar</h4>
                                                    {data[activeTab].category_details[selectedDetail.value].recent_listings.map((item: any, i: number) => (
                                                        <div key={i} className="p-5 bg-white/5 rounded-3xl border border-white/5 flex justify-between items-center hover:bg-white/10 transition-all group">
                                                            <div>
                                                                <p className="font-bold text-white group-hover:text-blue-400 transition-colors">
                                                                    {typeof item === 'string' ? item : (item.title || 'Noma\'lum')}
                                                                </p>
                                                                <p className="text-[10px] text-slate-500 uppercase tracking-widest mt-1">{item.region || 'Barcha hududlar'} <span className="text-white/10 mx-1">/</span> {item.time || 'Bugun'}</p>
                                                            </div>
                                                            <p className="text-xl font-black text-blue-400">{item.price}</p>
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </>
                                    ) : (
                                        <p className="text-slate-500 italic text-center py-10">{t.stats.loading_details}</p>
                                    )}
                                </>
                            )}

                            {selectedDetail.type === 'listings' && (
                                <div className="grid md:grid-cols-2 gap-4">
                                    {(selectedDetail.value || []).map((item: any, i: number) => (
                                        <motion.a
                                            key={i}
                                            href={item.url || "#"}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: (i % 12) * 0.04 }}
                                            className="group p-6 bg-white/5 rounded-3xl border border-white/5 hover:bg-white/10 transition-all flex justify-between items-center hover:border-blue-500/30 cursor-pointer"
                                        >
                                            <div className="flex items-center gap-4">
                                                <div className="w-12 h-12 bg-white/5 rounded-2xl flex items-center justify-center text-slate-500 group-hover:text-blue-400 transition-colors">
                                                    {activeTab === 'vehicles' ? <Car size={20} /> : <Building size={20} />}
                                                </div>
                                                <div>
                                                    <p className="text-lg font-black text-white group-hover:text-blue-400 transition-colors">
                                                        {item.title}
                                                    </p>
                                                    <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest mt-1 flex items-center gap-2">
                                                        <MapPin size={10} /> {item.region} <span className="text-white/10">|</span> {item.date}
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="text-right font-black text-2xl text-blue-400 tabular-nums">
                                                {item.price}
                                            </div>
                                        </motion.a>
                                    ))}
                                    
                                    {(selectedDetail.value || []).length === 0 && (
                                        <div className="col-span-2 py-20 text-center text-slate-600">
                                            <Info size={48} className="mx-auto mb-4 opacity-20" />
                                            <p>Yangi e'lonlar topilmadi.</p>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>

                        <div className="mt-12 flex gap-4">
                            <button
                                onClick={() => setViewMode(viewMode === 'overview' ? 'detailed' : 'overview')}
                                className="flex-1 py-4 bg-blue-600 text-white rounded-2xl font-black uppercase text-xs tracking-widest shadow-xl shadow-blue-500/20 active:scale-95 transition-all flex items-center justify-center gap-3"
                            >
                                {viewMode === 'overview' ? <><ListIcon size={16} /> To'liq ma'lumotlarni ko'rish</> : <><LayoutGrid size={16} /> Umumiy ko'rinishga qaytish</>}
                            </button>
                        </div>
                    </motion.div>
                </div>
            )}

            <div className="max-w-7xl mx-auto px-6 relative z-10">
                {/* Header */}
                <div className="flex flex-col md:flex-row justify-between items-end gap-6 mb-12">
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                    >
                        <h1 className="text-5xl font-black tracking-tighter mb-4 bg-gradient-to-r from-white via-blue-100 to-blue-400 bg-clip-text text-transparent">
                            {t.stats.title.split(' / ')[0]} <span className="text-white/20">/</span> {t.stats.title.split(' / ')[1]}
                        </h1>
                        <p className="text-slate-400 font-medium max-w-xl">
                            {t.stats.desc}
                        </p>
                    </motion.div>

                    <div className="flex bg-slate-900/40 backdrop-blur-xl p-1.5 rounded-[20px] border border-white/5">
                        <button
                            onClick={() => setActiveTab('vehicles')}
                            className={`px-8 py-3 rounded-[15px] font-black uppercase tracking-widest text-xs transition-all ${activeTab === 'vehicles' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-500 hover:text-white'}`}
                        >
                            {t.stats.vehicles}
                        </button>
                        <button
                            onClick={() => setActiveTab('real_estate')}
                            className={`px-8 py-3 rounded-[15px] font-black uppercase tracking-widest text-xs transition-all ${activeTab === 'real_estate' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-500 hover:text-white'}`}
                        >
                            {t.stats.real_estate}
                        </button>
                    </div>
                </div>

                {/* Global Stats Bar */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
                    {[
                        { label: t.stats.avg_price, value: `${stats?.avg_price || stats?.avg_price_m2 || 0}${activeTab === 'vehicles' ? ' USD' : ' $/m2'}`, icon: BarChart3, color: "text-blue-400", type: 'price' },
                        { label: t.stats.new_listings_month, value: stats?.new_listings || 0, icon: Calendar, color: "text-emerald-400", type: 'listings' },
                        { label: t.stats.demand_index, value: `${stats?.demand_index || 0}%`, icon: TrendingUp, color: "text-amber-400", type: 'demand' },
                        { label: t.stats.regions_count, value: stats?.regions?.length || 0, icon: MapPin, color: "text-purple-400", type: 'regions' },
                    ].map((item, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.1 }}
                            onClick={() => {
                                if (item.type === 'listings') {
                                    setSelectedDetail({ type: 'listings', value: stats?.new_listings_details || [] });
                                    setViewMode('detailed');
                                    setListFilter('new');
                                } else if (item.type === 'regions') {
                                    // Optionally could scroll to regions or open something else
                                }
                            }}
                            className={`bg-slate-900/60 backdrop-blur-md rounded-[30px] p-6 border border-white/5 transition-all ${item.type === 'listings' ? 'cursor-pointer hover:bg-blue-600/10 hover:border-blue-500/30' : ''}`}
                        >
                            <div className="flex justify-between items-start mb-4">
                                <div className={`p-3 rounded-2xl bg-white/5 ${item.color}`}>
                                    <item.icon size={24} />
                                </div>
                                <span className="text-[10px] font-black text-slate-600 uppercase tracking-widest">Live</span>
                            </div>
                            <p className="text-slate-500 font-bold text-xs uppercase tracking-wider mb-1 font-sans">{item.label}</p>
                            <h4 className="text-2xl font-black text-white italic">{item.value}</h4>
                        </motion.div>
                    ))}
                </div>

                <div className="grid lg:grid-cols-3 gap-8">
                    {/* Main Chart / List Area */}
                    <div className="lg:col-span-2 space-y-8">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="bg-slate-900/60 backdrop-blur-md rounded-[40px] p-8 border border-white/5 min-h-[400px] relative overflow-hidden"
                        >
                            <div className="flex justify-between items-center mb-10">
                                <h3 className="text-xl font-black tracking-tight uppercase">
                                    {t.stats.see_all.split(' ')[0]} {activeTab === 'vehicles' ? t.stats.top_models : t.stats.top_types}
                                </h3>
                                <div className="flex gap-2">
                                    <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                                    <div className="w-2 h-2 rounded-full bg-white/10"></div>
                                </div>
                            </div>

                            <div className="space-y-6">
                                {(activeTab === 'vehicles' ? stats?.top_models : stats?.top_types)?.map((item: any, idx: number) => (
                                    <div key={idx} className="group cursor-pointer">
                                        <div className="flex justify-between items-end mb-2">
                                            <div className="flex items-center gap-4">
                                                <span className="text-xs font-black text-slate-700">0{idx + 1}</span>
                                                <p className="font-bold text-slate-200 group-hover:text-blue-400 transition-colors">{item.name}</p>
                                            </div>
                                            <div className="flex items-end gap-3">
                                                <span className="text-sm font-black">{item.count} {t.stats.listings_unit.toLowerCase()}</span>
                                                <span className={`text-[10px] font-black px-2 py-0.5 rounded-full font-sans ${item.trend.startsWith('+') ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'}`}>
                                                    {item.trend}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                                            <motion.div
                                                initial={{ width: 0 }}
                                                animate={{ width: `${(item.count / 1500) * 100}%` }}
                                                className={`h-full ${activeTab === 'vehicles' ? 'bg-blue-600' : 'bg-indigo-600'}`}
                                            ></motion.div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </motion.div>

                        {/* Region Map Grid */}
                        <div className="bg-slate-900/60 backdrop-blur-md rounded-[40px] p-8 md:p-12 border border-white/5 shadow-2xl">
                            <h3 className="text-2xl font-black tracking-tight uppercase italic mb-10">{t.stats.regions_count} <span className="text-blue-500/50">/</span> {stats?.regions?.length} {t.stats.listings_unit.toLowerCase()}</h3>
                            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                                {stats?.regions?.map((reg: any, idx: number) => (
                                    <motion.div
                                        key={idx}
                                        whileHover={{ y: -5, scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                        onClick={() => handleRegionClick(reg)}
                                        className="bg-white/5 rounded-[25px] p-5 border border-white/5 hover:bg-white/10 transition-all cursor-pointer group active:bg-blue-600/10 hover:border-blue-500/30"
                                    >
                                        <div className="flex justify-between items-center mb-3">
                                            <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest font-sans group-hover:text-blue-400 transition-colors">{reg.name}</span>
                                            <MapPin size={12} className="text-slate-600 group-hover:text-blue-400" />
                                        </div>
                                        <p className="text-xl font-black tabular-nums">{reg.count}</p>
                                        <p className="text-[9px] font-black text-emerald-500/80 mt-1 uppercase tracking-widest font-sans">{reg.weekly_change} bu hafta</p>
                                    </motion.div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Sidebar Info */}
                    <div className="space-y-8">
                        <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-[40px] p-8 text-white relative overflow-hidden shadow-2xl">
                            <div className="absolute top-0 right-0 p-8 opacity-20 transform translate-x-4 -translate-y-4">
                                <TrendingUp size={120} />
                            </div>
                            <h3 className="text-2xl font-black mb-4 leading-tight">{t.stats.market_dynamics.split(' 2026')[0]} <br /> 2026</h3>
                            <p className="text-blue-100/80 text-sm font-medium leading-relaxed mb-8">
                                {t.stats.dynamics_desc}
                            </p>
                            <button
                                onClick={() => handleDownloadPDF(`${t.stats.market_dynamics.replace(/\s+/g, '_')}_${activeTab}`)}
                                className="bg-white text-blue-700 px-6 py-4 rounded-2xl font-black text-xs uppercase tracking-widest shadow-xl hover:bg-blue-50 transition-all active:scale-95 flex items-center gap-2"
                            >
                                <Download size={16} /> {t.stats.download_report}
                            </button>
                        </div>

                        <div className="bg-slate-900/60 backdrop-blur-md rounded-[40px] p-8 border border-white/5 relative overflow-hidden group">
                            <div className="absolute -right-4 -top-4 opacity-[0.03] group-hover:opacity-[0.08] transition-opacity">
                                <History size={120} />
                            </div>
                            <h3 className="text-xl font-black uppercase italic mb-6 flex items-center gap-2">
                                <History size={20} className="text-blue-400" /> {t.stats.weekly_archive}
                            </h3>
                            <p className="text-slate-500 text-xs font-medium mb-8">
                                {t.stats.archive_desc}
                            </p>
                            <div className="space-y-4">
                                {stats?.archive_data?.map((item: any, i: number) => (
                                    <div key={i} className="flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/5 hover:bg-white/10 transition-colors cursor-pointer group/item">
                                        <div>
                                            <p className="font-bold text-sm text-slate-200">{item.week}</p>
                                            <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest">{item.count} {t.stats.listings_unit.toLowerCase()}</p>
                                        </div>
                                        <button
                                            onClick={() => handleDownloadPDF(`Arxiv_${item.week}`)}
                                            className="p-2 bg-blue-500/10 text-blue-400 rounded-lg opacity-0 group-hover/item:opacity-100 transition-opacity"
                                        >
                                            <Download size={14} />
                                        </button>
                                    </div>
                                ))}
                            </div>
                            <button className="w-full mt-6 py-3 border border-white/10 rounded-2xl text-[10px] font-black uppercase tracking-widest text-slate-500 hover:text-white hover:bg-white/5 transition-all">
                                {t.stats.see_all}
                            </button>
                        </div>

                        <div className="bg-slate-900/60 backdrop-blur-md rounded-[40px] p-8 border border-white/5">
                            <h3 className="text-[10px] font-black uppercase tracking-[0.2em] mb-8 text-slate-500 font-sans">{t.stats.categories}</h3>
                            <div className="flex flex-wrap gap-3">
                                {stats?.categories?.map((cat: string, idx: number) => (
                                    <motion.span
                                        key={idx}
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                        onClick={() => setSelectedDetail({ type: 'category', value: cat })}
                                        className="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/5 rounded-xl text-xs font-bold cursor-pointer transition-colors hover:text-blue-400 hover:border-blue-400/30"
                                    >
                                        {cat}
                                    </motion.span>
                                ))}
                            </div>
                        </div>

                        <div
                            onClick={() => { setSelectedDetail({ type: 'listings', value: stats?.new_listings_details || [] }); setViewMode('detailed'); setListFilter('new'); }}
                            className="bg-slate-800/20 rounded-[40px] p-8 border border-white/5 group cursor-pointer hover:bg-blue-600/10 transition-all active:scale-95"
                        >
                            <div className="flex items-center gap-6">
                                <div className="w-12 h-12 bg-blue-500/20 rounded-2xl flex items-center justify-center text-blue-400 group-hover:scale-110 transition-transform">
                                    <Calendar size={24} />
                                </div>
                                <div>
                                    <h4 className="font-bold text-white group-hover:text-blue-400 transition-colors uppercase text-sm italic">{t.stats.new_listings_sidebar}</h4>
                                    <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest font-sans">{t.stats.all_filter}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
