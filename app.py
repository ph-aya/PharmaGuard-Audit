import streamlit as st
import pandas as pd
from difflib import get_close_matches

# ---------------------------------------------------------
# 1. App Configuration & Cyber-Green Styling 🎨
# ---------------------------------------------------------
st.set_page_config(
    page_title="PharmaGuard Audit", 
    layout="wide", 
    page_icon="🛡️",
    initial_sidebar_state="collapsed"
)

# 🔥 حقن كود CSS لفرض الثيم الأسود والأخضر
st.markdown("""
    <style>
    /* 1. الخلفية العامة والنصوص */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    
    /* 2. العناوين الرئيسية باللون الأخضر المشع */
    h1, h2, h3, h4 {
        color: #00FF99 !important;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* 3. تصميم الزر الرئيسي (Primary Button) */
    div.stButton > button:first-child {
        background: linear-gradient(45deg, #006400, #00FF99);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 255, 153, 0.2);
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(45deg, #00FF99, #006400);
        box-shadow: 0 6px 20px rgba(0, 255, 153, 0.6);
        transform: translateY(-2px);
    }

    /* 4. مربع النص (Text Area) */
    .stTextArea textarea {
        background-color: #1A1C24;
        color: #00FF99; /* الكتابة بالأخضر */
        border: 1px solid #333;
        border-radius: 8px;
    }
    .stTextArea textarea:focus {
        border: 1px solid #00FF99;
        box-shadow: 0 0 10px rgba(0, 255, 153, 0.2);
    }

    /* 5. الأرقام والإحصائيات */
    [data-testid="stMetricValue"] {
        color: #00FF99 !important;
    }

    /* 6. التنبيهات (Success/Error/Info) - تخصيص بسيط */
    .stAlert {
        background-color: #1A1C24;
        border: 1px solid #333;
    }
    
    /* 7. الفوتر المخصص */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #0E1117;
        color: #666;
        text-align: center;
        padding: 10px;
        border-top: 1px solid #333;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# العنوان الرئيسي
st.title("🛡️ PharmaGuard: EU Compliance Auditor")
st.markdown("<p style='color: #888;'>Auto-synced with EU CosIng Annex II Database via GitHub Pipeline 🟢</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Data Engine & Lists
# ---------------------------------------------------------

# ✅ قائمة الحصانة النهائية
SAFE_LIST = [
    "aqua", "water", "eau", "glycerin", "panthenol", "citric acid", 
    "phenoxyethanol", "tocopherol", "sodium benzoate", "potassium sorbate",
    "stearic acid", "cetearyl alcohol", "cetyl alcohol", "dimethicone",
    "parfum", "fragrance", "sodium hydroxide", "limonene", "linalool",
    "xanthan gum", "carbomer", "disodium edta", 
    "alcohol", "alcohol denat", "ethanol", "propylene glycol", 
    "paraffinum liquidum", "mineral oil", "petrolatum", "kaolin", 
    "mica", "talc", "silica", "ci 77891", "titanium dioxide",
    "isopropyl alcohol", "ammonium hydroxide", "resorcinol",
    "hydrogen peroxide"
]

# ☠️ قاموس الأسماء المستعارة
DANGEROUS_ALIASES = {
    "methyl alcohol": "Methanol (Toxic/Banned)",
    "wood alcohol": "Methanol (Toxic/Banned)",
    "formalin": "Formaldehyde (Carcinogen)",
    "lilial": "Butylphenyl Methylpropional (Banned Reprotoxic)",
    "p-bmhca": "Butylphenyl Methylpropional (Banned Reprotoxic)",
    "lyral": "Hydroxyisohexyl 3-Cyclohexene Carboxaldehyde",
    "ppd": "p-Phenylenediamine",
    "lead": "Heavy Metal (Banned)",
    "mercury": "Heavy Metal (Banned)",
    "hydroquinone": "Hydroquinone (Banned Skin Lightener)"
}

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
# 3. Intelligent Scan Logic
# ---------------------------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔍 Ingredient Scanner")
    user_input = st.text_area(
        "Paste Ingredient List:", 
        height=200, 
        placeholder="e.g. Aqua, Glycerin, Methyl Alcohol, 80-54-6..."
    )
    
    if st.button("🚀 Run Full Audit", type="primary"):
        if user_input:
            risks = []
            raw_text = user_input.replace('\n', ',')
            ingredients = [x.strip().lower() for x in raw_text.split(',')]
            
            for item in ingredients:
                if len(item) < 3: continue 
                
                # STEP 0: Check Safe List
                if item in SAFE_LIST: continue

                # STEP 1: Check Aliases
                if item in DANGEROUS_ALIASES:
                    real_name = DANGEROUS_ALIASES[item]
                    risks.append(f"❌ **BANNED (Alias Match):** **'{item}'** is a known alias for **{real_name}**.")
                    continue

                # STEP 2: CAS Number Scan
                if item in banned_cas:
                    risks.append(f"❌ **BANNED (CAS Match):** Code **'{item}'** is a prohibited substance.")
                    continue

                # STEP 3: Exact Name Match
                if item in banned_names:
                    risks.append(f"❌ **BANNED (Direct Match):** The substance **'{item}'** is explicitly listed.")
                    continue

                # STEP 4: Deep Substring Scan
                substring_match = False
                for banned in banned_names:
                    if len(item) > 5 and len(banned) > 6 and item in banned:
                        risks.append(f"⚠️ **BANNED (Hidden Match):** **'{item}'** was found inside: *'{banned[:50]}...'*")
                        substring_match = True
                        break 
                if substring_match: continue

                # STEP 5: Fuzzy Logic
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
                st.info("Note: Common safe ingredients are auto-approved.")
        else:
            st.warning("Enter ingredients to start.")

with col2:
    # تنسيق خاص للصندوق الجانبي
    st.markdown("""
    <div style="background-color: #1A1C24; padding: 20px; border-radius: 10px; border: 1px solid #333;">
        <h3 style="color: #00FF99; margin-top: 0;">📊 System Stats</h3>
    """, unsafe_allow_html=True)
    
    st.metric(label="Banned Substances", value=len(df))
    st.metric(label="Known Aliases", value=len(DANGEROUS_ALIASES))
    st.write("**Mode:** Production V6.2 🏆")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    with st.expander("ℹ️ Logic Explanation"):
        st.write("""
        1. **Safe List:** Skips approved items.
        2. **Alias Check:** Detects common names (e.g. Formalin).
        3. **CAS Check:** Checks ID numbers.
        4. **Hidden Match:** Finds banned items hidden in text.
        """)

# ---------------------------------------------------------
# 4. Footer & Credits ✍️
# ---------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; padding: 20px;'>
        <h4 style='color: #00FF99;'>Developed by Ph. Aya Omar 👩‍🔬</h4>
        <p style='color: #888;'>Powered by PharmaGuard Engine | © 2026</p>
    </div>
    """, 
    unsafe_allow_html=True
)
