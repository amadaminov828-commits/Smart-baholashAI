"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';
import { dictionaries, Language } from './dictionaries';

type DictionaryType = typeof dictionaries.uz;

interface I18nContextType {
    lang: Language;
    t: DictionaryType;
    setLanguage: (lang: Language) => void;
}

const I18nContext = createContext<I18nContextType | undefined>(undefined);

export const I18nProvider = ({ children }: { children: React.ReactNode }) => {
    const [lang, setLangState] = useState<Language>('uz');

    useEffect(() => {
        const saved = localStorage.getItem('app_lang') as Language;
        if (saved && dictionaries[saved]) {
            setLangState(saved);
        }
    }, []);

    const setLanguage = (newLang: Language) => {
        setLangState(newLang);
        localStorage.setItem('app_lang', newLang);
    };

    const t = dictionaries[lang];

    return (
        <I18nContext.Provider value={{ lang, t, setLanguage }}>
            {children}
        </I18nContext.Provider>
    );
};

export const useTranslation = () => {
    const context = useContext(I18nContext);
    if (!context) {
        throw new Error('useTranslation must be used within an I18nProvider');
    }
    return context;
};
