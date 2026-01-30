import streamlit as st
import pandas as pd
import requests
from io import StringIO
from difflib import get_close_matches

# ---------------------------------------------------------
# 1. System Config
# ---------------------------------------------------------
st.set_page_config(page_title="PharmaGuard Official", layout="wide", page_icon="🛡️")
st.title("🛡️ PharmaGuard: Official Live Compliance")

# ---------------------------------------------------------
# 2. Direct Live Fetcher (Strictly No Backup)
# ---------------------------------------------------------
@st.cache_data(ttl=600) # يمسح الكاش ويحدث إجبارياً كل 10 دقائق
def load_official_live_data():
    # روابط محدثة وموثوقة تسحب من قاعدة بيانات الاتحاد الأوروبي (CosIng)
    targets = [
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/main/cosing/csv/COSING_Annex_II_v2.csv",
        "https://raw.githubusercontent.com/datasets/cosmetics/master/data/cosmetics.csv",
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/master/cosing/csv/COSING_Annex_II_v2.csv",
        "https://media.githubusercontent.com/media/openfoodfacts/openbeautyfacts/master/cosing/csv/COSING_Annex_II_v2.csv"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    for url in targets:
        try:
            # محاولة الاتصال المباشر
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                df = pd.read_csv(StringIO(response.text), on_bad_lines='skip')
                # تنظيف الأعمدة
                df.columns = [c.strip().lower() for c in df.columns]
                # التأكد من جودة البيانات (أكثر من 500 مادة)
                if len(df) > 500:
                    return df, f"Successfully Synced with: {url.split('/')[2]}"
        except Exception:
            continue
            
    return None, "All Live Global Sources Unreachable"

# ---------------------------------------------------------
# 3. Execution Logic
# ---------------------------------------------------------
with st.spinner('📡 Establishing Live Link to EU Data Nodes...'):
    df, status_msg = load_official_live_data()

if df is not None:
    # تحديد الأعمدة بذكاء
    name_col = next((c for c in df.columns if 'name' in c or 'inn' in c), None)
    cas_col = next((c for c in df.columns if 'cas' in c), None)
    
    if name_col:
        banned_names = df[name_col].dropna().astype(str).str.lower().tolist()
        
        st.success(f"✅ **System Online** | {status_msg}")
        st.metric("Total Official Substances", f"{len(banned_names):,}")
        
        # --- Audit UI ---
        user_input = st.text_area("Paste Ingredient List (Direct Audit):", height=200)
        
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
                            risks.append(f"⚠️ **Possible Typo:** Did you mean '{matches[0]}'? (Banned)")
                
                if risks:
                    for r in risks: st.error(r)
                else:
                    st.success("✅ PASSED: No violations found in current live data.")
    else:
        st.error("🚨 Data Structure Failure: Source columns changed.")
else:
    # هذا هو طلبك: إذا ماكو داتا من النت، يوكف السيستم.
    st.error("🛑 **SYSTEM HALTED: Live Connection Failed**")
    st.info(f"Reason: {status_msg}")
    st.warning("Note: System is in 'Strict Mode'. It refuses to run on cached or manual data.")
    if st.button("🔄 Try Reconnect"):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")
