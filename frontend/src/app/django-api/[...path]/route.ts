import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest, { params }: { params: Promise<{ path?: string[] }> | { path?: string[] } }) {
    console.log(`[PROXY] Intercepted POST request to: ${req.url}`);
    const resolvedParams = await params;
    return handleProxy(req, resolvedParams?.path || []);
}

export async function GET(req: NextRequest, { params }: { params: Promise<{ path?: string[] }> | { path?: string[] } }) {
    console.log(`[PROXY] Intercepted GET request to: ${req.url}`);
    const resolvedParams = await params;
    return handleProxy(req, resolvedParams?.path || []);
}

export async function PATCH(req: NextRequest, { params }: { params: Promise<{ path?: string[] }> | { path?: string[] } }) {
    console.log(`[PROXY] Intercepted PATCH request to: ${req.url}`);
    const resolvedParams = await params;
    return handleProxy(req, resolvedParams?.path || []);
}

export async function PUT(req: NextRequest, { params }: { params: Promise<{ path?: string[] }> | { path?: string[] } }) {
    console.log(`[PROXY] Intercepted PUT request to: ${req.url}`);
    const resolvedParams = await params;
    return handleProxy(req, resolvedParams?.path || []);
}

export async function DELETE(req: NextRequest, { params }: { params: Promise<{ path?: string[] }> | { path?: string[] } }) {
    console.log(`[PROXY] Intercepted DELETE request to: ${req.url}`);
    const resolvedParams = await params;
    return handleProxy(req, resolvedParams?.path || []);
}

export async function OPTIONS(req: NextRequest, { params }: { params: Promise<{ path?: string[] }> | { path?: string[] } }) {
    console.log(`[PROXY] Intercepted OPTIONS request to: ${req.url}`);
    const resolvedParams = await params;
    return handleProxy(req, resolvedParams?.path || []);
}

async function handleProxy(req: NextRequest, pathArray: string[]) {
    const path = pathArray.join("/");
    const url = new URL(req.url);
    const search = url.search;

    // Construct destination URL.
    let targetUrl = `http://127.0.0.1:8000/api/${path}`;

    // Django ALWAYS requires a trailing slash for API routes unless they map to a file.
    if (!targetUrl.endsWith('/')) {
        targetUrl += '/';
    }

    if (search) {
        targetUrl += search;
    }

    const headers = new Headers(req.headers);
    headers.delete("host");
    headers.delete("connection");
    headers.delete("content-length"); // Let fetch calculate the length

    console.log(`[PROXY] Forwarding to Django: ${targetUrl} (Method: ${req.method})`);

    try {
        const body = req.method !== "GET" && req.method !== "HEAD" ? await req.text() : undefined;

        const response = await fetch(targetUrl, {
            method: req.method,
            headers: headers,
            body: body,
            redirect: 'manual'
        });

        console.log(`[PROXY] Django replied with status: ${response.status}`);

        let bodyBuffer = await response.arrayBuffer();

        if (response.status === 500) {
            const textRaw = new TextDecoder().decode(bodyBuffer);
            console.log(`[PROXY] 500 BODY TRACE:\n${textRaw.substring(0, 1500)}`);
        }

        const responseHeaders = new Headers(response.headers);
        responseHeaders.set("Access-Control-Allow-Origin", "*");
        responseHeaders.set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, PATCH, OPTIONS");

        return new NextResponse(bodyBuffer, {
            status: response.status,
            statusText: response.statusText,
            headers: responseHeaders,
        });
    } catch (error: any) {
        console.error("[PROXY] Proxy error:", error.message);
        return new NextResponse(JSON.stringify({ error: "Proxy server error", details: error.message }), {
            status: 500,
            headers: { "Content-Type": "application/json" },
        });
    }
}
