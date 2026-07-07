const fs = require('fs');
try {
    const content = fs.readFileSync('c:/Users/Asus/Desktop/antigravity/backend/server_log.txt', 'utf16le');
    const lines = content.split('\n');
    const lastLines = lines.slice(-200);
    console.log(lastLines.join('\n'));
} catch (error) {
    console.error(error);
}

