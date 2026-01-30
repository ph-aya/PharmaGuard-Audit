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
    # Priority 1: The Local Bundle (أسرع وأضمن طريقة)
    # إذا رفعتي ملف banned.csv للغتهب، هذا راح يشتغل فوراً
    try:
        df = pd.read_csv("banned.csv")
        # تنظيف الأعمدة
        df.columns = [c.strip().lower() for c in df.columns]
        return df, "Local Repo Database (Fastest)"
    except FileNotFoundError:
        pass # إذا الملف ما موجود، نحاول نجيبه من النت

    # Priority 2: Corrected Cloud Links (الروابط المصححة)
    possible_urls = [
        # الرابط الصحيح مع النقطة بدلاً من الشخط
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/master/cosing/COSING_Annex.II_v2.csv",
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/main/cosing/COSING_Annex.II_v2.csv"
    ]
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36"}
    
    for url in possible_urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                df = pd.read_csv(StringIO(response.text), on_bad_lines='skip')
                df.columns = [c.strip().lower() for c in df.columns]
                return df, "Live Cloud Database"
        except Exception:
            continue
            
    # Priority 3: Emergency Backup (في حال كل شيء فشل)
    # نستخدم هذا فقط إذا نسيتي ترفعين ملف banned.csv
    return None, "FAILED"

# تحميل البيانات
with st.spinner('Initializing PharmaGuard AI...'):
    df, source_status = load_data()

# التعامل مع الفشل التام
if df is None:
    st.error("🚨 Critical Error: Database Not Found.")
    st.info("💡 Action: Please upload the file 'banned.csv' to your GitHub repository.")
    st.stop()

# عرض الحالة
if "Local" in source_status:
    st.toast("✅ Database Loaded Locally (Super Fast)", icon="⚡")
elif "Live" in source_status:
    st.toast("✅ Connected to Live Server", icon="🟢")

st.markdown(f"**Status:** 🟢 System Online | **Source:** {source_status}")

# ---------------------------------------------------------
# 3. Data Processing & Search Logic
# ---------------------------------------------------------
# البحث الذكي عن الأعمدة (لأن الملفات تختلف أسماؤها)
name_col = next((c for c in df.columns if 'name' in c or 'inn' in c), None)
cas_col = next((c for c in df.columns if 'cas' in c), None)

if name_col:
    # تحويل البيانات إلى قوائم للمعالجة
    banned_names = df[name_col].dropna().astype(str).str.lower().tolist()
    banned_cas = df[cas_col].dropna().astype(str).tolist() if cas_col else []
    
    db_size = len(banned_names)

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
                ingredients = [x.strip().lower() for x in user_input.replace('\n', ',').split(',')]
                
                for item in ingredients:
                    if len(item) < 2: continue
                    
                    # 1. Exact Name Match
                    if item in banned_names:
                        risks.append(f"❌ **CRITICAL:** '{item}' is BANNED in EU Annex II.")
                        continue
                        
                    # 2. CAS Number Match
                    if item in banned_cas:
                        risks.append(f"❌ **CRITICAL (CAS):** ID '{item}' is a banned substance.")
                        continue

                    # 3. Fuzzy Logic (AI Typo Detection)
                    # نستخدم الذكاء فقط إذا لم نجد تطابق تام
                    matches = get_close_matches(item, banned_names, n=1, cutoff=0.85)
                    if matches:
                        risks.append(f"⚠️ **Typo Detected:** Did you mean '{matches[0]}'? It is BANNED.")
                
                st.markdown("---")
                if risks:
                    st.error(f"🚫 FAILED: Found {len(risks)} compliance violations.")
                    for r in risks: st.markdown(r)
                else:
                    st.success("✅ PASSED: No banned substances found.")
                    st.caption("Disclaimer: Verify with official EU CosIng documents.")
            else:
                st.warning("Please enter ingredients to scan.")

    with col2:
        st.info("📊 **Live Database Stats**")
        st.metric(label="Banned Substances Loaded", value=f"{db_size:,}")
        st.write("Standard: EU CosIng Annex II")
        st.markdown("---")
        with st.expander("ℹ️ How it works"):
            st.write("This tool scans against the official EU list of prohibited substances using Python & Fuzzy Logic.")

else:
    st.error("🚨 Data Error: Could not parse columns from the CSV file.")
    st.stop()

# Footer
st.markdown("---")
st.caption("PharmaGuard v3.0 | Engineered for Regulatory Agility")
