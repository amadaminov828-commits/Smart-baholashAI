import { NextResponse } from 'next/server';

export async function GET() {
    try {
        // 1. Get token
        const rawBody = JSON.stringify({ username: "331111111", password: "12345678" });
        const loginRes = await fetch("http://localhost:3000/api-proxy/v1/users/auth/login/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: rawBody,
        });

        if (loginRes.status !== 200) {
            return NextResponse.json({ error: "Login failed", status: loginRes.status, body: await loginRes.text() });
        }
        const tokenData = await loginRes.json();
        const token = tokenData.access;

        // 2. Fetch /users/me via proxy
        const meRes = await fetch("http://localhost:3000/api-proxy/v1/users/me", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        const meText = await meRes.text();

        return NextResponse.json({
            status: meRes.status,
            body: meText
        });
    } catch (error: any) {
        return NextResponse.json({ error: error.message, stack: error.stack });
    }
}
