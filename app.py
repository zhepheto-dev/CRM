import streamlit as st
from supabase import create_client, Client
import re

# 🔐 [기본값 유지] zhepheto님의 수파베이스 고유 정보
SUPABASE_URL = "https://xptuxxzsvwjxpzeelsjf.supabase.co"
SUPABASE_KEY = "sb_publishable_ZAcVzMbVwwl1A-YNZIJucA_D6gTqcd8"

@st.cache_resource
def get_supabase():
    try:
        return create_client(SUPABASE_URL.strip(), SUPABASE_KEY.strip())
    except Exception:
        return None

supabase = get_supabase()

st.set_page_config(page_title="Clinic CRM", layout="wide")

def number_to_korean(num):
    if num < 10000: return "1만 미만" if num > 0 else ""
    units = ["", "만", "억", "조"]
    result = []
    man_unit_val = num // 10000 
    idx = 1 
    while man_unit_val > 0:
        man_unit_val, mod = divmod(man_unit_val, 10000)
        if mod > 0: result.append(f"{mod:,}{units[idx]}")
        idx += 1
    return " ".join(reversed(result))

st.title("🏥 상담 내역 관리 시스템")

branch = st.sidebar.selectbox("지점 선택", ["지점을 선택하세요", "강남점", "서초점"])

if branch != "지점을 선택하세요":
    st.header(f"📍 {branch} 입력창")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 환자 정보")
        patient_name = st.text_input("환자명", value="")
        patient_type = st.radio("구분", ["신환", "구환"], horizontal=True)
        inflow = st.selectbox("경로", ["온라인", "소개", "워크인", "기타"])
        # 상담사 -> 상담자 변경
        staff_name = st.selectbox("상담자", ["우선혜", "전누리", "임예린"])
        
    with col2:
        st.subheader("💰 금액 정보")
        # 결과 -> 상담결과 변경
        result_status = st.selectbox("상담결과", ["확정", "미확정", "보류", "상담없음"])
        
        def get_num(val):
            clean = re.sub(r'[^0-9]', '', str(val))
            return int(clean) if clean else 0

        # 명칭 변경: 상담금액, 확정금액, 수납금액
        sug_raw = st.text_input("상담금액", value="", placeholder="숫자만 입력")
        conf_raw = st.text_input("확정금액", value="", placeholder="숫자만 입력")
        paid_raw = st.text_input("수납금액", value="", placeholder="숫자만 입력")

        sug_val, conf_val, paid_val = get_num(sug_raw), get_num(conf_raw), get_num(paid_raw)

        if sug_val > 0 or conf_val > 0 or paid_val > 0:
            # 수납금액 강조 (빨간색 & 2포인트 크게)를 위한 HTML 적용
            st.info("📊 **금액 상세 요약**")
            st.write(f"* 상담금액: {sug_val:,}원 ({number_to_korean(sug_val)} 원)")
            st.write(f"* 확정금액: {conf_val:,}원 ({number_to_korean(conf_val)} 원)")
            st.markdown(f"""
                <div style="font-size: 1.15em; color: #FF4B4B; font-weight: bold; margin-top: 5px;">
                    * 수납금액: {paid_val:,}원 ({number_to_korean(paid_val)} 원)
                </div>
                """, unsafe_url=True)

    content = st.text_area("📝 상담 상세 내용", height=150)
    
    if st.button("💾 상담 내역 금고에 저장하기"):
        if not patient_name:
            st.error("⚠️ 환자명을 입력해 주세요.")
        elif supabase is None:
            st.error("❌ 서버 연결 실패!")
        else:
            try:
                data = {
                    "branch": str(branch),
                    "patient_name": str(patient_name),
                    "patient_type": str(patient_type),
                    "inflow": str(inflow),
                    "staff_name": str(staff_name),
                    "result": str(result_status),
                    "price_suggested": int(sug_val),
                    "price_confirmed": int(conf_val),
                    "price_paid": int(paid_val),
                    "content": str(content)
                }
                supabase.table("counseling_logs").insert(data).execute()
                st.success(f"✅ {patient_name} 님 저장 완료!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ 저장 실패: {str(e)}")
