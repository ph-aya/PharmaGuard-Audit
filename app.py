import streamlit as st
import pandas as pd
import os
import time
from difflib import get_close_matches

# ---------------------------------------------------------
# 1. System Configuration (إعدادات النظام)
# ---------------------------------------------------------
st.set_page_config(
    page_title="PharmaGuard Audit", 
    layout="wide", 
    page_icon="🛡️"
)

st.title("🛡️ PharmaGuard: Live Compliance Auditor")
st.caption("Powered by Automated GitHub Actions | Sync Interval: 30 Mins")

# ---------------------------------------------------------
# 2. The "Engine" (Data Loader)
# ---------------------------------------------------------
@st.cache_data(ttl=600)  # يفرغ الكاش كل 10 دقائق ليقرأ التحديث الجديد
def load_database():
    file_path = "banned.csv"
    
    # التحقق من وجود الملف (هل الروبوت أكمل مهمته؟)
    if not os.path.exists(file_path):
        return None, "⏳ Initializing... Waiting for first sync."
    
    try:
        # قراءة الملف الذي جلبه الروبوت
        df = pd.read_csv(file_path, on_bad_lines='skip', low_memory=False)
        
        # تنظيف أسماء الأعمدة (لضمان عمل الكود مهما تغير المصدر)
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        # إضافة وقت آخر تعديل للملف (للمصداقية)
        mod_time = time.ctime(os.path.getmtime(file_path))
        
        return df, f"🟢 Online | Last Sync: {mod_time}"
    except Exception as e:
        return None, f"❌ Corrupted Data: {e}"

# تشغيل المحرك
df, system_status = load_database()

# ---------------------------------------------------------
# 3. Intelligent Column Detection (الكشف الذكي للأعمدة)
# ---------------------------------------------------------
if df is not None:
    # نبحث عن العمود الذي يحتوي الاسم (Name / INCI)
    name_col = next((c for c in df.columns if 'name' in c or 'inn' in c or 'substance' in c), None)
    # نبحث عن العمود الذي يحتوي الرقم (CAS)
    cas_col = next((c for c in df.columns if 'cas' in c), None)
    
    if not name_col:
        st.error("🚨 Critical Error: Could not identify 'Ingredient Name' column in the latest update.")
        st.stop()
        
    # تحضير القوائم للسرعة القصوى
    banned_names = df[name_col].dropna().astype(str).str.lower().tolist()
    banned_cas = df[cas_col].dropna().astype(str).tolist() if cas_col else []
    
    db_size = len(banned_names)
else:
    # حالة الانتظار (أول مرة فقط)
    st.warning(system_status)
    st.stop()

# ---------------------------------------------------------
# 4. The UI & Audit Logic (واجهة المستخدم والفحص)
# ---------------------------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🧪 Audit Panel")
    user_input = st.text_area("Paste Ingredient List (Comma Separated):", height=150, 
                            placeholder="Example: Aqua, Glycerin, Chloroform, 123-31-9...")
    
    if st.button("🚀 Run Compliance Audit", type="primary"):
        if user_input:
            risks = []
            # تنظيف المدخلات (إزالة الفواصل والمسافات الزائدة)
            raw_ingredients = [x.strip() for x in user_input.replace('\n', ',').split(',')]
            ingredients = [x.lower() for x in raw_ingredients if len(x) > 1]
            
            progress_bar = st.progress(0)
            
            for i, item in enumerate(ingredients):
                # تحديث شريط التقدم
                progress_bar.progress((i + 1) / len(ingredients))
                
                # 1. Exact Name Match (تطابق تام)
                if item in banned_names:
                    risks.append(f"❌ **CRITICAL:** '{item}' is BANNED by EU Regulations.")
                    continue
                    
                # 2. CAS Number Match (تطابق الرقم الكيميائي)
                if item in banned_cas:
                    risks.append(f"❌ **CRITICAL (CAS):** ID '{item}' matches a banned substance.")
                    continue

                # 3. Fuzzy Logic (كشف الأخطاء الإملائية)
                # نستخدم الذكاء فقط إذا لم نجد تطابق تام
                matches = get_close_matches(item, banned_names, n=1, cutoff=0.85)
                if matches:
                    risks.append(f"⚠️ **Typo Detected:** Did you mean '{matches[0]}'? It is BANNED.")
            
            # النتيجة النهائية
            st.markdown("---")
            if risks:
                st.error(f"🚫 FAILED: Found {len(risks)} Violations.")
                for r in risks: st.write(r)
            else:
                st.success("✅ PASSED: No banned substances detected.")
                st.caption("Auto-Certified against latest EU Annex II Snapshot.")
                
        else:
            st.warning("⚠️ Please enter ingredients to scan.")

with col2:
    st.info("📊 **Live System Stats**")
    st.metric(label="Total Banned Substances", value=f"{db_size:,}")
    st.write(f"**Status:** {system_status}")
    st.markdown("---")
    
    with st.expander("ℹ️ How updates work?"):
        st.write("""
        1. **The Spy Bot:** A script wakes up every 30 mins.
        2. **The Fetch:** It grabs the latest CSV from EU Servers.
        3. **The Sync:** It pushes the update to this dashboard automatically.
        """)

# Footer
st.markdown("---")
st.caption("PharmaGuard v4.1 | Autonomous Compliance System")
