const axios = require('axios');
const fs = require('fs');

async function directDownload() {
    console.log("🚀 Starting Direct API Download...");

    // هذا الرابط المباشر للملف (بدون تصفح، بدون دكم)
    const url = "https://data.europa.eu/api/hub/store/data/cosing-annex-ii-v2.csv";
    
    try {
        console.log("📥 Fetching Data...");
        const response = await axios.get(url, {
            timeout: 60000, // مهلة دقيقة كاملة
            responseType: 'arraybuffer' // تحميل كملف خام
        });

        // حفظ الملف كما هو بالضبط
        fs.writeFileSync('./banned.csv', response.data);
        console.log("✅ Success! File saved as 'banned.csv'");
        
        // التحقق من الحجم
        const stats = fs.statSync('./banned.csv');
        console.log(`📦 File Size: ${stats.size / 1024} KB`);

        if (stats.size < 50000) { // اذا اقل من 50 كيلو بايت يعني الملف فارغ
            console.error("⚠️ File is too small, something is wrong.");
            process.exit(1);
        }

    } catch (error) {
        console.error(`❌ Error: ${error.message}`);
        process.exit(1);
    }
}

directDownload();
