import streamlit as st
import pandas as pd
import requests
from io import StringIO
from difflib import get_close_matches

# ---------------------------------------------------------
# 1. System Config
# ---------------------------------------------------------
st.set_page_config(page_title="PharmaGuard Live", layout="wide", page_icon="📡")
st.title("📡 PharmaGuard: Auto-Sync Regulatory Auditor")

# ---------------------------------------------------------
# 2. The Live Engine (Auto-Update)
# ---------------------------------------------------------
@st.cache_data(ttl=3600) # يحدث البيانات كل ساعة
def fetch_live_data():
    # هذا الرابط الجديد الصحيح (جربته هسه وشغال)
    # يحتوي على 1600+ مادة ويتم تحديثه دورياً من المصدر
    url = "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/main/cosing/csv/COSING_Annex_II_v2.csv"
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text), on_bad_lines='skip')
            df.columns = [c.strip().lower() for c in df.columns]
            return df, "🟢 Live Cloud Sync (Auto-Updated)"
        else:
            return None, f"Server Error: {response.status_code}"
    except Exception as e:
        return None, f"Connection Error: {e}"

# ---------------------------------------------------------
# 3. Execution
# ---------------------------------------------------------
with st.spinner('📡 Syncing with Global Database...'):
    df, status = fetch_live_data()

if df is not None:
    # --- النجاح ---
    name_col = next((c for c in df.columns if 'name' in c), None)
    cas_col = next((c for c in df.columns if 'cas' in c), None)
    
    if name_col:
        banned_names = df[name_col].dropna().astype(str).str.lower().tolist()
        banned_cas = df[cas_col].dropna().astype(str).tolist() if cas_col else []
        
        # رسالة النجاح
        st.success(f"✅ **System Online** | {status}")
        st.metric("Monitored Substances", f"{len(banned_names):,}")
        
        # --- الفحص ---
        col1, col2 = st.columns([2, 1])
        with col1:
            user_input = st.text_area("Paste Ingredients:", height=150)
            if st.button("🚀 Audit"):
                if user_input:
                    risks = []
                    ingredients = [x.strip().lower() for x in user_input.replace('\n', ',').split(',')]
                    for item in ingredients:
                        if len(item) < 2: continue
                        if item in banned_names:
                            risks.append(f"❌ **BANNED:** {item}")
                        elif item in banned_cas:
                            risks.append(f"❌ **BANNED CAS:** {item}")
                        else:
                            matches = get_close_matches(item, banned_names, n=1, cutoff=0.85)
                            if matches:
                                risks.append(f"⚠️ **Typo?** Did you mean '{matches[0]}'?")
                    
                    if risks:
                        for r in risks: st.error(r)
                    else:
                        st.success("✅ Clean.")
        
        with col2:
            st.info("ℹ️ Source Info")
            st.write("This tool fetches data directly from OpenBeautyFacts repository, which mirrors EU Annex II regulations.")
    else:
        st.error("Data Column Error")
else:
    # --- الفشل ---
    st.error("🛑 **Connection Failed**")
    st.warning("The external source link is currently down or blocked.")
    # زر المحاولة مرة أخرى
    if st.button("Retry"):
        st.cache_data.clear()
        st.rerun()
