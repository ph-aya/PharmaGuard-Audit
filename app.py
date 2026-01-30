import streamlit as st
import pandas as pd
import requests
from io import StringIO
from difflib import get_close_matches

# 1. إعدادات الصفحة
st.set_page_config(page_title="PharmaGuard Official", layout="wide", page_icon="🛡️")
st.title("🛡️ PharmaGuard: Official EU Compliance")

# 2. محرك الجلب المباشر (No Internal Data)
@st.cache_data(ttl=3600)
def load_official_data():
    # هذه الروابط هي الـ Endpoints الوحيدة اللي توفر CSV للسوق الأوروبي حالياً
    urls = [
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/main/cosing/csv/COSING_Annex_II_v2.csv",
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/master/cosing/csv/COSING_Annex_II_v2.csv"
    ]
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                df = pd.read_csv(StringIO(response.text), on_bad_lines='skip')
                df.columns = [c.strip().lower() for c in df.columns]
                # نرجع الداتا واسم المصدر (بدون باك اب)
                return df, f"Live EU Database ({url.split('/')[-3]})"
        except Exception:
            continue
            
    return None, "Connection Failed"

# تشغيل الجلب
with st.spinner('📡 Syncing with EU Official Records...'):
    df, source_status = load_official_data()

if df is not None:
    # تحديد الأعمدة
    name_col = next((c for c in df.columns if 'name' in c or 'inn' in c), None)
    cas_col = next((c for c in df.columns if 'cas' in c), None)
    
    if name_col:
        banned_names = df[name_col].dropna().astype(str).str.lower().tolist()
        banned_cas = df[cas_col].dropna().astype(str).tolist() if cas_col else []
        
        # عرض الحالة الحقيقية (العدد لازم يكون فوق الـ 1500)
        st.success(f"🟢 System Online | {source_status}")
        st.metric("Total Substances Monitored", len(banned_names))
        
        # واجهة الفحص
        col1, col2 = st.columns([2, 1])
        with col1:
            user_input = st.text_area("Paste Ingredient List:", height=200)
            if st.button("🚀 Run Audit", type="primary"):
                if user_input:
                    risks = []
                    ingredients = [x.strip().lower() for x in user_input.replace('\n', ',').split(',')]
                    for item in ingredients:
                        if len(item) < 2: continue
                        if item in banned_names:
                            risks.append(f"❌ **BANNED:** {item}")
                        elif item in banned_cas:
                            risks.append(f"❌ **BANNED (CAS):** {item}")
                        else:
                            matches = get_close_matches(item, banned_names, n=1, cutoff=0.85)
                            if matches:
                                risks.append(f"⚠️ **Typo?** Did you mean '{matches[0]}'?")
                    
                    if risks:
                        for r in risks: st.error(r)
                    else:
                        st.success("✅ PASSED: No violations found in current official data.")
    else:
        st.error("🚨 Source Structure Error.")
else:
    # هنا الحقيقة: إذا ماكو نت، يوكف السيستم وما يشتغل على 8 مواد
    st.error("🛑 CRITICAL ERROR: Could not reach Live Database.")
    st.info("The system is configured to ONLY use official live data. Please check your network or Streamlit Cloud status.")

st.markdown("---")
st.caption("PharmaGuard v2.5 | Strictly Autonomous & Official")
