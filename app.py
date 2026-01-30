import streamlit as st
import pandas as pd
from difflib import get_close_matches

# ---------------------------------------------------------
# 1. إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(
    page_title="PharmaGuard Audit", 
    layout="wide", 
    page_icon="🛡️"
)

st.title("🛡️ PharmaGuard: Live Compliance Auditor")
st.caption("Auto-synced with EU Cosing Annex II via GitHub")

# ---------------------------------------------------------
# 2. محرك البيانات (المربوط بـ GitHub مالتج)
# ---------------------------------------------------------
@st.cache_data(ttl=1800) # تحديث كل 30 دقيقة
def load_data():
    # الرابط المباشر لملفك المحدث
    url = "https://raw.githubusercontent.com/ph-aya/PharmaGuard-Audit/main/banned.csv"
    
    try:
        # قراءة الملف مع تخطي الأسطر التالفة
        df = pd.read_csv(url, on_bad_lines='skip', engine='python')
        
        # توحيد أسماء الأعمدة لتسهيل البحث
        df = df.rename(columns={
            'Chemical name / INN': 'inci_name',
            'CAS Number': 'cas_no',
            'EC Number': 'ec_number',
            'Reference Number': 'ref_no'
        })
        
        # تنظيف البيانات (مسح الفراغات وتحويل لصغير)
        if 'inci_name' in df.columns:
            df['inci_name'] = df['inci_name'].astype(str).str.strip().str.lower()
            # إزالة الرموز الغريبة من الأسماء إن وجدت
            df['inci_name'] = df['inci_name'].str.replace(r'[^\w\s-]', '', regex=True)
        
        if 'cas_no' in df.columns:
            df['cas_no'] = df['cas_no'].astype(str).str.strip()

        return df

    except Exception as e:
        st.error(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
        return pd.DataFrame()

# تحميل البيانات
with st.spinner('جاري سحب البيانات المحدثة من السيرفر...'):
    df = load_data()

# التأكد من وجود البيانات
if df.empty:
    st.warning("⚠️ النظام يعمل، ولكن لا توجد بيانات. تأكد من تحديث الملف في GitHub.")
    st.stop()
else:
    # تجهيز قوائم البحث السريع
    banned_names = df['inci_name'].tolist()
    banned_cas = df['cas_no'].tolist()
    
    # عرض حالة الاتصال (يختفي بعد ثواني)
    st.toast(f"✅ تم الاتصال بنجاح! عدد المواد المحظورة: {len(df)}", icon="🟢")

# ---------------------------------------------------------
# 3. واجهة المستخدم والبحث
# ---------------------------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔍 فحص المكونات")
    user_input = st.text_area(
        "الصق قائمة المكونات هنا (افصل بينها بفواصل):", 
        height=200, 
        placeholder="مثال: Aqua, Glycerin, Hydroquinone, Lilial..."
    )
    
    if st.button("🚀 ابدأ الفحص (Run Audit)", type="primary"):
        if user_input:
            risks = []
            # تحويل النص المدخل إلى قائمة
            ingredients = [x.strip().lower() for x in user_input.replace('\n', ',').split(',')]
            
            for item in ingredients:
                if len(item) < 2: continue # تجاهل الكلمات القصيرة جداً
                
                # 1. بحث عن الاسم (Exact Match)
                if item in banned_names:
                    risks.append(f"❌ **محظور (CRITICAL):** المادة **'{item}'** موجودة في قائمة المنع!")
                    continue
                    
                # 2. بحث عن رقم CAS
                if item in banned_cas:
                    risks.append(f"❌ **محظور (CAS Match):** الكود **'{item}'** يعود لمادة محظورة.")
                    continue

                # 3. الذكاء الاصطناعي (Fuzzy Search) - لكشف الأخطاء الإملائية
                # يبحث عن أقرب كلمة تشبه المدخل بنسبة 85%
                matches = get_close_matches(item, banned_names, n=1, cutoff=0.85)
                if matches:
                    risks.append(f"⚠️ **اشتباه (Typo?):** هل تقصد **'{matches[0]}'**؟ هذه المادة محظورة!")
            
            # عرض النتائج
            st.markdown("---")
            if risks:
                st.error(f"🚫 فشل الفحص: تم العثور على {len(risks)} مخالفات.")
                for r in risks: 
                    st.markdown(r)
            else:
                st.success("✅ سليم: لم يتم العثور على أي مواد محظورة من القائمة الحالية.")
                st.caption("ملاحظة: هذه النتيجة تعتمد على قاعدة بيانات CosIng Annex II المحدثة.")
        else:
            st.warning("الرجاء إدخال مواد للفحص.")

with col2:
    st.info("📊 **إحصائيات قاعدة البيانات**")
    st.write(f"**عدد المواد:** {len(df)}")
    st.write("**المصدر:** EU CosIng Annex II")
    st.write("**حالة التحديث:** Auto-Synced via GitHub 🟢")
    st.markdown("---")
    with st.expander("ℹ️ كيف يعمل النظام؟"):
        st.write("""
        هذا النظام متصل مباشرة بملف CSV على GitHub يتم تحديثه تلقائياً.
        يقوم بمقارنة مدخلاتك مع القائمة الرسمية للمواد المحظورة، ويكشف حتى عن الأخطاء الإملائية البسيطة.
        """)

# تذييل الصفحة
st.markdown("---")
st.caption("PharmaGuard Audit System | v3.0 Auto-Pilot Edition")
