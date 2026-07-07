const { startTunnel } = require('untun');

async function main() {
  console.log("Starting Cloudflare Quick Tunnel on port 3000...");
  try {
    const tunnel = await startTunnel({
      port: 3000,
      acceptCloudflareNotice: true
    });
    const url = await tunnel.getURL();
    console.log("-----------------------------------------");
    console.log(`Cloudflare Tunnel started successfully!`);
    console.log(`URL: ${url}`);
    console.log("-----------------------------------------");
    
    // Write URL to file for settings lookup or debug
    const fs = require('fs');
    fs.writeFileSync('../cf_url.txt', url);
  } catch (err) {
    console.error("Error starting tunnel:", err);
  }
}

main();
