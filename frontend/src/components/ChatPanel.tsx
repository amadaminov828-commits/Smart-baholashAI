'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Image as ImageIcon, Send, X, Paperclip, Loader2, BookOpen } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  image?: string; // Base64 for local preview
}

const ChatPanel: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      processImage(file);
    }
  };

  const processImage = (file: File) => {
    if (!file.type.startsWith('image/')) {
      alert("Faqat rasm yuklash mumkin");
      return;
    }
    setSelectedImage(file);
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        const file = items[i].getAsFile();
        if (file) processImage(file);
      }
    }
  };

  const removeImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleSend = async () => {
    if ((!input.trim() && !selectedImage) || isLoading) return;

    const userMessage: Message = { 
      role: 'user', 
      content: input,
      image: imagePreview || undefined
    };
    
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    const currentImage = selectedImage;
    
    setInput('');
    removeImage();
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append('message', currentInput);
      formData.append('history', JSON.stringify(messages.map(m => ({ role: m.role, content: m.content }))));
      if (currentImage) {
        formData.append('image', currentImage);
      }

      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      const headers: Record<string, string> = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch('/api-proxy/v1/chat/', {
        method: 'POST',
        headers: headers,
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: `Xatolik: ${data.error || 'Noma\'lum xato'}` }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Server bilan aloqa uzildi.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Floating Neon Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="relative group bg-blue-600 hover:bg-blue-500 text-white rounded-full p-4 shadow-[0_0_20px_rgba(37,99,235,0.5)] transition-all hover:scale-110 active:scale-95 flex items-center justify-center overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-blue-600 opacity-0 group-hover:opacity-20 transition-opacity"></div>
          <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </button>
      )}

      {/* Glassmorphism Chat Window */}
      {isOpen && (
        <div className="bg-[#0f172a]/95 backdrop-blur-2xl border border-white/10 shadow-[0_0_50px_rgba(0,0,0,0.5),0_0_20px_rgba(37,99,235,0.1)] rounded-[32px] w-80 md:w-[450px] h-[650px] flex flex-col overflow-hidden transition-all duration-300 animate-in zoom-in-95 slide-in-from-bottom-10">
          
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-900/40 to-indigo-900/40 p-5 flex justify-between items-center text-white border-b border-white/5">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="absolute -inset-1 bg-cyan-500 rounded-full blur opacity-40 animate-pulse"></div>
                <div className="relative w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center shadow-lg">
                  <BookOpen size={20} className="text-white" />
                </div>
              </div>
              <div className="flex flex-col">
                <span className="font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-blue-200">Smart Yordamchi</span>
                <span className="text-[10px] text-cyan-400 font-medium tracking-widest uppercase">AI Vision Online</span>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white/40 hover:text-white hover:bg-white/10 p-2 rounded-xl transition-all"
            >
              <X size={24} />
            </button>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-white/10">
            {messages.length === 0 && (
              <div className="text-center mt-12 space-y-4 px-4">
                <div className="w-16 h-16 bg-blue-500/10 rounded-full mx-auto flex items-center justify-center mb-2">
                   <ImageIcon size={32} className="text-blue-400/30" />
                </div>
                <p className="text-sm text-gray-400 font-medium">Salom! Men rasmlarni ham tushunaman.</p>
                <p className="text-xs text-gray-500 italic">Rasm tashlang yoki savol bering.</p>
              </div>
            )}
            
            {messages.map((m, i) => (
              <div
                key={i}
                className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-4 duration-500`}
              >
                <div
                  className={`max-w-[85%] p-4 rounded-2xl text-sm leading-relaxed ${
                    m.role === 'user'
                      ? 'bg-blue-600 text-white rounded-br-none shadow-lg shadow-blue-900/20'
                      : 'bg-white/5 text-gray-200 border border-white/10 rounded-bl-none'
                  }`}
                >
                  {m.image && (
                    <img src={m.image} alt="User upload" className="w-full max-h-60 object-cover rounded-xl mb-3 border border-white/10 shadow-sm" />
                  )}
                  <div className="whitespace-pre-wrap">{m.content}</div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white/5 border border-white/10 p-4 rounded-2xl rounded-bl-none flex gap-2 items-center text-blue-400">
                  <Loader2 size={16} className="animate-spin" />
                  <span className="text-xs font-medium uppercase tracking-tighter">AI o'ylamoqda...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-6 bg-black/20 border-t border-white/5">
            {/* Image Preview */}
            <AnimatePresence>
              {imagePreview && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }}
                  className="mb-4 relative w-20 h-20"
                >
                  <img src={imagePreview} className="w-full h-full object-cover rounded-2xl border-2 border-blue-500 shadow-lg shadow-blue-500/20" />
                  <button 
                    onClick={removeImage}
                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 shadow-lg hover:bg-red-400 transition-colors"
                  >
                    <X size={12} />
                  </button>
                </motion.div>
              )}
            </AnimatePresence>

            <div className="relative flex items-center gap-3">
              <input 
                type="file" accept="image/*" className="hidden" 
                ref={fileInputRef} onChange={handleImageSelect} 
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className="p-3 bg-white/5 hover:bg-white/10 text-gray-400 rounded-2xl transition-all"
                title="Rasm yuklash"
              >
                <Paperclip size={20} />
              </button>

              <div className="relative flex-1">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  onPaste={handlePaste}
                  placeholder="Xabar yozing yoki rasm tashlang..."
                  className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-4 text-sm text-white placeholder:text-gray-500 focus:outline-none focus:border-blue-500 transition-all"
                  disabled={isLoading}
                />
                <button
                  onClick={handleSend}
                  disabled={isLoading || (!input.trim() && !selectedImage)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 bg-blue-600 hover:bg-blue-500 text-white p-2.5 rounded-xl transition-all active:scale-90 disabled:opacity-50"
                >
                  <Send size={18} />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatPanel;
