import streamlit as st
import pandas as pd
import requests
from io import StringIO
from difflib import get_close_matches

st.set_page_config(page_title="Official EU Auditor", layout="wide", page_icon="🇪🇺")
st.title("🇪🇺 PharmaGuard: Official Live Auditor")

# ---------------------------------------------------------
# 2. The Global Live Fetcher (No Backups - Strictly Live)
# ---------------------------------------------------------
@st.cache_data(ttl=600)
def fetch_live_official_data():
    # روابط الـ Third Party اللي تسحب من الموقع الرسمي (حصراً)
    targets = [
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/main/cosing/csv/COSING_Annex_II_v2.csv",
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/master/cosing/csv/COSING_Annex_II_v2.csv",
        "https://media.githubusercontent.com/media/openfoodfacts/openbeautyfacts/master/cosing/csv/COSING_Annex_II_v2.csv",
        "https://raw.githubusercontent.com/datasets/cosmetics/master/data/cosmetics.csv"
    ]
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    
    for url in targets:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                df = pd.read_csv(StringIO(response.text), on_bad_lines='skip')
                df.columns = [c.strip().lower() for c in df.columns]
                return df, f"Successfully Synced with Global Node: {url.split('/')[2]}"
        except:
            continue
            
    return None, "CRITICAL: All Live Sources Unreachable."

# ---------------------------------------------------------
# 3. Execution Logic
# ---------------------------------------------------------
with st.spinner('📡 Establishing Live Connection to EU Repositories...'):
    df, status_msg = fetch_live_official_data()

if df is not None:
    # تحديد الأعمدة
    name_col = next((c for c in df.columns if 'name' in c or 'inn' in c), None)
    cas_col = next((c for c in df.columns if 'cas' in c), None)
    
    if name_col:
        banned_names = df[name_col].dropna().astype(str).str.lower().tolist()
        banned_cas = df[cas_col].dropna().astype(str).tolist() if cas_col else []
        
        st.success(f"✅ **System Live:** {status_msg}")
        st.metric("Total Substances (Annex II)", f"{len(banned_names):,}")
        
        # --- Audit UI ---
        user_input = st.text_area("Paste Ingredient List:", height=200)
        
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
                            risks.append(f"⚠️ **Possible Typo:** Did you mean '{matches[0]}'? (Banned)")
                
                if risks:
                    for r in risks: st.error(r)
                else:
                    st.success("✅ PASSED: No violations found in current official data.")
    else:
        st.error("🚨 Data Structure Error: EU file format changed.")
else:
    # هذا هو طلبك: إذا ماكو داتا من النت، يوكف السيستم.
    st.error("🛑 **SYSTEM HALTED: Live Connection Failed**")
    st.info(f"Reason: {status_msg}")
    st.warning("Note: System is in 'Strict Mode'. It refuses to run on cached or manual data.")
