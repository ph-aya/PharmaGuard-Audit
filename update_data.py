import pandas as pd
import requests
from io import StringIO
import os

def update_database():
    print("🚀 Starting High-Performance Update...")

    # هذا الرابط مستقر جداً (Raw CSV) وسريع لأنه نص خالص
    # المصدر: OpenBeautyFacts (نسخة مطابقة للمواصفات الأوروبية)
    stable_url = "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/master/cosing/csv/COSING_Annex_II_v2.csv"
    
    # قائمة المواد الجديدة (الحقن اليدوي) - 2024/2025
    new_bans = [
        {"INCI name": "BUTYLPHENYL METHYLPROPIONAL", "CAS No": "80-54-6"},
        {"INCI name": "ZINC PYRITHIONE", "CAS No": "13463-41-7"},
        {"INCI name": "4-METHYLBENZYLIDENE CAMPHOR", "CAS No": "36861-47-9"},
        {"INCI name": "PENTETIC ACID", "CAS No": "67-43-6"},
        {"INCI name": "PENTASODIUM PENTETATE", "CAS No": "140-01-2"},
        {"INCI name": "DIMETHYLTOLYLAMINE", "CAS No": "99-97-8"},
        {"INCI name": "SODIUM HYDROXYMETHYLGLYCINATE", "CAS No": "70161-44-3"},
        {"INCI name": "TRIMETHYLBENZOYL DIPHENYLPHOSPHINE OXIDE", "CAS No": "75980-60-8"}
    ]

    try:
        print("📥 Downloading heavy database...")
        # استخدام requests مع timeout عالي
        response = requests.get(stable_url, timeout=60)
        
        if response.status_code == 200:
            # قراءة الملف
            df = pd.read_csv(StringIO(response.text), on_bad_lines='skip', low_memory=False)
            
            # 🛑 صمام الأمان: إذا الملف صغير (أقل من 1000 مادة) نرفضه
            if len(df) < 1000:
                raise Exception("Downloaded file is too small! Operation aborted.")

            print(f"✅ Base Loaded: {len(df)} substances.")

            # توحيد أسماء الأعمدة لتجنب المشاكل
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            # محاولة العثور على الأعمدة الصحيحة
            name_col = next((c for c in df.columns if 'name' in c or 'inn' in c), 'inci name')
            cas_col = next((c for c in df.columns if 'cas' in c), 'cas no')

            # 💉 حقن المواد الجديدة (Injecting New Bans)
            print("💉 Injecting 2025 updates...")
            new_rows = []
            existing_names = df[name_col].astype(str).str.lower().values
            
            for item in new_bans:
                # نضيف المادة فقط إذا لم تكن موجودة
                if item["INCI name"].lower() not in existing_names:
                    row = {col: "" for col in df.columns} # صف فارغ
                    row[name_col] = item["INCI name"]
                    row[cas_col] = item["CAS No"]
                    new_rows.append(row)
            
            if new_rows:
                df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)

            # الحفظ النهائي
            df.to_csv("banned.csv", index=False)
            print(f"💾 SAVED SUCCESS: 'banned.csv' now has {len(df)} entries.")
        
        else:
            print(f"❌ Server Error: {response.status_code}")
            exit(1) # نخرج بخطأ حتى ينبهنا النظام

    except Exception as e:
        print(f"🚨 FATAL ERROR: {e}")
        exit(1) # ممنوع الحفظ إذا اكو خطأ

if __name__ == "__main__":
    update_database()
