import streamlit as st
import pandas as pd
import requests
from io import StringIO
from difflib import get_close_matches

# ---------------------------------------------------------
# 1. System Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="PharmaGuard Audit", 
    layout="wide", 
    page_icon="🛡️"
)

st.title("🛡️ PharmaGuard: Live Compliance Auditor")

# ---------------------------------------------------------
# 2. The "Tank" Engine (Robust Data Loader)
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def load_data():
    # محاولة 1: روابط محدثة (جربنا مسارات مختلفة لضمان الوصول)
    possible_urls = [
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/main/cosing/csv/COSING_Annex_II_v2.csv",
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/master/cosing/csv/COSING_Annex_II_v2.csv",
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/main/cosing/COSING_Annex_II_v2.csv"
    ]
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36"}
    
    for url in possible_urls:
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                # إذا نجح الاتصال، نحول النص إلى داتا ونطلع
                df = pd.read_csv(StringIO(response.text), on_bad_lines='skip')
                # تنظيف أسماء الأعمدة لضمان التطابق
                df.columns = [c.strip().lower() for c in df.columns]
                return df, "Live Cloud Database"
        except Exception:
            continue # فشل الرابط؟ نعبر عالبعده
            
    # محاولة 2: وضع الطوارئ (Emergency Backup)
    # في حال كل الروابط فشلت، نستخدم داتا مخزونة هنا
    emergency_csv = """Reference number,Chemical name / INN,CAS Number
    1183,Hydroquinone,123-31-9
    1370,Clobetasol propionate,25122-46-7
    386,Mercury,7439-97-6
    4a,Tretinoin (Retinoic acid),302-79-4
    12,Betamethasone,378-44-9
    3,Corticosteroids (Glucocorticoids),
    1120,Chloroform,67-66-3
    198,Phenol,108-95-2
    """
    df = pd.read_csv(StringIO(emergency_csv))
    df.columns = [c.strip().lower() for c in df.columns]
    return df, "Internal Backup (Offline Mode)"

# تحميل البيانات وتشغيل المحرك
with st.spinner('Syncing Regulatory Data...'):
    df, source_status = load_data()
    
    # عرض الحالة خارج الدالة لتجنب الخطأ
    if "Backup" in source_status:
        st.toast("⚠️ Network Error. Using Internal Backup.", icon="🟠")
    else:
        st.toast(f"✅ Live Data Connected", icon="🟢")
        
    st.markdown(f"**Status:** 🟢 System Online | **Source:** {source_status}")

# ---------------------------------------------------------
# 3. Data Processing & Search Logic
# ---------------------------------------------------------
# تحديد الأعمدة الصحيحة أوتوماتيكياً
name_col = next((c for c in df.columns if 'name' in c or 'inn' in c), None)
cas_col = next((c for c in df.columns if 'cas' in c), None)

if name_col:
    # تحويل الداتا لقوائم للبحث السريع
    banned_names = df[name_col].dropna().astype(str).str.lower().tolist()
    banned_cas = df[cas_col].dropna().astype(str).tolist() if cas_col else []

    # ---------------------------------------------------------
    # 4. User Interface
    # ---------------------------------------------------------
    col1, col2 = st.columns([2, 1])

    with col1:
        user_input = st.text_area("Paste Ingredient List (Comma Separated):", height=200, 
                                placeholder="Example: Aqua, Glycerin, Hydroquinone, 123-31-9...")
        
        if st.button("🚀 Run Compliance Audit", type="primary"):
            if user_input:
                risks = []
                # تنظيف المدخلات
                ingredients = [x.strip().lower() for x in user_input.replace('\n', ',').split(',')]
                
                for item in ingredients:
                    if len(item) < 2: continue
                    
                    # 1. تطابق تام بالاسم
                    if item in banned_names:
                        risks.append(f"❌ **CRITICAL:** '{item}' is BANNED (Exact Match).")
                        continue
                        
                    # 2. تطابق برقم CAS
                    if item in banned_cas:
                        risks.append(f"❌ **CRITICAL (CAS):** ID '{item}' is a banned substance.")
                        continue

                    # 3. الذكاء الاصطناعي (تصحيح الأخطاء)
                    matches = get_close_matches(item, banned_names, n=1, cutoff=0.85)
                    if matches:
                        risks.append(f"⚠️ **Typo Detected:** Did you mean '{matches[0]}'? It is BANNED.")
                
                # عرض النتائج
                st.markdown("---")
                if risks:
                    st.error(f"🚫 FAILED: Found {len(risks)} compliance violations.")
                    for r in risks: st.markdown(r)
                else:
                    st.success("✅ PASSED: No banned substances found in current database.")
                    st.caption("Note: Always verify with official EU CosIng documents.")
            else:
                st.warning("Please enter data to scan.")

    with col2:
        st.info("📊 **Audit Stats**")
        st.write(f"Database Size: {len(banned_names)} substances")
        st.write("Standards: EU Annex II")
        st.markdown("---")
        with st.expander("ℹ️ How it works"):
            st.write("This tool automatically scans ingredient lists against the EU CosIng Annex II database of prohibited substances. It uses fuzzy logic to detect misspellings.")

else:
    st.error("🚨 Critical Data Error: Could not parse database columns.")
    st.stop()

# Footer
st.markdown("---")
st.caption("PharmaGuard v2.1 | Engineered for Regulatory Agility")