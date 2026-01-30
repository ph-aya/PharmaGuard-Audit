import pandas as pd
import streamlit as st

# نستخدم الكاش حتى لا يثقل الموقع، ويحدث كل 30 دقيقة (مثل توقيت غوغل)
@st.cache_data(ttl=1800)
def load_data():
    # هذا الرابط هو "خط الأنابيب" المباشر للملف بداخل GitHub
    url = "https://raw.githubusercontent.com/ph-aya/PharmaGuard-Audit/main/banned.csv"
    
    try:
        # قراءة الملف مباشرة من الرابط
        df = pd.read_csv(url)
        
        # ⚠️ خطوة جوهرية: توحيد أسماء الأعمدة ⚠️
        # الملف الرسمي يستخدم أسماء طويلة، احنا نحولها للأسماء البرمجية اللي كودج متعود عليها
        df = df.rename(columns={
            'Chemical name / INN': 'inci_name',
            'CAS Number': 'cas_no',
            'EC Number': 'ec_number',
            'Reference Number': 'ref_no'
        })
        
        # تنظيف البيانات: تحويل كلشي لنصوص صغيرة (Lowercase) لسهولة البحث
        # وفحص اذا عمود inci_name موجود أصلاً بعد إعادة التسمية
        if 'inci_name' in df.columns:
            df['inci_name'] = df['inci_name'].astype(str).str.strip().str.lower()
        else:
            st.error("🚨 خطأ: أسماء الأعمدة في الملف المصدر تغيرت! تأكد من ملف CSV.")
            
        return df

    except Exception as e:
        st.error(f"❌ فشل الاتصال بقاعدة البيانات الحية: {e}")
        return pd.DataFrame() # نرجع جدول فارغ حتى لا يوكف التطبيق

# --- بداية التطبيق ---
df = load_data()

# تأكد بسيط (للمطور فقط - تكدرين تمسحيه بعدين)
if not df.empty:
    st.success(f"✅ تم الاتصال بـ GitHub! عدد المواد المحظورة: {len(df)}")
else:
    st.warning("⚠️ جاري العمل بنظام الطوارئ (لا توجد بيانات).")
