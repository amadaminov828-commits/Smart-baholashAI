"use client";

import { useParams, useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function VerifyReportFallback() {
    const params = useParams();
    const router = useRouter();
    const id = params.id;

    useEffect(() => {
        if (id) {
            // Redirect from old QR code path to new verification path
            router.replace(`/verify/${id}`);
        }
    }, [id, router]);

    return (
        <div className="min-h-screen bg-[#0a0f1d] flex items-center justify-center">
            <div className="w-12 h-12 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin"></div>
        </div>
    );
}
