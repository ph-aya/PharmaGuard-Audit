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
# 2. Data Engine & Extended Safe List
# ---------------------------------------------------------
# 🔥 قائمة الحصانة الموسعة (V5.1) - لمنع حظر المواد الأساسية
SAFE_LIST = [
    "aqua", "water", "eau", "glycerin", "panthenol", "citric acid", 
    "phenoxyethanol", "tocopherol", "sodium benzoate", "potassium sorbate",
    "stearic acid", "cetearyl alcohol", "cetyl alcohol", "dimethicone",
    "parfum", "fragrance", "sodium hydroxide", "limonene", "linalool",
    "xanthan gum", "carbomer", "disodium edta", 
    "alcohol", "alcohol denat", "ethanol", "propylene glycol", 
    "paraffinum liquidum", "mineral oil", "petrolatum", "kaolin", 
    "mica", "talc", "silica", "ci 77891", "titanium dioxide"
]

@st.cache_data(ttl=1800)
def load_data():
    url = "https://raw.githubusercontent.com/ph-aya/PharmaGuard-Audit/main/banned.csv"
    try:
        df = pd.read_csv(url, on_bad_lines='skip', engine='python')
        df = df.rename(columns={
            'Chemical name / INN': 'inci_name',
            'CAS Number': 'cas_no'
        })
        
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
    banned_names = df['inci_name'].tolist()
    banned_cas = df['cas_no'].tolist()
    st.toast(f"✅ System Ready! Loaded {len(df)} substances.", icon="🟢")

# ---------------------------------------------------------
# 3. Intelligent Scan Logic (With Safety Filter)
# ---------------------------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔍 Ingredient Scanner")
    user_input = st.text_area(
        "Paste Ingredient List:", 
        height=200, 
        placeholder="e.g. Aqua, Glycerin, Isopropylparaben, 80-54-6..."
    )
    
    if st.button("🚀 Run Smart Scan", type="primary"):
        if user_input:
            risks = []
            # معالجة النصوص: تقسيم بالفواصل أو الأسطر الجديدة
            raw_text = user_input.replace('\n', ',')
            ingredients = [x.strip().lower() for x in raw_text.split(',')]
            
            for item in ingredients:
                if len(item) < 3: continue 
                
                # ✅ STEP 0: Check Safe List (Immunity)
                if item in SAFE_LIST:
                    continue

                # ❌ STEP 1: CAS Number Scan
                if item in banned_cas:
                    risks.append(f"❌ **BANNED (CAS Match):** Code **'{item}'** is a prohibited substance.")
                    continue

                # ❌ STEP 2: Exact Name Match
                if item in banned_names:
                    risks.append(f"❌ **BANNED (Direct Match):** The substance **'{item}'** is explicitly listed.")
                    continue

                # ⚠️ STEP 3: Deep Substring Scan (The Hunter)
                # تم رفع شرط الطول لتقليل الاخطاء
                substring_match = False
                for banned in banned_names:
                    # يجب أن تكون الكلمة المدخلة أطول من 5 أحرف لتفعيل البحث العميق
                    if len(item) > 5 and len(banned) > 6 and item in banned:
                        risks.append(f"⚠️ **BANNED (Hidden Match):** **'{item}'** was found inside: *'{banned[:50]}...'*")
                        substring_match = True
                        break 
                
                if substring_match: continue

                # ❓ STEP 4: Fuzzy Logic (Typo Detection)
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
                st.info("Note: Common safe ingredients (Aqua, Alcohol, Glycerin) are auto-approved.")
        else:
            st.warning("Enter ingredients to start.")

with col2:
    st.info("📊 **System Stats**")
    st.metric(label="Banned Substances", value=len(df))
    st.metric(label="Safe List Items", value=len(SAFE_LIST))
    st.write("**Mode:** Smart Filter V5.1 🧠")
    st.markdown("---")
    with st.expander("ℹ️ Logic Explanation"):
        st.write("""
        1. **Safe List:** Skips common safe items (Water, Alcohol, Glycerin).
        2. **CAS Check:** Checks ID numbers.
        3. **Hidden Match:** Finds banned items hidden in text.
        4. **Typo Detector:** Catches misspellings.
        """)
