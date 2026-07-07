"use client";

import { useTranslation } from './I18nProvider';
import { Language } from './dictionaries';
import { Globe } from 'lucide-react';

export function LanguageSwitcher() {
    const { lang, setLanguage } = useTranslation();

    return (
        <div className="relative group inline-block">
            <button className="flex items-center gap-2 p-2 rounded-lg hover:bg-black/5 transition-colors text-sm font-medium">
                <Globe size={18} />
                <span className="uppercase">{lang}</span>
            </button>

            <div className="absolute right-0 top-full mt-2 w-32 bg-white rounded-xl shadow-xl border border-gray-100 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                <div className="py-2 flex flex-col">
                    {[
                        { id: 'uz', name: "O'zbek" },
                        { id: 'ru', name: "Русский" },
                        { id: 'en', name: "English" },
                        { id: 'kk', name: "Қазақша" },
                        { id: 'ky', name: "Кыргызча" },
                        { id: 'tg', name: "Тоҷикӣ" },
                        { id: 'tk', name: "Türkmen" }
                    ].map((item) => (
                        <button
                            key={item.id}
                            onClick={() => setLanguage(item.id as Language)}
                            className={`px-4 py-2 text-sm text-left hover:bg-blue-50 hover:text-blue-600 transition-colors ${lang === item.id ? 'font-bold text-blue-600 bg-blue-50/50' : 'text-gray-700'
                                }`}
                        >
                            {item.name}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}
