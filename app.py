import streamlit as st
import pandas as pd
from difflib import get_close_matches

# ---------------------------------------------------------
# 1. App Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="PharmaGuard Audit", 
    layout="wide", 
    page_icon="🛡️"
)

st.title("🛡️ PharmaGuard: EU Compliance Auditor")
st.caption("Auto-synced with EU CosIng Annex II Database via GitHub Pipeline")

# ---------------------------------------------------------
# 2. Data Engine (Auto-Sync)
# ---------------------------------------------------------
@st.cache_data(ttl=1800)
def load_data():
    url = "https://raw.githubusercontent.com/ph-aya/PharmaGuard-Audit/main/banned.csv"
    try:
        df = pd.read_csv(url, on_bad_lines='skip', engine='python')
        df = df.rename(columns={
            'Chemical name / INN': 'inci_name',
            'CAS Number': 'cas_no',
            'EC Number': 'ec_number',
            'Reference Number': 'ref_no'
        })
        
        # Cleaning: Lowercase everything for comparison
        if 'inci_name' in df.columns:
            df['inci_name'] = df['inci_name'].astype(str).str.lower().str.strip()
        
        if 'cas_no' in df.columns:
            df['cas_no'] = df['cas_no'].astype(str).str.strip()

        return df
    except Exception as e:
        st.error(f"❌ Critical Error: Failed to connect to live database. {e}")
        return pd.DataFrame()

with st.spinner('Syncing with EU Server...'):
    df = load_data()

if df.empty:
    st.stop()
else:
    # We keep the raw list for fuzzy matching
    banned_names = df['inci_name'].tolist()
    banned_cas = df['cas_no'].tolist()
    st.toast(f"✅ System Ready! Loaded {len(df)} substances.", icon="🟢")

# ---------------------------------------------------------
# 3. Intelligent Scan Logic
# ---------------------------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔍 Ingredient Scanner")
    user_input = st.text_area(
        "Paste Ingredient List:", 
        height=200, 
        placeholder="e.g. Aqua, Isopropylparaben, Lilial, 80-54-6..."
    )
    
    if st.button("🚀 Run Deep Scan", type="primary"):
        if user_input:
            risks = []
            ingredients = [x.strip().lower() for x in user_input.replace('\n', ',').split(',')]
            
            for item in ingredients:
                if len(item) < 3: continue 
                
                # --- LEVEL 1: CAS Number Scan (High Precision) ---
                if item in banned_cas:
                    risks.append(f"❌ **BANNED (CAS Match):** Code **'{item}'** is a prohibited substance.")
                    continue

                # --- LEVEL 2: Exact Name Match ---
                if item in banned_names:
                    risks.append(f"❌ **BANNED (Direct Match):** The substance **'{item}'** is explicitly listed.")
                    continue

                # --- LEVEL 3: Deep Substring Scan (New Feature) 🔥 ---
                # يبحث إذا كانت الكلمة المدخلة جزءاً من اسم طويل في القائمة
                # Example: Finds "Isopropylparaben" inside "Salts of Isopropylparaben"
                substring_match = False
                for banned in banned_names:
                    # شرط الطول لتجنب الأخطاء (مثلا البحث عن tea لا يمسك tears)
                    if len(item) > 4 and item in banned:
                        risks.append(f"⚠️ **BANNED (Hidden Match):** **'{item}'** was found inside the prohibited entry: *'{banned[:50]}...'*")
                        substring_match = True
                        break # Stop searching for this item if found
                
                if substring_match: continue

                # --- LEVEL 4: Fuzzy Logic (Typo Detection) ---
                matches = get_close_matches(item, banned_names, n=1, cutoff=0.85)
                if matches:
                    risks.append(f"❓ **SUSPICIOUS (Typo?):** Did you mean **'{matches[0][:30]}...'**? It is BANNED.")

            # Display Results
            st.markdown("---")
            if risks:
                st.error(f"🚫 AUDIT FAILED: Found {len(risks)} violations.")
                for r in risks: st.markdown(r)
            else:
                st.success("✅ AUDIT PASSED: No banned substances found.")
                st.caption("Checked against EU Annex II (Official GitHub Mirror).")
        else:
            st.warning("Enter ingredients to start.")

with col2:
    st.info("📊 **Database Stats**")
    st.metric(label="Banned Substances", value=len(df))
    st.write("**Scan Mode:** Deep Search (Substring + Fuzzy)")
    st.write("**Status:** Online 🟢")
    st.markdown("---")
    with st.expander("ℹ️ How Deep Scan Works"):
        st.write("""
        1. **CAS Check:** Checks chemical ID numbers.
        2. **Exact Match:** Direct name comparison.
        3. **Hidden Match:** Finds ingredients hidden inside long chemical descriptions (e.g. finding 'Paraben' inside 'Salts of Paraben').
        4. **Typo Detector:** Catches spelling mistakes.
        """)
