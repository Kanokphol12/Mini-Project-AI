import streamlit as st
import requests
import pandas as pd
import re
from collections import Counter

st.set_page_config(
    page_title="Thai Text Analytics",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Sarabun', sans-serif !important;
    }

    .app-title {
        font-size: 2.2rem;
        font-weight: 600;
        margin-bottom: 2px;
    }

    .app-subtitle {
        font-size: 1rem;
        opacity: 0.8;
        margin-bottom: 20px;
    }

    .card-pos {
        background-color: rgba(16, 185, 129, 0.1);
        border-left: 5px solid #10B981;
        padding: 16px 20px;
        border-radius: 8px;
    }

    .card-neg {
        background-color: rgba(239, 68, 68, 0.1);
        border-left: 5px solid #EF4444;
        padding: 16px 20px;
        border-radius: 8px;
    }

    .card-neu {
        background-color: rgba(14, 165, 233, 0.1);
        border-left: 5px solid #0EA5E9;
        padding: 16px 20px;
        border-radius: 8px;
    }

    .stButton > button {
        border-radius: 6px !important;
        font-weight: 500 !important;
        background-color: #2563EB !important;
        color: white !important;
        border: none !important;
        padding: 8px 16px !important;
        transition: background-color 0.2s ease !important;
    }

    .stButton > button:hover {
        background-color: #1D4ED8 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 8px 14px;
        font-weight: 500;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🗝️ ตั้งค่า API")
    raw_api_key = st.text_input("AIForThai API Key:", type="password", placeholder="กรอก API Key ที่นี่")
    api_key = raw_api_key.strip()

    st.markdown("---")
    st.markdown("""
    **คำแนะนำการขอ Key:**
    1. ลงทะเบียนที่ [AIForThai](https://aiforthai.in.th/)
    2. คัดลอก Key จากหน้าข้อมูลส่วนตัว
    """)
    st.caption("ประมวลผลด้วย AIForThai SSense Engine")

st.markdown('<div class="app-title">🍃 Thai Text Analytics & Processing Portal</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">เครื่องมือวิเคราะห์และจัดหมวดหมู่ข้อความภาษาไทยเพื่อการใช้งานเชิงธุรกิจ</div>', unsafe_allow_html=True)

def call_sentiment_api(text, key):
    url = "https://api.aiforthai.in.th/ssense"
    headers = {
        'Apikey': key,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'text': text}
    return requests.post(url, headers=headers, data=data, timeout=10)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎭 วิเคราะห์อารมณ์", 
    "📊 ประมวลผลกลุ่ม (Batch)", 
    "🛡️ ตรวจสอบคำสุ่มเสี่ยง",
    "🔠 คำฮิตสำคัญ",
    "🧹 ปรับแต่งข้อความ"
])

with tab1:
    with st.container(border=True):
        st.markdown("##### 🎭 วิเคราะห์อารมณ์ข้อความเดี่ยว (Single Sentiment Analysis)")
        text_input = st.text_area(
            "ข้อความภาษาไทยที่ต้องการวิเคราะห์:",
            height=100,
            placeholder="ตัวอย่าง: สินค้าคุณภาพดี การจัดส่งรวดเร็ว บริการประทับใจ"
        )

        if st.button("ประมวลผลข้อความ", key="btn_single"):
            if not api_key:
                st.error("⚠️ กรุณากรอก AIForThai API Key ในแถบด้านข้าง")
            elif not text_input.strip():
                st.warning("⚠️ กรุณากรอกข้อความก่อนกดวิเคราะห์")
            else:
                with st.spinner("กำลังวิเคราะห์..."):
                    try:
                        res = call_sentiment_api(text_input, api_key)
                        if res.status_code == 200:
                            data = res.json()
                            sentiment = data.get('sentiment', {}).get('polarity', 'Unknown').lower()
                            score = data.get('sentiment', {}).get('score', '0')

                            col1, col2 = st.columns([2, 1])
                            with col1:
                                if sentiment == 'positive':
                                    st.markdown("""
                                    <div class="card-pos">
                                        <b style="font-size: 1.1rem; color: #10B981;">😃 เชิงบวก (Positive)</b><br>
                                        <span style="font-size: 0.9rem; color: #D1D5DB;">ข้อความแสดงความพึงพอใจ หรือความรู้สึกในแง่ดี</span>
                                    </div>
                                    """, unsafe_allow_html=True)
                                elif sentiment == 'negative':
                                    st.markdown("""
                                    <div class="card-neg">
                                        <b style="font-size: 1.1rem; color: #EF4444;">😡 เชิงลบ (Negative)</b><br>
                                        <span style="font-size: 0.9rem; color: #D1D5DB;">ข้อความแสดงความไม่พึงพอใจ หรือข้อติชม</span>
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown("""
                                    <div class="card-neu">
                                        <b style="font-size: 1.1rem; color: #0EA5E9;">😐 เป็นกลาง (Neutral)</b><br>
                                        <span style="font-size: 0.9rem; color: #D1D5DB;">ข้อความให้ข้อมูลทั่วไป ไม่แสดงอารมณ์ชัดเจน</span>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            with col2:
                                with st.container(border=True):
                                    st.metric(label="คะแนนความมั่นใจ", value=f"{float(score):.2f}")

                            with st.expander("แสดงข้อมูลดิบ (JSON Response)"):
                                st.json(data)
                        else:
                            st.error(f"เกิดข้อผิดพลาดจาก Server (Code {res.status_code}): {res.text}")
                    except Exception as e:
                        st.error(f"การเชื่อมต่อขัดข้อง: {e}")

with tab2:
    with st.container(border=True):
        st.markdown("##### 📊 วิเคราะห์ความคิดเห็นจำนวนมาก (Batch Analytics)")
        st.caption("ใส่รีวิวหรือข้อความหลายๆ บรรทัด (1 ข้อความต่อ 1 บรรทัด) เพื่อสรุปสถิติภาพรวม")
        
        batch_input = st.text_area(
            "ข้อความหลายบรรทัด:",
            height=130,
            placeholder="สินค้าคุณภาพดีมาก\nกล่องพัสดุบุบและจัดส่งช้า\nพนักงานให้บริการสุภาพเรียบร้อย"
        )

        if st.button("ประมวลผลภาพรวม", key="btn_batch"):
            if not api_key:
                st.error("⚠️ กรุณากรอก AIForThai API Key ในแถบด้านข้าง")
            elif not batch_input.strip():
                st.warning("⚠️ กรุณากรอกข้อความอย่างน้อย 1 บรรทัด")
            else:
                lines = [line.strip() for line in batch_input.split('\n') if line.strip()]
                results = []
                
                prog = st.progress(0)
                for idx, line in enumerate(lines):
                    try:
                        res = call_sentiment_api(line, api_key)
                        pol = res.json().get('sentiment', {}).get('polarity', 'neutral') if res.status_code == 200 else 'error'
                    except:
                        pol = 'error'
                    
                    results.append({'ข้อความ': line, 'ผลวิเคราะห์': pol})
                    prog.progress((idx + 1) / len(lines))

                df = pd.DataFrame(results)
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("จำนวนทั้งหมด", len(df))
                m2.metric("เชิงบวก 😃", len(df[df['ผลวิเคราะห์'] == 'positive']))
                m3.metric("เชิงลบ 😡", len(df[df['ผลวิเคราะห์'] == 'negative']))
                m4.metric("เป็นกลาง 😐", len(df[df['ผลวิเคราะห์'] == 'neutral']))

                st.markdown("---")
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.markdown("**สัดส่วนอารมณ์**")
                    st.bar_chart(df['ผลวิเคราะห์'].value_counts())
                with c2:
                    st.markdown("**ตารางรายละเอียด**")
                    st.dataframe(df, use_container_width=True, height=200)
                
                csv_data = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("ดาวน์โหลดผลลัพธ์ (CSV)", data=csv_data, file_name="batch_sentiment.csv", mime="text/csv")

with tab3:
    with st.container(border=True):
        st.markdown("##### 🛡️ ตรวจสอบความเหมาะสมและสถิติข้อความ")
        check_text = st.text_area("กรอกข้อความที่ต้องการตรวจสอบ:", height=110, key="txt_mod")

        if check_text:
            col_a, col_b = st.columns(2)
            with col_a:
                with st.container(border=True):
                    st.markdown("**สถิติข้อความ (Text Metrics)**")
                    st.write(f"- จำนวนอักขระรวม: `{len(check_text)}` ตัว")
                    st.write(f"- จำนวนคำโดยประมาณ: `{len(check_text.split())}` คำ")
                    st.write(f"- จำนวนบรรทัด: `{len(check_text.splitlines())}` บรรทัด")

            with col_b:
                with st.container(border=True):
                    st.markdown("**คัดกรองคำสุ่มเสี่ยง**")
                    bad_words = ["ควย", "เหี้ย", "สัตว์", "สัส", "มึง", "กู", "เย็ด", "เชี่ย"]
                    found_bad = [w for w in bad_words if w in check_text]

                    if found_bad:
                        st.error(f"⚠️ พบคำไม่สุภาพ: {', '.join(found_bad)}")
                    else:
                        st.success("✅ ไม่พบคำหยาบคายในระบบคัดกรองเบื้องต้น")

with tab4:
    with st.container(border=True):
        st.markdown("##### 🔠 สกัดคำฮิตและคำสำคัญ (Top Keywords)")
        st.caption("ระบบคัดกรองและตัดคำเชื่อมภาษาไทย (Stop Words) ออกให้อัตโนมัติ")
        
        kw_text = st.text_area("วางข้อความบทความหรือข้อมูลจำนวนมาก:", height=130, key="txt_kw")
        
        if st.button("สกัดคำสำคัญ"):
            if kw_text.strip():
                thai_stop_words = set(["และ", "ที่", "เป็น", "การ", "มี", "ได้", "ให้", "ใน", "กับ", "ก็", "จะ", "ของ", "ความ", "ว่า", "ไป", "มา", "ไม่", "แต่", "อยู่", "เอา", "เลย", "ถึง", "จาก", "ทาง", "แล้ว"])
                words = re.findall(r'\w+', kw_text)
                filtered = [w for w in words if w not in thai_stop_words and len(w) > 1 and not w.isdigit()]
                
                if filtered:
                    counts = Counter(filtered).most_common(10)
                    kw_df = pd.DataFrame(counts, columns=['คำสำคัญ', 'จำนวนที่พบ'])
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.dataframe(kw_df, use_container_width=True)
                    with c2:
                        st.bar_chart(kw_df.set_index('คำสำคัญ'))
            else:
                st.warning("⚠️ กรุณากรอกข้อความก่อนทำการวิเคราะห์")

with tab5:
    with st.container(border=True):
        st.markdown("##### 🧹 เครื่องมือทำความสะอาดข้อความ (Text Preprocessing)")
        clean_input = st.text_area("ข้อความที่ต้องการปรับแต่ง:", height=110, key="txt_clean")
        
        c1, c2, c3 = st.columns(3)
        rem_url = c1.checkbox("ลบ URL / ลิงก์", value=True)
        rem_emoji = c2.checkbox("ลบ Emoji / สัญลักษณ์", value=True)
        rem_space = c3.checkbox("ลบช่องว่างซ้ำซ้อน", value=True)
        
        if st.button("เริ่มทำความสะอาด"):
            cleaned = clean_input
            if rem_url:
                cleaned = re.sub(r'http\S+|www\.\S+', '', cleaned)
            if rem_emoji:
                cleaned = re.sub(r'[^\w\sก-๙]', '', cleaned)
            if rem_space:
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                
            st.markdown("**ผลลัพธ์ข้อความที่ปรับแต่งแล้ว:**")
            st.code(cleaned, language="text")