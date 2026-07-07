const fetch = require('node-fetch');

async function testFetch() {
    try {
        const res = await fetch('http://localhost:3000/django-api/v1/reports/', {
            headers: {
                // Mock a simple auth or just hit it
                'Content-Type': 'application/json'
            }
        });
        const text = await res.text();
        console.log("STATUS:", res.status);
        console.log("BODY:", text.substring(0, 1000));
    } catch (e) {
        console.error("Fetch failed:", e);
    }
}
testFetch();
