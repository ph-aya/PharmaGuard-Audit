const { chromium } = require('playwright');
const XLSX = require('xlsx');
const ObjectsToCsv = require('objects-to-csv');
const fs = require('fs');

async function humanDownload() {
    console.log("🤖 Launching Virtual Browser...");
    
    // تشغيل متصفح كروم وهمي
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    try {
        console.log("🌍 Going to EU Website...");
        // الرابط المباشر لقائمة Annex II
        await page.goto('https://ec.europa.eu/growth/tools-databases/cosing/?fuseaction=search.details_v2&id=1&annex_id=II', { timeout: 60000 });

        // ننتظر شوية حتى الموقع يحمل (مثل البشر)
        console.log("⏳ Waiting for page to load...");
        await page.waitForTimeout(5000);

        // التعامل مع التنزيل
        console.log("🖱️ Looking for 'Export' button...");
        
        // ننتظر دكمة التنزيل ونضغط عليها
        const downloadPromise = page.waitForEvent('download');
        
        // هذا الكود يدور على اي دكمة بيها كلمة Export أو ايقونة اكسل
        // بموقع EU القديم والجديد، عادة الرابط يحتوي على 'fuseaction=search.export'
        await page.click('a[href*="export"], img[title*="Export"], i.fa-file-excel');

        const download = await downloadPromise;
        const tempPath = await download.path();
        console.log("✅ File Downloaded Successfully!");

        // --- مرحلة التحويل (Excel to CSV) ---
        console.log("⚙️ Converting Excel to CSV...");
        
        // قراءة ملف الاكسل
        const workbook = XLSX.readFile(tempPath);
        const sheetName = workbook.SheetNames[0];
        const rawData = XLSX.utils.sheet_to_json(workbook.Sheets[sheetName]);

        console.log(`📊 Found ${rawData.length} rows.`);

        // تنظيف البيانات
        const cleanData = rawData.map(row => {
            // ندور على الاسم والرقم بغض النظر عن اسم العمود
            const values = Object.values(row);
            const keys = Object.keys(row).map(k => k.toLowerCase());
            
            let name = "";
            let cas = "";

            // محاولة ذكية لإيجاد الاسم
            keys.forEach((key, index) => {
                if (key.includes('name') || key.includes('inn')) name = values[index];
                if (key.includes('cas')) cas = values[index];
            });

            return { inci_name: name, cas_no: cas };
        }).filter(item => item.inci_name && item.inci_name.length > 2);

        // الحفظ النهائي
        const csv = new ObjectsToCsv(cleanData);
        await csv.toDisk('./banned.csv');
        console.log(`💾 SAVED 'banned.csv' with ${cleanData.length} items.`);

    } catch (error) {
        console.error("❌ Error:", error.message);
        // في حال الفشل، الكود راح يطبع الخطأ ويطلع
        process.exit(1);
    } finally {
        await browser.close();
    }
}

humanDownload();
