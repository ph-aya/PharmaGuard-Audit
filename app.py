import streamlit as st
import pandas as pd
import requests
from io import StringIO
from difflib import get_close_matches

# ---------------------------------------------------------
# 1. System Config
# ---------------------------------------------------------
st.set_page_config(page_title="PharmaGuard Auto-Sync", layout="wide", page_icon="📡")
st.title("📡 PharmaGuard: Autonomous Regulatory Auditor")
st.caption("System Status: Auto-Fetching from Global Repositories...")

# ---------------------------------------------------------
# 2. The "Hunter" Engine (Auto-Fetch Logic)
# ---------------------------------------------------------
@st.cache_data(ttl=3600)  # يحدث البيانات كل ساعة تلقائياً
def fetch_live_data():
    # قائمة الأهداف: روابط مباشرة للداتا (اذا واحد مات، الثاني يشتغل)
    targets = [
        # الرابط الأكثر استقراراً (Dataset Mirror)
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/main/cosing/csv/COSING_Annex_II_v2.csv",
        # المصدر الثاني (Backup Branch)
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/master/cosing/csv/COSING_Annex_II_v2.csv",
        # المصدر الثالث (Old Structure)
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/main/cosing/COSING_Annex_II_v2.csv",
        # المصدر الرابع (Raw Data Backup)
        "https://raw.githubusercontent.com/datasets/cosmetics/master/data/cosmetics.csv"
    ]
    
    # التمويه (حتى السيرفر عباله احنا متصفح مو كود)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    for url in targets:
        try:
            # محاولة الاتصال
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # قراءة الملف
                csv_data = StringIO(response.text)
                df = pd.read_csv(csv_data, on_bad_lines='skip')
                
                # تنظيف أسماء الأعمدة (Normalization)
                df.columns = [c.strip().lower() for c in df.columns]
                
                # التأكد من أن الملف يحتوي على داتا حقيقية مو فارغ
                if len(df) > 100:
                    return df, f"Successfully Synced with: {url.split('/')[2]} Repo"
                    
        except Exception as e:
            continue # فشل هذا الرابط؟ طز، جرب اللي بعده
            
    return None, "All Targets Failed"

# ---------------------------------------------------------
# 3. Execution & Interface
# ---------------------------------------------------------
with st.spinner('📡 Connecting to EU Data Nodes...'):
    df, status_msg = fetch_live_data()

if df is not None:
    # الذكاء في تحديد الأعمدة (Smart Column Detection)
    # يدور على العمود اللي بي كلمة name أو inn
    name_col = next((c for c in df.columns if 'name' in c or 'inn' in c), None)
    # يدور على العمود اللي بي كلمة cas
    cas_col = next((c for c in df.columns if 'cas' in c), None)
    
    if name_col:
        # تحضير قوائم البحث
        banned_names = df[name_col].dropna().astype(str).str.lower().tolist()
        banned_cas = df[cas_col].dropna().astype(str).tolist() if cas_col else []
        
        # واجهة النجاح
        st.success(f"✅ **Online & Ready** | {status_msg}")
        st.metric("Active Prohibitions Monitored", f"{len(banned_names):,}")
        
        # --- منطقة الفحص ---
        col1, col2 = st.columns([2, 1])
        
        with col1:
            user_input = st.text_area("Paste Ingredients Here:", height=200, placeholder="Aqua, Glycerin, Hydroquinone...")
            
            if st.button("🚀 Audit Now"):
                if user_input:
                    risks = []
                    ingredients = [x.strip().lower() for x in user_input.replace('\n', ',').split(',')]
                    
                    for item in ingredients:
                        if len(item) < 2: continue
                        
                        # 1. Exact Match
                        if item in banned_names:
                            risks.append(f"❌ **BANNED:** {item}")
                        
                        # 2. CAS Match
                        elif item in banned_cas:
                            risks.append(f"❌ **BANNED ID (CAS):** {item}")
                        
                        # 3. Fuzzy Logic (AI)
                        else:
                            matches = get_close_matches(item, banned_names, n=1, cutoff=0.85)
                            if matches:
                                risks.append(f"⚠️ **Typo Detected:** Did you mean '{matches[0]}'? It is BANNED.")
                    
                    if risks:
                        st.error(f"Found {len(risks)} Violations!")
                        for r in risks: st.write(r)
                    else:
                        st.success("✅ PASSED: No banned substances found in live database.")
                else:
                    st.warning("Input is empty.")
                    
        with col2:
            st.info("ℹ️ **System Info**")
            st.write("This tool autonomously fetches the latest 'Annex II' regulations from open-source mirrors of the EU Commission data.")
            st.write(f"**Update Interval:** Hourly")

    else:
        st.error("🚨 Data Structure Error: Could not identify 'Name' column in the fetched file.")
else:
    # هذا الإيرر يطلع بس إذا انقطعت الانترنت عن الكوكب كله
    st.error("📡 Connection Error: Unable to fetch data from any source.")
    st.warning("Please check Streamlit Cloud logs.")
