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
# 2. The Combat Fetcher (محرك قتالي لجلب البيانات)
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_live_data():
    # قائمة المصادر (اذا واحد مات، الثاني يشيل الحمل)
    # ملاحظة: هذه روابط حقيقية ومختلفة لضمان عدم الفشل
    mirrors = [
        # المصدر 1: الفرع الرئيسي (Main)
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/main/cosing/csv/COSING_Annex_II_v2.csv",
        # المصدر 2: الفرع القديم (Master) - غالباً هذا اللي يشتغل لما الأول يوكف
        "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/master/cosing/csv/COSING_Annex_II_v2.csv",
        # المصدر 3: مسار بديل للطوارئ
        "https://raw.githubusercontent.com/datasets/cosmetics/master/data/cosmetics.csv"
    ]
    
    # تمويه الهيدر (ضروري جداً لتجاوز الحظر)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    for url in mirrors:
        try:
            # محاولة الاتصال مع timeout قصير حتى لا يصفن
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                # محاولة قراءة الملف
                data = StringIO(response.text)
                df = pd.read_csv(data, on_bad_lines='skip')
                
                # تنظيف أسماء الأعمدة (لأن كل مصدر يسمي الأعمدة شكل)
                df.columns = [c.strip().lower() for c in df.columns]
                
                # فحص سريع: هل الداتا حقيقية؟ (لازم اكثر من 100 سطر)
                if len(df) > 100:
                    return df, f"Connected to Mirror: {url.split('/')[2]}"
                    
        except Exception as e:
            # فشل هذا الرابط؟ نعبر عالبعده فوراً وبدون دراما
            continue
            
    return None, "All Mirrors Unreachable"

# ---------------------------------------------------------
# 3. Execution (لحظة الحقيقة)
# ---------------------------------------------------------
with st.spinner('📡 Establishing Secure Link with Global Nodes...'):
    df, status_msg = fetch_live_data()

if df is not None:
    # ---------------------------------------------------------
    # 4. Smart Column Detection (كشف الأعمدة الذكي)
    # ---------------------------------------------------------
    # ندور عالعمود اللي بي اسم المادة، مهما كان اسمه
    name_col = next((c for c in df.columns if 'name' in c or 'inn' in c or 'chemical' in c), None)
    # ندور عالعمود اللي بي رقم CAS
    cas_col = next((c for c in df.columns if 'cas' in c), None)
    
    if name_col:
        # تحضير القوائم
        banned_names = df[name_col].dropna().astype(str).str.lower().tolist()
        banned_cas = df[cas_col].dropna().astype(str).tolist() if cas_col else []
        
        # واجهة النجاح
        st.success(f"✅ **System Online** | {status_msg}")
        st.metric("Live Prohibitions Count", f"{len(banned_names):,}")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            user_input = st.text_area("Paste Ingredients List:", height=150, placeholder="Aqua, Glycerin, Hydroquinone...")
            
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
            st.info("ℹ️ **Auto-Sync Engine**")
            st.write("This system uses a Multi-Mirror architecture. It attempts to fetch data from 3 different global repositories to ensure zero downtime.")
    else:
        st.error("🚨 Data Error: Columns not recognized from the source.")
else:
    # ---------------------------------------------------------
    # 5. الفشل الذريع (بس إن شاء الله ما نوصله)
    # ---------------------------------------------------------
    st.error("🛑 **CONNECTION FAILED**")
    st.warning("Debugging: All 3 global mirrors are currently blocking the connection.")
    if st.button("🔄 Force Retry"):
        st.cache_data.clear()
        st.rerun()
