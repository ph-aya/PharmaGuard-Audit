import pandas as pd
import requests
from io import StringIO

def update_database():
    print("🚀 Starting Force-Update Protocol...")

    # الرابط المعتمد (OpenFoodFacts) - عادة يكون مفصول بفواصل
    url = "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/master/cosing/csv/COSING_Annex_II_v2.csv"
    
    try:
        print("📥 Downloading Database...")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            # 🛑 السر هنا: sep=None يخلي بايثون يشم الفاصلة واكتشافها اوتوماتيكياً
            df = pd.read_csv(StringIO(response.text), sep=None, engine='python', on_bad_lines='skip')
            
            print(f"✅ Raw Data Loaded: {len(df)} rows.")

            # تنظيف العناوين (مسح المسافات وتوحيد الحروف)
            df.columns = [str(c).strip().lower().replace(' ', '_').replace('.', '') for c in df.columns]

            # البحث عن العمود الصحيح للاسم
            # نحاول نلكه اي عمود بي كلمة name او inn
            name_col = next((c for c in df.columns if 'name' in c or 'inn' in c), None)
            cas_col = next((c for c in df.columns if 'cas' in c), None)

            if name_col is None:
                print("❌ Column Error: Could not find Name column.")
                exit(1)

            # توحيد اسماء الاعمدة للشكل المطلوب
            df.rename(columns={name_col: 'inci_name', cas_col: 'cas_no'}, inplace=True)

            # 💉 حقن المواد الجديدة 2025 (التحديث اليدوي)
            print("💉 Injecting 2025 Updates...")
            new_bans = pd.DataFrame([
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
            ])

            # دمج الملفين
            final_df = pd.concat([df, new_bans], ignore_index=True)
            
            # فلترة الأعمدة: نبقي فقط الاسم والرقم
            if 'cas_no' in final_df.columns:
                final_df = final_df[['inci_name', 'cas_no']]
            else:
                final_df = final_df[['inci_name']]

            # إزالة التكرار
            final_df.drop_duplicates(subset=['inci_name'], inplace=True)

            # الحفظ
            final_df.to_csv("banned.csv", index=False)
            print(f"💾 SUCCESS: Saved 'banned.csv' with {len(final_df)} unique substances.")

        else:
            print(f"❌ HTTP Error: {response.status_code}")
            exit(1)

    except Exception as e:
        print(f"🚨 Script Crashed: {e}")
        exit(1)

if __name__ == "__main__":
    update_database()
