import { NextRequest, NextResponse } from "next/server";
import fs from "fs";

export const dynamic = 'force-dynamic';
export const revalidate = 0;

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

    // Construct destination URL properly without URL() normalization which might strip trailing slashes
    let finalUrl = `http://127.0.0.1:8000/api/${path}`;

    // Check if the original request path had a trailing slash. If not, Django usually expects one.
    if (!finalUrl.endsWith('/') && !finalUrl.match(/\.[a-zA-Z0-9]+$/)) {
        finalUrl += '/';
    }

    if (url.search) {
        // Strip trailing slash before adding search if it somehow interferes?
        // No, trailing slash MUST come BEFORE the query string for Django!
        finalUrl += url.search;
    }

    const headers = new Headers(req.headers);
    headers.delete("host");
    headers.delete("connection");
    headers.delete("content-length"); // Let fetch calculate the length

    const authHeader = req.headers.get("authorization");

    let logMsg = `\n--- [PROXY] ` + new Date().toISOString() + ` ---\n`;
    logMsg += `Original Method: ${req.method}, Original URL: ${req.url}\n`;
    logMsg += `Forwarding to Django: ${finalUrl}\n`;
    logMsg += `Auth Header present: ${!!authHeader} (Length: ${authHeader?.length || 0})\n`;

    console.log(`[PROXY] Forwarding to Django: ${finalUrl} (Method: ${req.method})`);

    try {
        const contentType = req.headers.get("content-type") || "";
        let body: any = undefined;

        if (req.method !== "GET" && req.method !== "HEAD") {
            if (contentType.includes("multipart/form-data")) {
                body = await req.formData();
                // When forwarding FormData, delete the Content-Type header
                // so fetch can automatically set it with the correct boundary
                headers.delete("content-type");
            } else if (contentType.includes("application/json")) {
                body = await req.text();
            } else {
                body = await req.blob();
            }
        }

        const response = await fetch(finalUrl, {
            method: req.method,
            headers: headers,
            body: body,
            redirect: 'manual'
        });

        logMsg += `Django replied with status: ${response.status} ${response.statusText}\n`;
        fs.appendFileSync('c:\\Users\\Asus\\Desktop\\antigravity\\proxy_debug.log', logMsg);

        console.log(`[PROXY] Django replied with status: ${response.status}`);

        const responseHeaders = new Headers(response.headers);
        responseHeaders.set("Access-Control-Allow-Origin", "*");
        responseHeaders.set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, PATCH, OPTIONS");
        responseHeaders.set("Cache-Control", "no-store, no-cache, must-revalidate, proxy-revalidate");
        responseHeaders.set("Pragma", "no-cache");
        responseHeaders.set("Expires", "0");
        responseHeaders.set("X-Debug-Final-Url", finalUrl);

        return new NextResponse(response.body, {
            status: response.status,
            statusText: response.statusText,
            headers: responseHeaders,
        });
    } catch (error: any) {
        logMsg += `Proxy error: ${error.message}\n`;
        fs.appendFileSync('c:\\Users\\Asus\\Desktop\\antigravity\\proxy_debug.log', logMsg);
        console.error("[PROXY] Proxy error:", error.message);
        return new NextResponse(JSON.stringify({ error: "Proxy server error", details: error.message }), {
            status: 500,
            headers: { "Content-Type": "application/json" },
        });
    }
}
