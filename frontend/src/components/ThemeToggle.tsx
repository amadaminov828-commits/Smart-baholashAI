"use client";

import { useState, useEffect } from 'react';
import { Moon, Sun } from 'lucide-react';

export function ThemeToggle() {
    const [isDark, setIsDark] = useState(false);

    useEffect(() => {
        // Check initial preference from localStorage or HTML class
        const savedTheme = localStorage.getItem('app_theme');
        if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            setIsDark(true);
            document.documentElement.classList.add('dark');
        }
    }, []);

    const toggleTheme = () => {
        if (isDark) {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('app_theme', 'light');
            setIsDark(false);
        } else {
            document.documentElement.classList.add('dark');
            localStorage.setItem('app_theme', 'dark');
            setIsDark(true);
        }
    };

    return (
        <button
            onClick={toggleTheme}
            className="p-2 mr-2 text-gray-500 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors flex items-center justify-center"
            title="Tungi / Kunduzgi rejim"
        >
            {isDark ? <Sun size={20} className="text-yellow-500" /> : <Moon size={20} />}
        </button>
    );
}
