import pandas as pd
import requests
import time
from io import StringIO

def update_database():
    print("🛡️ Starting Smart-Sync Protocol...")
    
    # 1. المصدر المضمون (حتى لو قديم، هو الأساس)
    # هذا الرابط مستحيل يفشل لأنه على GitHub
    backup_url = "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/master/cosing/csv/COSING_Annex_II_v2.csv"
    
    try:
        print("📥 Fetching base database...")
        response = requests.get(backup_url, timeout=30)
        
        if response.status_code == 200:
            # قراءة الملف القديم
            df = pd.read_csv(StringIO(response.text), on_bad_lines='skip')
            
            # تنظيف الأعمدة
            df.columns = [str(c).strip().lower() for c in df.columns]
            print(f"✅ Base loaded: {len(df)} substances.")

            # ---------------------------------------------------------
            # 💉 The Injection: حقن المواد الجديدة يدوياً (Workaround)
            # هذه القائمة تغطي تحديثات 2022-2025 التي يفتقدها الملف القديم
            # ---------------------------------------------------------
            new_bans = [
                {"name": "BUTYLPHENYL METHYLPROPIONAL", "cas": "80-54-6"},  # Lilial (2022)
                {"name": "ZINC PYRITHIONE", "cas": "13463-41-7"},           # Anti-dandruff (2022)
                {"name": "SODIUM HYDROXYMETHYLGLYCINATE", "cas": "70161-44-3"},
                {"name": "4-METHYLBENZYLIDENE CAMPHOR", "cas": "36861-47-9"}, # Omnibus VII (2024/25)
                {"name": "PENTETIC ACID", "cas": "67-43-6"},
                {"name": "PENTASODIUM PENTETATE", "cas": "140-01-2"},
                {"name": "DIMETHYLTOLYLAMINE", "cas": "99-97-8"},
                {"name": "TRIMETHYLBENZOYL DIPHENYLPHOSPHINE OXIDE", "cas": "75980-60-8"}
            ]

            print(f"💉 Injecting {len(new_bans)} new critical substances...")
            
            # العثور على اسم الأعمدة الصحيحة في الملف
            name_col = next((c for c in df.columns if 'name' in c or 'inn' in c), 'inci name')
            cas_col = next((c for c in df.columns if 'cas' in c), 'cas no')

            # إضافة المواد الجديدة للجدول
            new_rows = []
            for item in new_bans:
                # نتحقق اذا المادة موجودة اصلاً حتى لا نكررها
                if item["name"].lower() not in df[name_col].astype(str).str.lower().values:
                    row = {col: "" for col in df.columns} # صف فارغ
                    row[name_col] = item["name"]
                    row[cas_col] = item["cas"]
                    new_rows.append(row)
            
            if new_rows:
                df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
                print(f"✅ Successfully added {len(new_rows)} new bans.")
            
            # حفظ الملف النهائي
            df.to_csv("banned.csv", index=False)
            print(f"💾 File saved. Total Count: {len(df)}")
            
        else:
            print(f"❌ Failed to fetch base DB. Status: {response.status_code}")
            exit(1)

    except Exception as e:
        print(f"🚨 Critical Failure: {e}")
        exit(1)

if __name__ == "__main__":
    update_database()
