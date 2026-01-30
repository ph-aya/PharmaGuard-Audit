import pandas as pd
import requests
from io import StringIO
import os
import sys

def cdn_update():
    print("⚡ Starting CDN Bypass Protocol (jsDelivr)...")

    # نستخدم شبكة توصيل محتوى (CDN) بدلاً من الرابط المباشر
    # هذه الشبكة لا تحظر الروبوتات وسريعة جداً
    cdn_url = "https://cdn.jsdelivr.net/gh/openfoodfacts/openbeautyfacts@main/cosing/csv/COSING_Annex_II_v2.csv"
    
    # رابط احتياطي ثاني
    backup_url = "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/main/cosing/csv/COSING_Annex_II_v2.csv"

    final_df = None

    # دالة محاولة التحميل
    def try_download(target_url, source_name):
        try:
            print(f"📡 Contacting {source_name}...")
            response = requests.get(target_url, timeout=30)
            if response.status_code == 200:
                # قراءة ذكية للفواصل
                data = pd.read_csv(StringIO(response.text), sep=None, engine='python', on_bad_lines='skip')
                if len(data) > 500:
                    print(f"✅ Success from {source_name}! Got {len(data)} rows.")
                    return data
                else:
                    print(f"⚠️ File too small from {source_name}.")
            else:
                print(f"❌ Status {response.status_code} from {source_name}.")
        except Exception as e:
            print(f"⚠️ Error from {source_name}: {e}")
        return None

    # 1. المحاولة الأولى: عبر الـ CDN
    final_df = try_download(cdn_url, "CDN Mirror")

    # 2. المحاولة الثانية: عبر المصدر المباشر (اذا فشل الاول)
    if final_df is None:
        print("🔄 Switching to Direct Source...")
        final_df = try_download(backup_url, "GitHub Raw")

    # 3. مرحلة الحفظ (The Safety Lock)
    if final_df is not None:
        # تنظيف العناوين
        final_df.columns = [str(c).strip().lower().replace(' ', '_') for c in final_df.columns]
        
        # توحيد الأسماء
        name_col = next((c for c in final_df.columns if 'name' in c or 'inn' in c), None)
        cas_col = next((c for c in final_df.columns if 'cas' in c), None)

        if name_col:
            final_df.rename(columns={name_col: 'inci_name', cas_col: 'cas_no'}, inplace=True)
            
            # 💉 حقن المواد الجديدة 2025 (لضمان الحداثة)
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
            
            # دمج وحذف التكرار
            if 'cas_no' not in final_df.columns: final_df['cas_no'] = ''
            final_df = pd.concat([final_df, new_bans], ignore_index=True)
            final_df.drop_duplicates(subset=['inci_name'], keep='last', inplace=True)
            
            # حفظ الملف
            final_df.to_csv("banned.csv", index=False)
            print(f"💾 SAVED 'banned.csv' with {len(final_df)} entries.")
            sys.exit(0) # خروج ناجح
        else:
            print("❌ Column mismatch in downloaded file.")
            sys.exit(1)
    else:
        # إذا فشل كل شيء، لا تمسح الملف القديم!
        # نخرج بخطأ لكن نبقي الملف القديم كما هو (اذا كان موجوداً)
        print("🚨 ALL DOWNLOADS FAILED. Keeping old file if exists.")
        sys.exit(1)

if __name__ == "__main__":
    cdn_update()
