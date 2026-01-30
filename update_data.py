import pandas as pd
import requests
from io import StringIO
import os
import sys

def real_update():
    print("🌐 Connecting to Official Database Source...")

    # هذا الرابط هو "مرآة" (Mirror) طبق الأصل لقاعدة بيانات الاتحاد الأوروبي
    # موجودة على GitHub (فرع main) وتتحدث اوتوماتيكياً
    # المصدر: OpenBeautyFacts (المصدر المفتوح المعتمد عالمياً)
    url = "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/main/cosing/csv/COSING_Annex_II_v2.csv"
    
    try:
        # 1. التحميل (بدون أي لف ودوران)
        response = requests.get(url, timeout=45)
        
        if response.status_code == 200:
            print("✅ Connection Established. Downloading...")
            
            # 2. القراءة الذكية (Smart Parsing)
            # engine='python' و sep=None: يخلي بايثون يكتشف الفاصلة وحده (سواء كانت ; أو ,)
            # هذا يحل مشكلة "الأسطر اللازكة" اللي طلعتلك قبل شويه
            df = pd.read_csv(StringIO(response.text), sep=None, engine='python', on_bad_lines='skip')
            
            # 3. التحقق من الحجم (Quality Control)
            # إذا الملف اقل من 500 مادة، معناه الملف المعروض بالسيرفر مضروب
            if len(df) < 500:
                print(f"⚠️ Error: Downloaded file is empty or too small ({len(df)} rows).")
                sys.exit(1) # نفصل فوراً، ما نجامل

            # 4. تنظيف العناوين
            df.columns = [str(c).strip().lower().replace(' ', '_') for c in df.columns]

            # 5. البحث عن الأعمدة وتوحيدها
            # ندور على اي عمود اسمه name ونسميه inci_name
            name_col = next((c for c in df.columns if 'name' in c or 'inn' in c), None)
            cas_col = next((c for c in df.columns if 'cas' in c), None)

            if name_col:
                df.rename(columns={name_col: 'inci_name', cas_col: 'cas_no'}, inplace=True)
                
                # إبقاء الأعمدة الصافية فقط
                if 'cas_no' not in df.columns: df['cas_no'] = ''
                final_df = df[['inci_name', 'cas_no']]
                
                # الحفظ
                final_df.to_csv("banned.csv", index=False)
                print(f"🎉 SUCCESS: Real Database Updated. Total Substances: {len(final_df)}")
            else:
                print("❌ Structure Error: Columns not found in the source file.")
                sys.exit(1)

        else:
            print(f"❌ Server Connection Failed: {response.status_code}")
            sys.exit(1)

    except Exception as e:
        print(f"💀 Fatal Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    real_update()
