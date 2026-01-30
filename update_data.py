import pandas as pd
import urllib.request
from io import StringIO
import time

def update_database():
    print("🔋 Connecting to Satellite Mirrors...")

    # القائمة الذهبية للروابط (اذا فشل واحد يجرب الثاني)
    # لاحظي: غيرنا master الى main وهو السبب الرئيسي للمشكلة
    urls = [
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/main/cosing/csv/COSING_Annex_II_v2.csv",
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/master/cosing/csv/COSING_Annex_II_v2.csv",
        "https://data.europa.eu/api/hub/store/data/cosing-annex-ii-v2.csv"
    ]
    
    # قائمة الطوارئ (للحماية فقط)
    emergency_backup = [
        {"inci_name": "BUTYLPHENYL METHYLPROPIONAL", "cas_no": "80-54-6"},
        {"inci_name": "ZINC PYRITHIONE", "cas_no": "13463-41-7"},
        {"inci_name": "HYDROQUINONE", "cas_no": "123-31-9"}
    ]

    fetched_df = None

    for link in urls:
        try:
            print(f"📡 Trying URL: {link} ...")
            # استخدام urllib بدل requests لتجاوز بعض مشاكل السيرفرات
            with urllib.request.urlopen(link, timeout=30) as response:
                data = response.read().decode('utf-8', errors='ignore')
                
                # فحص سريع: هل البيانات نصية وبها سطور كثيرة؟
                if len(data.splitlines()) < 100:
                    print("⚠️ File too small, skipping...")
                    continue
                
                # تحويل النص الى جدول
                df = pd.read_csv(StringIO(data), on_bad_lines='skip', low_memory=False)
                
                # تنظيف الأعمدة
                df.columns = [str(c).strip().lower() for c in df.columns]
                
                # توحيد الأسماء (Mapping)
                # هذا الجزء ذكي جداً: يبحث عن أي عمود يشبه الاسم ويسميه inci_name
                renamed = False
                for col in df.columns:
                    if 'name' in col or 'inn' in col:
                        df.rename(columns={col: 'inci_name'}, inplace=True)
                        renamed = True
                        break
                
                if renamed and len(df) > 1000:
                    fetched_df = df
                    print(f"✅ BINGO! Downloaded {len(df)} substances.")
                    break # نخرج من اللوب لأننا نجحنا

        except Exception as e:
            print(f"❌ Failed: {e}")
            continue

    # مرحلة الحفظ
    if fetched_df is not None:
        # حقن المواد الجديدة 2025
        print("💉 Injecting 2025 Updates...")
        new_bans = pd.DataFrame([
            {"inci_name": "4-METHYLBENZYLIDENE CAMPHOR", "cas_no": "36861-47-9"},
            {"inci_name": "PENTETIC ACID", "cas_no": "67-43-6"},
            {"inci_name": "PENTASODIUM PENTETATE", "cas_no": "140-01-2"},
            {"inci_name": "DIMETHYLTOLYLAMINE", "cas_no": "99-97-8"},
            {"inci_name": "SODIUM HYDROXYMETHYLGLYCINATE", "cas_no": "70161-44-3"},
            {"inci_name": "TRIMETHYLBENZOYL DIPHENYLPHOSPHINE OXIDE", "cas_no": "75980-60-8"}
        ])
        
        # التأكد من وجود عمود cas_no
        cas_col = next((c for c in fetched_df.columns if 'cas' in c), 'cas_no')
        fetched_df.rename(columns={cas_col: 'cas_no'}, inplace=True)

        final_df = pd.concat([fetched_df, new_bans], ignore_index=True)
        final_df.to_csv("banned.csv", index=False)
        print("💾 SAVED FULL DATABASE.")
    else:
        print("🚨 ALL MIRRORS FAILED. Using Emergency Backup.")
        pd.DataFrame(emergency_backup).to_csv("banned.csv", index=False)

if __name__ == "__main__":
    update_database()
