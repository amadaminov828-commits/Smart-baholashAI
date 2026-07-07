"use client";

import React from 'react';

interface LogoProps {
    className?: string;
    size?: number;
}

export const Logo: React.FC<LogoProps> = ({ className, size = 180 }) => {
    return (
        <div className={className} style={{ width: size, height: size }}>
            <svg width="100%" height="100%" viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="roofGrad" x1="100" y1="100" x2="400" y2="400" gradientUnits="userSpaceOnUse">
                        <stop stopColor="#3A86FF" />
                        <stop offset="1" stopColor="#38BDF8" />
                    </linearGradient>
                    <linearGradient id="arrowGrad" x1="150" y1="200" x2="450" y2="450" gradientUnits="userSpaceOnUse">
                        <stop stopColor="#4ADE80" />
                        <stop offset="1" stopColor="#22C55E" />
                    </linearGradient>
                    <filter id="glowEffect">
                        <feGaussianBlur stdDeviation="6" result="blur" />
                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                    <path id="curvePath" d="M 80, 420 A 200,200 0 0,0 432, 420" />
                </defs>

                {/* Outer Circular Container */}
                <circle cx="256" cy="256" r="230" fill="#0F172A" stroke="#1E293B" strokeWidth="2" />

                {/* House Roof (Perspective bars) */}
                <path d="M120 220L256 80L392 220" stroke="url(#roofGrad)" strokeWidth="30" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M160 260L256 160L352 260" stroke="#3A86FF" strokeWidth="15" strokeLinecap="round" strokeLinejoin="round" opacity="0.4" />

                {/* Car Silhouette (Sleek) */}
                <path d="M140 320C140 300 180 285 256 285C332 285 372 300 372 320V360H140V320Z" fill="#38BDF8" opacity="0.7" />
                <path d="M180 360H332V380H180V360Z" fill="#1E40AF" />

                {/* Prominent Checkmark / Arrow (The 'Smart' part) */}
                <path d="M220 380L300 440L460 160" stroke="url(#arrowGrad)" strokeWidth="40" strokeLinecap="round" strokeLinejoin="round" filter="url(#glowEffect)" />

                {/* Balanced Text: SMART BAHOLASH */}
                <text fill="white" fontSize="38" fontWeight="900" letterSpacing="6">
                    <textPath href="#curvePath" startOffset="50%" textAnchor="middle">
                        SMART BAHOLASH
                    </textPath>
                </text>
            </svg>
        </div>
    );
};
