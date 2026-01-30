import pandas as pd
import streamlit as st

# نستخدم الكاش حتى لا يثقل الموقع، ويحدث كل 30 دقيقة (مثل توقيت غوغل)
@st.cache_data(ttl=1800)
def load_data():
    url = "https://raw.githubusercontent.com/ph-aya/PharmaGuard-Audit/main/banned.csv"
    
    try:
        # التغيير هنا: ضفنا on_bad_lines='skip' لتجاهل الأسطر الخربانة
        # وضفنا engine='python' لأنه أذكى في التعامل مع الملفات المعقدة
        df = pd.read_csv(url, on_bad_lines='skip', engine='python')
        
        df = df.rename(columns={
            'Chemical name / INN': 'inci_name',
            'CAS Number': 'cas_no',
            'EC Number': 'ec_number',
            'Reference Number': 'ref_no'
        })
        
        if 'inci_name' in df.columns:
            df['inci_name'] = df['inci_name'].astype(str).str.strip().str.lower()
        else:
            st.error("🚨 الأعمدة تغيرت! تأكد من المصدر.")
            return pd.DataFrame()
            
        return df

    except Exception as e:
        st.error(f"❌ فشل الاتصال: {e}")
        return pd.DataFrame()
# --- بداية التطبيق ---
df = load_data()

# تأكد بسيط (للمطور فقط - تكدرين تمسحيه بعدين)
if not df.empty:
    st.success(f"✅ تم الاتصال بـ GitHub! عدد المواد المحظورة: {len(df)}")
else:
    st.warning("⚠️ جاري العمل بنظام الطوارئ (لا توجد بيانات).")

