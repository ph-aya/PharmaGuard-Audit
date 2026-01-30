import pandas as pd
import requests
from io import StringIO
import os

def update_database():
    print("🛡️ Starting Fail-Safe Update Protocol...")

    # 1. قائمة الطوارئ (Emergency List)
    # هذه القائمة تحتوي على المواد الخطيرة جداً والحديثة (2022-2025)
    # نستخدمها في حال فشل الاتصال بالإنترنت تماماً
    manual_bans = [
        {"INCI Name": "BUTYLPHENYL METHYLPROPIONAL", "CAS No": "80-54-6"},  # Lilial
        {"INCI Name": "ZINC PYRITHIONE", "CAS No": "13463-41-7"},           # Dandruff
        {"INCI Name": "4-METHYLBENZYLIDENE CAMPHOR", "CAS No": "36861-47-9"}, # 2024 Ban
        {"INCI Name": "PENTETIC ACID", "CAS No": "67-43-6"},
        {"INCI Name": "PENTASODIUM PENTETATE", "CAS No": "140-01-2"},
        {"INCI Name": "DIMETHYLTOLYLAMINE", "CAS No": "99-97-8"},
        {"INCI Name": "SODIUM HYDROXYMETHYLGLYCINATE", "CAS No": "70161-44-3"},
        {"INCI Name": "TRIMETHYLBENZOYL DIPHENYLPHOSPHINE OXIDE", "CAS No": "75980-60-8"},
        {"INCI Name": "CHLOROFORM", "CAS No": "67-66-3"},
        {"INCI Name": "HYDROQUINONE", "CAS No": "123-31-9"}
    ]

    # الرابط المستقر جداً (على غيت هب)
    url = "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/master/cosing/csv/COSING_Annex_II_v2.csv"
    
    final_df = None

    # المحاولة 1: الاتصال بالإنترنت
    try:
        print("🌍 Attempting to download official database...")
        response = requests.get(url, timeout=20)
        
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text), on_bad_lines='skip')
            # توحيد أسماء الأعمدة
            df.columns = [str(c).strip().title() for c in df.columns] 
            print(f"✅ Download Success! Fetched {len(df)} rows.")
            final_df = df
        else:
            print(f"⚠️ Network Warning: Server returned {response.status_code}")
    
    except Exception as e:
        print(f"⚠️ Network Error: {e}")

    # المحاولة 2: المعالجة والدمج
    try:
        if final_df is None:
            print("⚠️ Switching to EMERGENCY MODE (Offline Data).")
            final_df = pd.DataFrame(manual_bans)
        else:
            # دمج المواد اليدوية مع الملف المحمل (لضمان وجود كل شيء)
            print("💉 Injecting critical 2025 updates...")
            injection_df = pd.DataFrame(manual_bans)
            
            # محاولة مطابقة أسماء الأعمدة للدمج
            # نبحث عن عمود الاسم في الملف المحمل
            name_col = next((c for c in final_df.columns if 'Name' in c or 'Inn' in c), 'INCI name')
            cas_col = next((c for c in final_df.columns if 'Cas' in c), 'CAS No')
            
            # إعادة تسمية أعمدة القائمة اليدوية لتطابق الملف
            injection_df.rename(columns={"INCI Name": name_col, "CAS No": cas_col}, inplace=True)
            
            final_df = pd.concat([final_df, injection_df], ignore_index=True)

        # الحفظ النهائي (مهم جداً)
        final_df.to_csv("banned.csv", index=False)
        print(f"💾 SUCCESS: Saved 'banned.csv' with {len(final_df)} entries.")
    
    except Exception as e:
        print(f"🚨 Logic Error: {e}")
        # الملاذ الأخير: إنشاء ملف صغير جداً حتى لا يفشل الروبوت
        df_emergency = pd.DataFrame(manual_bans)
        df_emergency.to_csv("banned.csv", index=False)
        print("💾 Saved Emergency Backup List.")

if __name__ == "__main__":
    update_database()
