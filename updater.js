const axios = require('axios');
const fs = require('fs');
const ObjectsToCsv = require('objects-to-csv');

// المواد الاجبارية (2025)
const forcedBans = [
    { inci_name: "BUTYLPHENYL METHYLPROPIONAL", cas_no: "80-54-6" },
    { inci_name: "ZINC PYRITHIONE", cas_no: "13463-41-7" },
    { inci_name: "4-METHYLBENZYLIDENE CAMPHOR", cas_no: "36861-47-9" },
    { inci_name: "PENTETIC ACID", cas_no: "67-43-6" },
    { inci_name: "PENTASODIUM PENTETATE", cas_no: "140-01-2" },
    { inci_name: "DIMETHYLTOLYLAMINE", cas_no: "99-97-8" },
    { inci_name: "SODIUM HYDROXYMETHYLGLYCINATE", cas_no: "70161-44-3" },
    { inci_name: "TRIMETHYLBENZOYL DIPHENYLPHOSPHINE OXIDE", cas_no: "75980-60-8" },
    { inci_name: "CHLOROFORM", cas_no: "67-66-3" },
    { inci_name: "HYDROQUINONE", cas_no: "123-31-9" }
];

// المصدر (CDN سريع جداً)
const url = "https://cdn.jsdelivr.net/gh/openfoodfacts/openbeautyfacts@main/cosing/csv/COSING_Annex_II_v2.csv";

async function run() {
    console.log("🚀 Starting Node.js Updater...");
    let finalData = [];

    try {
        console.log("📡 Downloading from CDN...");
        const response = await axios.get(url);
        const lines = response.data.split('\n');

        // معالجة الاسطر
        lines.forEach(line => {
            // تنظيف السطر من علامات الاقتباس والفوارز الزائدة
            const cols = line.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/); // RegEx للفصل الذكي
            
            // اذا السطر بي بيانات مفيدة
            if(cols.length > 2) {
                 // تنظيف الاسم والرقم
                let name = cols[0]?.replace(/"/g, '').trim(); 
                let cas = cols[1]?.replace(/"/g, '').trim();

                // اذا ما لكيناهم بالاول، ندور بغير اعمدة (احتياط)
                if (!name || name.length < 3) name = cols[1]?.replace(/"/g, '').trim();
                
                if (name && name.length > 3 && !name.toLowerCase().includes('name')) {
                    finalData.push({ inci_name: name, cas_no: cas });
                }
            }
        });
        console.log(`✅ Downloaded ${finalData.length} items.`);
    } catch (e) {
        console.log("⚠️ Download Error (Using Backup Only).");
    }

    // الدمج
    console.log("💉 Injecting manual updates...");
    finalData = [...finalData, ...forcedBans];

    // الحفظ
    const csv = new ObjectsToCsv(finalData);
    await csv.toDisk('./banned.csv');
    console.log("💾 Saved banned.csv successfully.");
}

run();
