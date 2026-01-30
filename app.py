import streamlit as st
import pandas as pd
import requests
from io import StringIO
from difflib import get_close_matches

# 1. System Config
st.set_page_config(page_title="PharmaGuard Live", layout="wide", page_icon="📡")
st.title("📡 PharmaGuard: Real-Time Regulatory Auditor")

# 2. Real-Time Fetcher with Fail-Over (The Fix)
@st.cache_data(ttl=600)
def fetch_live_data():
    # قائمة المصادر (إذا واحد وكع، الثاني يشيل الحمل)
    sources = [
        # الرابط الجديد (الفرع الرئيسي - عادة هو الاصح)
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/main/cosing/COSING_Annex_II_v2.csv",
        # الرابط القديم (احتياط)
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/master/cosing/COSING_Annex_II_v2.csv",
        # رابط احتياطي ثالث بمسار مختلف
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/master/cosing/csv/COSING_Annex_II_v2.csv"
    ]
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36"}
    
    for url in sources:
        try:
            # محاولة الاتصال
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                # نجاح! نقرأ الداتا ونطلع من اللوب
                df = pd.read_csv(StringIO(response.text), on_bad_lines='skip')
                df.columns = [c.strip().lower() for c in df.columns]
                return df, f"Connected to Live Branch ({url.split('/')[-3]})" # يرجع اسم الفرع main/master
        except Exception:
            continue # فشل هذا الرابط؟ جرب البعده فوراً
            
    return None, "All Sources Failed"

# 3. Execution
with st.spinner('📡 Establishing Secure Connection to EU Database...'):
    df, status_msg = fetch_live_data()

if df is not None:
    # --- النجاح ---
    name_col = next((c for c in df.columns if 'name' in c or 'inn' in c), None)
    cas_col = next((c for c in df.columns if 'cas' in c), None)
    
    if name_col:
        banned_names = df[name_col].dropna().astype(str).str.lower().tolist()
        banned_cas = df[cas_col].dropna().astype(str).tolist() if cas_col else []
        
        st.success(f"✅ **System Online:** {status_msg}")
        st.info(f"🛡️ **Live Database:** Monitoring **{len(banned_names)}** prohibited substances (Annex II).")
        
        # --- الفحص ---
        col1, col2 = st.columns([2, 1])
        with col1:
            user_input = st.text_area("Paste Ingredient List:", height=150, placeholder="Aqua, Glycerin, Hydroquinone...")
            if st.button("🚀 Run Live Audit"):
                if user_input:
                    risks = []
                    ingredients = [x.strip().lower() for x in user_input.replace('\n', ',').split(',')]
                    for item in ingredients:
                        if len(item) < 2: continue
                        if item in banned_names:
                            risks.append(f"❌ **BANNED:** {item}")
                        elif item in banned_cas:
                            risks.append(f"❌ **BANNED ID:** {item}")
                        else:
                            matches = get_close_matches(item, banned_names, n=1, cutoff=0.85)
                            if matches:
                                risks.append(f"⚠️ **Possible Typo:** Did you mean '{matches[0]}'? It is BANNED.")
                    
                    if risks:
                        for r in risks: st.error(r)
                    else:
                        st.success("✅ Clean: No banned substances found.")
        
        with col2:
            st.caption("ℹ️ Data is fetched directly from OpenBeautyFacts repositories. Refreshes every 10 mins.")

    else:
        st.error("🚨 Source Format Error: Columns mismatch.")
else:
    # --- الفشل ---
    st.error(f"📡 {status_msg}")
    st.warning("Debugging: All 3 external links are unreachable. GitHub might be down or blocking the request.")
