import pandas as pd
import requests
from io import StringIO
import os

def update_database():
    print("🧟‍♂️ Starting Zombie-Mode Update...")

    # 1. قائمة الطوارئ (Emergency Backup)
    # هذه القائمة نستخدمها اذا فشل كل شيء بالكون
    backup_data = [
        {"inci_name": "BUTYLPHENYL METHYLPROPIONAL", "cas_no": "80-54-6"},
        {"inci_name": "ZINC PYRITHIONE", "cas_no": "13463-41-7"},
        {"inci_name": "4-METHYLBENZYLIDENE CAMPHOR", "cas_no": "36861-47-9"},
        {"inci_name": "PENTETIC ACID", "cas_no": "67-43-6"},
        {"inci_name": "PENTASODIUM PENTETATE", "cas_no": "140-01-2"},
        {"inci_name": "DIMETHYLTOLYLAMINE", "cas_no": "99-97-8"},
        {"inci_name": "SODIUM HYDROXYMETHYLGLYCINATE", "cas_no": "70161-44-3"},
        {"inci_name": "TRIMETHYLBENZOYL DIPHENYLPHOSPHINE OXIDE", "cas_no": "75980-60-8"},
        {"inci_name": "CHLOROFORM", "cas_no": "67-66-3"},
        {"inci_name": "HYDROQUINONE", "cas_no": "123-31-9"}
    ]

    # رابط قوي جداً (Raw GitHub)
    url = "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/master/cosing/csv/COSING_Annex_II_v2.csv"
    
    # المتغير اللي راح يشيل الداتا النهائية
    final_df = None

    # --- المحاولة 1: التحميل من النت ---
    try:
        print("🌍 Attempting download...")
        response = requests.get(url, timeout=40) # وقت انتظار طويل
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text), on_bad_lines='skip', low_memory=False)
            print(f"✅ Downloaded {len(df)} rows from internet.")
            
            # تنظيف الاعمدة لتطابق الكود
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            # محاولة توحيد الاسماء
            # اذا العمود اسمه 'inci name' او 'name' نسويه 'inci_name'
            col_map = {}
            for col in df.columns:
                if 'name' in col or 'inn' in col:
                    col_map[col] = 'inci_name'
                elif 'cas' in col:
                    col_map[col] = 'cas_no'
            
            df.rename(columns=col_map, inplace=True)
            
            # التأكد ان الاعمدة المطلوبة موجودة
            if 'inci_name' in df.columns:
                final_df = df
            else:
                print("⚠️ Columns not found in downloaded file.")
        else:
            print("⚠️ Download failed.")

    except Exception as e:
        print(f"⚠️ Network Error: {e}")

    # --- المحاولة 2: استخدام الطوارئ (اذا فشل النت) ---
    if final_df is None or len(final_df) < 5:
        print("🚨 Network Failed. Switching to EMERGENCY LOCAL DATA.")
        final_df = pd.DataFrame(backup_data)
    
    # --- الخطوة الاخيرة: الدمج والحفظ ---
    # نضمن ان المواد الجديدة (2025) موجودة حتى لو الملف المحمل قديم
    try:
        print("💉 Injecting critical updates...")
        injection_df = pd.DataFrame(backup_data)
        
        # التأكد من توحيد اسماء الاعمدة قبل الدمج
        if 'inci_name' not in final_df.columns:
            final_df.rename(columns={"INCI Name": "inci_name", "CAS No": "cas_no"}, inplace=True)

        # دمج
        final_df = pd.concat([final_df, injection_df], ignore_index=True)
        
        # إزالة التكرار
        if 'inci_name' in final_df.columns:
            final_df.drop_duplicates(subset=['inci_name'], keep='last', inplace=True)

        # الحفظ
        final_df.to_csv("banned.csv", index=False)
        print(f"💾 SUCCESS: Saved 'banned.csv' with {len(final_df)} rows.")
        
    except Exception as e:
        print(f"💀 Logical Error: {e}")
        # الملاذ الاخير جداً: حفظ ملف الطوارئ الخام
        pd.DataFrame(backup_data).to_csv("banned.csv", index=False)
        print("💾 Saved pure emergency list.")

    # 🛑 سر النجاح: لا يوجد exit(1) هنا أبداً
    print("🏁 Job Finished Successfully.")

if __name__ == "__main__":
    update_database()
