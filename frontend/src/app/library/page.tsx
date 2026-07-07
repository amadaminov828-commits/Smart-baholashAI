"use client";

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Book as BookIcon, Search, Upload, Filter, X, Eye, Download, BookOpen, RefreshCw, CheckCircle, AlertCircle, Trash2 } from 'lucide-react';
import { api } from '@/services/api';
import { useTranslation } from '@/i18n/I18nProvider';
import { Navbar } from '@/components/Navbar';

interface Book {
  id: number;
  title: string;
  author: string;
  description: string;
  file: string;
  cover_image: string;
  category: string;
  category_display: string;
  is_indexed: boolean;
}

export default function LibraryPage() {
  const { t } = useTranslation();
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('all');
  const [showUpload, setShowUpload] = useState(false);
  const [viewingBook, setViewingBook] = useState<Book | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [reindexing, setReindexing] = useState(false);
  const [reindexResult, setReindexResult] = useState('');

  // Upload Form State
  const [uploadData, setUploadData] = useState({
    title: '',
    author: '',
    description: '',
    category: 'other',
    file: null as File | null,
    cover: null as File | null
  });

  useEffect(() => {
    fetchBooks();
  }, []);

  const fetchBooks = async () => {
    try {
      const res = await api.get('books/');
      setBooks(res.data);
    } catch (err) {
      console.error("Books fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadData.file) return;

    const formData = new FormData();
    formData.append('title', uploadData.title);
    formData.append('author', uploadData.author);
    formData.append('description', uploadData.description);
    formData.append('category', uploadData.category);
    formData.append('file', uploadData.file);
    if (uploadData.cover) formData.append('cover_image', uploadData.cover);

    setUploading(true);
    setUploadError('');
    try {
      await api.post('books/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setUploadSuccess(true);
      setTimeout(() => {
        setShowUpload(false);
        setUploadSuccess(false);
        fetchBooks();
        setUploadData({ title: '', author: '', description: '', category: 'other', file: null, cover: null });
      }, 1500);
    } catch (err: any) {
      setUploadError("Yuklashda xatolik yuz berdi. Qaytadan urinib ko'ring.");
    } finally {
      setUploading(false);
    }
  };

  const handleReindexAll = async () => {
    setReindexing(true);
    setReindexResult('');
    try {
      const res = await api.post('books/reindex-all/');
      const results = res.data.results || [];
      const ok = results.filter((r: any) => r.indexed).length;
      setReindexResult(`${ok} ta kitob muvaffaqiyatli indekslandi`);
      fetchBooks();
    } catch (err) {
      setReindexResult("Indekslashda xatolik yuz berdi");
    } finally {
      setReindexing(false);
      setTimeout(() => setReindexResult(''), 4000);
    }
  };

  const handleDeleteBook = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    if (!window.confirm("Haqiqatdan ham ushbu kitobni o'chirmoqchimisiz? Bu amalni ortga qaytarib bo'lmaydi.")) return;

    try {
      await api.delete(`books/${id}/`);
      setBooks(books.filter(b => b.id !== id));
    } catch (err) {
      console.error("Delete error:", err);
      alert("O'chirishda xatolik yuz berdi");
    }
  };

  const filteredBooks = books.filter(b => 
    (category === 'all' || b.category === category) &&
    (b.title.toLowerCase().includes(search.toLowerCase()) || b.author?.toLowerCase().includes(search.toLowerCase()))
  );

  const getFileUrl = (fileUrl: string) => {
    // If it's a relative path from Django, prefix with backend URL
    if (fileUrl && !fileUrl.startsWith('http')) {
      return `http://localhost:8000${fileUrl}`;
    }
    return fileUrl;
  };

  return (
    <div className="min-h-screen bg-[#0a0f1c] text-white">
      <Navbar />

      <main className="max-w-7xl mx-auto px-6 py-12">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-12">
          <div>
            <h1 className="text-4xl font-black tracking-tighter mb-2 bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent uppercase">
              Bilimlar Bazasi
            </h1>
            <p className="text-slate-400 font-medium">Baholashga oid barcha kitoblar va me'yoriy hujjatlar</p>
          </div>

          <div className="flex items-center gap-3 w-full md:w-auto">
            <div className="relative flex-1 md:w-64">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
              <input 
                type="text" 
                placeholder="Kitob qidirish..." 
                className="w-full bg-white/5 border border-white/10 rounded-2xl py-3 pl-12 pr-4 text-sm focus:border-blue-500 outline-none transition-all"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            {/* Reindex All Button */}
            <button
              onClick={handleReindexAll}
              disabled={reindexing}
              title="Barcha kitoblarni AI xotirasiga yozish"
              className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white p-3 rounded-2xl transition-all shadow-lg shadow-emerald-600/20"
            >
              <RefreshCw size={20} className={reindexing ? 'animate-spin' : ''} />
            </button>
            <button 
              onClick={() => setShowUpload(true)}
              className="bg-blue-600 hover:bg-blue-500 text-white p-3 rounded-2xl transition-all shadow-lg shadow-blue-600/20"
            >
              <Upload size={20} />
            </button>
          </div>
        </div>

        {/* Reindex Result Toast */}
        <AnimatePresence>
          {reindexResult && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mb-6 p-4 bg-emerald-600/20 border border-emerald-500/30 rounded-2xl text-emerald-400 text-sm font-medium flex items-center gap-3"
            >
              <CheckCircle size={18} /> {reindexResult}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Categories */}
        <div className="flex gap-3 mb-10 overflow-x-auto pb-2 scrollbar-none">
          {[
            { id: 'all', name: 'Barchasi' },
            { id: 'real_estate', name: "Ko'chmas mulk" },
            { id: 'vehicles', name: 'Transport' },
            { id: 'legal', name: 'Qonunchilik' },
            { id: 'methodology', name: 'Metodologiya' },
            { id: 'other', name: 'Boshqa' }
          ].map((cat) => (
            <button
              key={cat.id}
              onClick={() => setCategory(cat.id)}
              className={`px-6 py-2.5 rounded-full text-xs font-black uppercase tracking-widest transition-all border ${
                category === cat.id 
                  ? 'bg-blue-600 border-blue-500 shadow-lg shadow-blue-600/20' 
                  : 'bg-white/5 border-white/10 text-slate-400 hover:bg-white/10'
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>

        {/* Books Grid */}
        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-8">
            {[1,2,3,4,5].map(i => (
              <div key={i} className="aspect-[3/4] bg-white/5 rounded-3xl animate-pulse"></div>
            ))}
          </div>
        ) : filteredBooks.length === 0 ? (
          <div className="text-center py-24 text-slate-600">
            <BookIcon size={64} className="mx-auto mb-4 opacity-20" />
            <p className="font-bold text-lg">Hech qanday kitob topilmadi</p>
            <p className="text-sm mt-2">Yangi kitob yuklash uchun + tugmasini bosing</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-8">
            {filteredBooks.map((book) => (
              <motion.div 
                key={book.id}
                layoutId={`book-${book.id}`}
                whileHover={{ y: -10 }}
                className="group relative cursor-pointer"
                onClick={() => setViewingBook(book)}
              >
                <div className="aspect-[3/4] rounded-3xl overflow-hidden bg-slate-800 border border-white/5 shadow-2xl relative">
                  {book.cover_image ? (
                    <img src={getFileUrl(book.cover_image)} alt={book.title} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-slate-800 to-slate-900">
                      <BookIcon size={48} className="text-slate-700 mb-4" />
                      <span className="text-[10px] uppercase font-black text-slate-600 tracking-widest">Muqova mavjud emas</span>
                    </div>
                  )}
                  
                  {/* Overlay */}
                  <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-all duration-300 flex flex-col items-center justify-center gap-4 backdrop-blur-sm">
                    <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center hover:scale-110 transition-transform">
                      <Eye size={20} />
                    </div>
                    <a 
                      href={getFileUrl(book.file)} 
                      download
                      onClick={e => e.stopPropagation()}
                      className="w-12 h-12 bg-white/10 rounded-full flex items-center justify-center hover:bg-white/20 transition-all"
                    >
                      <Download size={20} />
                    </a>
                    <button 
                      onClick={(e) => handleDeleteBook(e, book.id)}
                      className="w-12 h-12 bg-red-600/20 text-red-400 rounded-full flex items-center justify-center hover:bg-red-600 hover:text-white transition-all border border-red-500/30"
                      title="O'chirish"
                    >
                      <Trash2 size={20} />
                    </button>
                  </div>
                </div>
                <h3 className="mt-4 font-bold text-sm line-clamp-1 group-hover:text-blue-400 transition-colors">{book.title}</h3>
                <p className="text-slate-500 text-xs mt-1">{book.author || "Muallif noma'lum"}</p>
                <div className="mt-2 flex items-center gap-2">
                   <span className="text-[10px] font-black uppercase text-blue-500/80 tracking-tighter">{book.category_display}</span>
                   {book.is_indexed && <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full shadow-[0_0_5px_rgba(16,185,129,0.5)]" title="AI uchun indekslangan"></span>}
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Upload Modal */}
        <AnimatePresence>
          {showUpload && (
            <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">
              <motion.div 
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                onClick={() => !uploading && setShowUpload(false)}
                className="absolute inset-0 bg-black/80 backdrop-blur-md"
              />
              <motion.div 
                initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
                className="bg-[#151b2b] border border-white/10 rounded-[40px] p-8 w-full max-w-xl relative z-10 shadow-2xl"
              >
                <div className="flex justify-between items-center mb-8">
                  <h2 className="text-2xl font-black tracking-tighter uppercase">Yangi Kitob Yuklash</h2>
                  <button onClick={() => !uploading && setShowUpload(false)} className="text-slate-500 hover:text-white transition-colors">
                    <X size={24} />
                  </button>
                </div>

                {uploadSuccess ? (
                  <div className="flex flex-col items-center justify-center py-12 gap-4">
                    <CheckCircle size={56} className="text-emerald-400" />
                    <p className="text-xl font-bold text-emerald-400">Muvaffaqiyatli yuklandi!</p>
                    <p className="text-slate-400 text-sm">Kitob AI xotirasiga ham qo'shildi</p>
                  </div>
                ) : (
                  <form onSubmit={handleUpload} className="space-y-6">
                    <div>
                      <label className="text-[10px] font-black uppercase text-slate-500 tracking-widest mb-2 block">Kitob Nomi</label>
                      <input 
                        required type="text" value={uploadData.title}
                        onChange={e => setUploadData({...uploadData, title: e.target.value})}
                        className="w-full bg-white/5 border border-white/10 rounded-2xl py-3 px-4 outline-none focus:border-blue-500" 
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-[10px] font-black uppercase text-slate-500 tracking-widest mb-2 block">Muallif</label>
                        <input 
                          type="text" value={uploadData.author}
                          onChange={e => setUploadData({...uploadData, author: e.target.value})}
                          className="w-full bg-white/5 border border-white/10 rounded-2xl py-3 px-4 outline-none focus:border-blue-500" 
                        />
                      </div>
                      <div>
                        <label className="text-[10px] font-black uppercase text-slate-500 tracking-widest mb-2 block">Kategoriya</label>
                        <select 
                          value={uploadData.category}
                          onChange={e => setUploadData({...uploadData, category: e.target.value})}
                          className="w-full bg-slate-800 border border-white/10 rounded-2xl py-3 px-4 outline-none focus:border-blue-500 text-white cursor-pointer"
                        >
                          <option value="real_estate" className="bg-[#151b2b]">Ko'chmas mulk</option>
                          <option value="vehicles" className="bg-[#151b2b]">Transport vositalari</option>
                          <option value="legal" className="bg-[#151b2b]">Qonunchilik</option>
                          <option value="methodology" className="bg-[#151b2b]">Metodologiya</option>
                          <option value="other" className="bg-[#151b2b]">Boshqa</option>
                        </select>
                      </div>
                    </div>
                    <div>
                      <label className="text-[10px] font-black uppercase text-slate-500 tracking-widest mb-2 block">Fayl (PDF/Docx)</label>
                      <input 
                        required type="file" accept=".pdf,.docx"
                        onChange={e => setUploadData({...uploadData, file: e.target.files?.[0] || null})}
                        className="w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-black file:uppercase file:bg-blue-600 file:text-white hover:file:bg-blue-500" 
                      />
                      <p className="text-xs text-slate-600 mt-2">💡 .docx fayllar avtomatik PDF ga o'giriladi</p>
                    </div>

                    {uploadError && (
                      <div className="flex items-center gap-2 text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-xl p-3">
                        <AlertCircle size={16} /> {uploadError}
                      </div>
                    )}
                    
                    <button 
                      type="submit" 
                      disabled={uploading}
                      className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-60 py-4 rounded-2xl font-black uppercase tracking-[0.2em] transition-all shadow-lg shadow-blue-600/20 flex items-center justify-center gap-3"
                    >
                      {uploading ? (
                        <>
                          <RefreshCw size={18} className="animate-spin" />
                          Yuklanmoqda...
                        </>
                      ) : "Bazaga Qo'shish"}
                    </button>
                  </form>
                )}
              </motion.div>
            </div>
          )}
        </AnimatePresence>

        {/* PDF Viewer Modal */}
        <AnimatePresence>
          {viewingBook && (
            <div className="fixed inset-0 z-[100] flex flex-col">
              <motion.div 
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="absolute inset-0 bg-black backdrop-blur-xl"
              />
              <header className="relative z-10 p-6 flex justify-between items-center border-b border-white/10 bg-[#0a0f1c]/90">
                <div className="flex items-center gap-4">
                   <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
                      <BookOpen size={20} />
                   </div>
                   <div>
                      <h2 className="text-sm font-bold tracking-tight">{viewingBook.title}</h2>
                      <p className="text-[10px] text-slate-500 uppercase font-black">{viewingBook.author}</p>
                   </div>
                </div>
                <div className="flex items-center gap-3">
                  <a
                    href={getFileUrl(viewingBook.file)}
                    download
                    className="p-3 bg-white/5 rounded-xl hover:bg-white/10 transition-colors flex items-center gap-2 text-xs font-bold text-slate-300"
                  >
                    <Download size={16} /> Yuklab olish
                  </a>
                  <button onClick={() => setViewingBook(null)} className="p-3 bg-white/5 rounded-xl hover:bg-white/10 transition-colors">
                    <X size={20} />
                  </button>
                </div>
              </header>
              <div className="flex-1 relative z-10 bg-[#0a0f1c]">
                 <iframe 
                    src={`${getFileUrl(viewingBook.file)}#toolbar=1&navpanes=1`}
                    className="w-full h-full border-none"
                    title={viewingBook.title}
                 />
              </div>
            </div>
          )}
        </AnimatePresence>

      </main>
    </div>
  );
}
