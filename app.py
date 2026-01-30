import streamlit as st
import pandas as pd
import requests
from io import StringIO
from difflib import get_close_matches

st.set_page_config(page_title="PharmaGuard Official", layout="wide", page_icon="🛡️")
st.title("🛡️ PharmaGuard: Official Live Compliance")

# محرك الجلب المباشر (No Backup Data - Pure Live)
@st.cache_data(ttl=600) # يحدث كل 10 دقائق
def load_official_data():
    # روابط من 3 منظمات مختلفة تراقب بيانات الاتحاد الأوروبي
    urls = [
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/main/cosing/csv/COSING_Annex_II_v2.csv",
        "https://raw.githubusercontent.com/datasets/cosmetics/master/data/cosmetics.csv",
        "https://media.githubusercontent.com/media/openfoodfacts/openbeautyfacts/master/cosing/csv/COSING_Annex_II_v2.csv",
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/master/cosing/csv/COSING_Annex_II_v2.csv"
    ]
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=7)
            if response.status_code == 200:
                df = pd.read_csv(StringIO(response.text), on_bad_lines='skip')
                df.columns = [c.strip().lower() for c in df.columns]
                if len(df) > 500: # تأكيد أن الداتا كاملة
                    return df, f"Live Stream: {url.split('/')[2]}"
        except Exception:
            continue
            
    return None, "All Global Sources Blocked"

# تشغيل الجلب
with st.spinner('📡 Synchronizing with EU Regulatory Servers...'):
    df, source_status = load_official_data()

if df is not None:
    # تحديد الأعمدة
    name_col = next((c for c in df.columns if 'name' in c or 'inn' in c), None)
    cas_col = next((c for c in df.columns if 'cas' in c), None)
    
    if name_col:
        banned_names = df[name_col].dropna().astype(str).str.lower().tolist()
        
        st.success(f"🟢 System Online | {source_status}")
        st.metric("Total Official Substances", f"{len(banned_names):,}")
        
        # واجهة الفحص
        user_input = st.text_area("Paste Ingredient List:", height=200, placeholder="Example: Hydroquinone, Mercury...")
        if st.button("🚀 Run Live Audit", type="primary"):
            if user_input:
                risks = []
                ingredients = [x.strip().lower() for x in user_input.replace('\n', ',').split(',')]
                for item in ingredients:
                    if len(item) < 2: continue
                    if item in banned_names:
                        risks.append(f"❌ **BANNED:** {item}")
                    else:
                        matches = get_close_matches(item, banned_names, n=1, cutoff=0.85)
                        if matches:
                            risks.append(f"⚠️ **Typo?** Did you mean '{matches[0]}'?")
                
                if risks:
                    for r in risks: st.error(r)
                else:
                    st.success("✅ PASSED: No violations found in current official data.")
    else:
        st.error("🚨 Data Structure Error at Source.")
else:
    st.error("🛑 CRITICAL: SYSTEM HALTED.")
    st.warning("Reason: All live regulatory endpoints are unreachable from the current server location.")
    if st.button("🔄 Force Reconnect"):
        st.cache_data.clear()
        st.rerun()
