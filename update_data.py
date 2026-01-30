import pandas as pd
import requests
import time
import random
from io import StringIO
import os

def update_database():
    # 1. التمويه: ننتظر وقت عشوائي بين 2 و 10 ثواني (كأننا بشر)
    sleep_time = random.uniform(2, 10)
    print(f"🕵️‍♂️ Waiting for {sleep_time:.2f} seconds to avoid detection...")
    time.sleep(sleep_time)

    # 2. الرابط الرسمي المباشر للاتحاد الأوروبي (Annex II)
    # ملاحظة: هذا الرابط قد يتغير مستقبلاً، لذا وضعنا كود يكشف الخطأ
    url = "https://ec.europa.eu/growth/tools-databases/cosing/index.cfm?fuseaction=search.details_v2&id=1&annex_id=II&search"
    
    # رابط بديل مباشر في حال فشل الأول (من بوابة البيانات المفتوحة)
    backup_url = "https://data.europa.eu/api/hub/store/data/cosing-annex-ii-v2.csv"

    print("🚀 Connecting to EU Server...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # محاولة قراءة الجدول مباشرة من الصفحة (أقوى طريقة)
        # نقرأ كل الجداول في الصفحة، وعادة الجدول الكبير هو المطلوب
        dfs = pd.read_html(url)
        df = dfs[0] # الجدول الأول
        
        # حفظ الملف
        df.to_csv("banned.csv", index=False)
        print(f"✅ Success! Updated 'banned.csv' with {len(df)} substances.")
        
    except Exception as e:
        print(f"⚠️ Primary method failed: {e}")
        print("🔄 Trying backup method...")
        try:
            response = requests.get(backup_url, headers=headers, timeout=15)
            if response.status_code == 200:
                with open("banned.csv", "wb") as f:
                    f.write(response.content)
                print("✅ Backup Success! File saved.")
            else:
                print("❌ Backup failed.")
                exit(1) # نخرج بخطأ حتى GitHub ينبهنا
        except Exception as e2:
            print(f"❌ Critical Error: {e2}")
            exit(1)

if __name__ == "__main__":
    update_database()
