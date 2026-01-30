import pandas as pd
import requests
import time
import random
import os

def update_database():
    print("🕵️‍♂️ Starting Stealth Update Protocol...")
    
    # قائمة المصادر (اذا فشل الاول يروح للثاني)
    sources = [
        # المصدر 1: البوابة المفتوحة للبيانات الأوروبية (ملف CSV مباشر ومستقر)
        {
            "type": "direct_csv",
            "url": "https://data.europa.eu/api/hub/store/data/cosing-annex-ii-v2.csv"
        },
        # المصدر 2: الموقع الرسمي (محاولة قراءة الجدول)
        {
            "type": "html_scrape",
            "url": "https://ec.europa.eu/growth/tools-databases/cosing/index.cfm?fuseaction=search.details_v2&id=1&annex_id=II&search"
        }
    ]

    # هيدر متصفح حقيقي (لتجنب الحظر)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    for source in sources:
        try:
            print(f"🔄 Trying Source: {source['type']}...")
            time.sleep(random.uniform(2, 5)) # تمويه

            if source["type"] == "direct_csv":
                # نجرب ننزل الملف مباشرة
                response = requests.get(source["url"], headers=headers, timeout=30, verify=False) # verify=False لتجاهل مشاكل SSL
                if response.status_code == 200:
                    with open("banned.csv", "wb") as f:
                        f.write(response.content)
                    print("✅ Success! Downloaded CSV directly.")
                    return # نطلع لأن نجحنا
                else:
                    print(f"❌ Failed with Status Code: {response.status_code}")

            elif source["type"] == "html_scrape":
                # نجرب نقرأ الجدول
                dfs = pd.read_html(source["url"])
                if len(dfs) > 0:
                    df = dfs[0]
                    df.to_csv("banned.csv", index=False)
                    print(f"✅ Success! Scraped Table with {len(df)} rows.")
                    return
                else:
                    print("❌ No tables found.")

        except Exception as e:
            print(f"⚠️ Error with source {source['type']}: {e}")
            continue # نجرب المصدر اللي بعده

    # إذا وصلنا هنا يعني كل المصادر فشلت
    print("🚨 FATAL ERROR: All sources failed.")
    exit(1) # هذا يخلي العلامة حمراء ب GitHub

if __name__ == "__main__":
    update_database()
