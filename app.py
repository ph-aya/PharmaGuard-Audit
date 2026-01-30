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
@st.cache_data(ttl=1800) # Auto-refresh every 30 mins
def load_data():
    # Direct link to your auto-updated file
    url = "https://raw.githubusercontent.com/ph-aya/PharmaGuard-Audit/main/banned.csv"
    
    try:
        # Load CSV with robust error handling
        df = pd.read_csv(url, on_bad_lines='skip', engine='python')
        
        # Normalize column names to standard internal IDs
        df = df.rename(columns={
            'Chemical name / INN': 'inci_name',
            'CAS Number': 'cas_no',
            'EC Number': 'ec_number',
            'Reference Number': 'ref_no'
        })
        
        # Data Cleaning & Preprocessing
        if 'inci_name' in df.columns:
            # Convert to lowercase and strip whitespace
            df['inci_name'] = df['inci_name'].astype(str).str.strip().str.lower()
            # Remove special characters for better matching
            df['inci_name'] = df['inci_name'].str.replace(r'[^\w\s-]', '', regex=True)
        
        if 'cas_no' in df.columns:
            df['cas_no'] = df['cas_no'].astype(str).str.strip()

        return df

    except Exception as e:
        st.error(f"❌ Critical Error: Failed to connect to live database. {e}")
        return pd.DataFrame()

# Load Data
with st.spinner('Syncing with EU Server...'):
    df = load_data()

# Validation Check
if df.empty:
    st.warning("⚠️ System is running in safe mode. No data available from GitHub.")
    st.stop()
else:
    # Prepare lookup lists for speed
    banned_names = df['inci_name'].tolist()
    banned_cas = df['cas_no'].tolist()
    
    # Success Toast
    st.toast(f"✅ Database Synced! Loaded {len(df)} banned substances.", icon="🟢")

# ---------------------------------------------------------
# 3. User Interface & Logic
# ---------------------------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔍 Ingredient Scanner")
    user_input = st.text_area(
        "Paste Ingredient List (Comma Separated):", 
        height=200, 
        placeholder="e.g. Aqua, Glycerin, Lilial, Butylphenyl Methylpropional..."
    )
    
    if st.button("🚀 Run Audit", type="primary"):
        if user_input:
            risks = []
            # Parse input: split by comma, strip spaces, convert to lowercase
            ingredients = [x.strip().lower() for x in user_input.replace('\n', ',').split(',')]
            
            for item in ingredients:
                if len(item) < 2: continue # Skip empty/short strings
                
                # A. Exact Name Match
                if item in banned_names:
                    risks.append(f"❌ **BANNED (Direct Match):** The substance **'{item}'** is prohibited in the EU.")
                    continue
                    
                # B. CAS Number Match
                if item in banned_cas:
                    risks.append(f"❌ **BANNED (CAS Match):** Code **'{item}'** corresponds to a prohibited substance.")
                    continue

                # C. Fuzzy Logic (Typo Detection)
                # Finds matches with >85% similarity
                matches = get_close_matches(item, banned_names, n=1, cutoff=0.85)
                if matches:
                    risks.append(f"⚠️ **SUSPICIOUS (Typo?):** Did you mean **'{matches[0]}'**? It is BANNED.")
            
            # Display Results
            st.markdown("---")
            if risks:
                st.error(f"🚫 AUDIT FAILED: Found {len(risks)} compliance violations.")
                for r in risks: 
                    st.markdown(r)
            else:
                st.success("✅ AUDIT PASSED: No banned substances found.")
                st.caption("Note: Result is based on the current version of EU Annex II.")
        else:
            st.warning("Please enter ingredients to scan.")

with col2:
    st.info("📊 **Database Status**")
    st.write(f"**Total Substances:** {len(df)}")
    st.write("**Source:** EU CosIng Annex II")
    st.write("**Last Sync:** Live via GitHub 🟢")
    st.markdown("---")
    with st.expander("ℹ️ How it works"):
        st.write("""
        This tool cross-references your input against the official EU list of prohibited cosmetic substances.
        It uses exact matching, CAS number verification, and fuzzy logic to detect hidden or misspelled risks.
        """)

# Footer
st.markdown("---")
st.caption("PharmaGuard Audit System | v3.0 Auto-Pilot Edition")
