import streamlit as st
import pandas as pd
import requests
from io import StringIO
from difflib import get_close_matches

# 1. System Config
st.set_page_config(page_title="PharmaGuard Live", layout="wide", page_icon="📡")

st.title("📡 PharmaGuard: Real-Time Regulatory Auditor")
st.caption("Connected directly to EU CosIng Open Data Source")

# 2. Real-Time Fetcher Engine (No Local Files)
# TTL = 600 seconds (يحدث البيانات كل 10 دقائق تلقائياً)
@st.cache_data(ttl=600)
def fetch_live_data():
    # الرابط الخام المباشر من المصدر (Third Party Repository)
    # نستخدم المستودع الرسمي لـ OpenBeautyFacts لأنهم يحدثون البيانات دورياً
    live_url = "https://raw.githubusercontent.com/openfoodfacts/openbeautyfacts/master/cosing/csv/COSING_Annex_II_v2.csv"
    
    try:
        # 1. نرسل طلب "محترم" للسيرفر مع User-Agent
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36"}
        response = requests.get(live_url, headers=headers, timeout=10)
        
        # 2. نتأكد أن الرابط شغال
        if response.status_code == 200:
            # نحول النص المستلم إلى جدول بيانات
            df = pd.read_csv(StringIO(response.text), on_bad_lines='skip')
            
            # تنظيف أسماء الأعمدة (Normalization)
            df.columns = [c.strip().lower() for c in df.columns]
            return df
        else:
            return None
            
    except Exception as e:
        # طباعة الخطأ في الكونسول للمبرمج فقط
        print(f"Connection Error: {e}")
        return None

# 3. Execution & Status Check
with st.spinner('📡 Syncing with Global Database (Real-Time)...'):
    df = fetch_live_data()

if df is not None:
    # تحديد الأعمدة الذكي
    name_col = next((c for c in df.columns if 'name' in c or 'inn' in c), None)
    cas_col = next((c for c in df.columns if 'cas' in c), None)
    
    if name_col:
        banned_names = df[name_col].dropna().astype(str).str.lower().tolist()
        banned_cas = df[cas_col].dropna().astype(str).tolist() if cas_col else []
        
        # عرض حالة الاتصال (لإبهار المستخدم)
        st.success(f"✅ **System Synced:** Connected to Live Stream. Database contains **{len(banned_names)}** active prohibitions.")
        
        # --- منطقة الفحص ---
        col1, col2 = st.columns([2, 1])
        
        with col1:
            user_input = st.text_area("Paste Ingredient List:", height=150, placeholder="Paste list here to audit against live data...")
            
            if st.button("🚀 Run Live Audit"):
                if user_input:
                    risks = []
                    ingredients = [x.strip().lower() for x in user_input.replace('\n', ',').split(',')]
                    
                    for item in ingredients:
                        if len(item) < 2: continue
                        
                        # Exact Match
                        if item in banned_names:
                            risks.append(f"❌ **BANNED:** {item}")
                        # CAS Match
                        elif item in banned_cas:
                            risks.append(f"❌ **BANNED (CAS ID):** {item}")
                        # Fuzzy Match
                        else:
                            matches = get_close_matches(item, banned_names, n=1, cutoff=0.85)
                            if matches:
                                risks.append(f"⚠️ **Suspicious:** Did you mean '{matches[0]}'? It is banned.")
                    
                    if risks:
                        st.error(f"Audit Results: Found {len(risks)} Violations")
                        for r in risks: st.write(r)
                    else:
                        st.success("✅ Clean: No banned substances found in current live list.")
                        
        with col2:
            st.info("ℹ️ **Live Source Info**")
            st.markdown(f"""
            - **Source:** EU CosIng Annex II
            - **Provider:** OpenBeautyFacts Repo
            - **Sync Interval:** Every 10 mins
            - **Total Substances:** {len(banned_names)}
            """)
            
    else:
        st.error("🚨 Data Structure Error: Source columns changed.")
else:
    # هذا يطلع فقط إذا السيرفر المصدر وكع أو الرابط تغير
    st.error("📡 Connection Failed: Could not fetch live data from GitHub.")
    st.warning("Please check the 'OpenBeautyFacts' repository URL status.")

st.markdown("---")
