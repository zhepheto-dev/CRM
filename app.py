import streamlit as st
from supabase import create_client, Client
import re

# 🔐 [기본 규격] 수파베이스 접속 정보 (image_44b8a1.png 근거)
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

# 💰 [천 원 단위 정밀 출력] 90만 5,000원 형식으로 변환
def number_to_korean(num):
    if num == 0: return "0"
    result = []
    
    temp_num = num
    # 억 단위
    if temp_num >= 100000000:
        억 = temp_num // 100000000
        result.append(f"{억:,}억")
        temp_num %= 100000000
        
    # 만 단위
    if temp_num >= 10000:
        만 = temp_num // 10000
        result.append(f"{만:,}만")
        temp_num %= 10000
        
    # 천 단위 (zhepheto님 요청: 천 원 단위까지 상세 표기)
    if temp_num >= 1000:
        천 = temp_num // 1000
        result.append(f"{천:,}천")
        
    return " ".join(result)

st.title("🏥 상담 내역 관리 시스템")

# 지점 선택 사이드바
branch = st.sidebar.selectbox("지점 선택", ["지점을 선택하세요", "강남점", "서초점"])

if branch != "지점을 선택하세요":
    st.header(f"📍 {branch} 입력창")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 환자 및 상담 정보")
        patient_name = st.text_input("환자명", value="")
        patient_type = st.radio("구분", ["신환", "구환"], horizontal=True)
        
        # 🚀 [수정] 상담항목 선택
        consult_item = st.selectbox("상담항목", [
            "항목을 선택하세요", "임플란트", "교정", "미백/라미네이트", "충치/보철", "턱관절/이갈이", "기타(직접입력)"
        ])
        if consult_item == "기타(직접입력)":
            consult_item = st.text_input("상세 상담항목 입력")

        inflow = st.selectbox("경로", ["온라인", "소개", "워크인", "기타"])
        staff_name = st.selectbox("상담자", ["우선혜", "전누리", "임예린"])
        
    with col2:
        st.subheader("💰 금액 및 예약 정보")
        result_status = st.selectbox("상담결과", ["확정", "미확정", "보류", "상담없음"])
        
        # 🚀 [추가] 다음 예약 여부
        next_reservation = st.radio("다음 예약 여부", ["예약 완료", "미예약", "추후 연락"], horizontal=True)
        
        def get_num(val):
            clean = re.sub(r'[^0-9]', '', str(val))
            return int(clean) if clean else 0

        # 명칭 변경 반영 (상담/확정/수납금액)
        sug_raw = st.text_input("상담금액", value="", placeholder="숫자만 입력")
        conf_raw = st.text_input("확정금액", value="", placeholder="숫자만 입력")
        paid_raw = st.text_input("수납금액", value="", placeholder="숫자만 입력")

        sug_val, conf_val, paid_val = get_num(sug_raw), get_num(conf_raw), get_num(paid_raw)

        if sug_val > 0 or conf_val > 0 or paid_val > 0:
            st.info("📊 **금액 상세 요약**")
            st.write(f"* 상담금액: {sug_val:,}원 ({number_to_korean(sug_val)} 원)")
            st.write(f"* 확정금액: {conf_val:,}원 ({number_to_korean(conf_val)} 원)")
            # 🚀 [강조] 수납금액 빨간색 및 폰트 확대 (image_4499fa.png 에러 수정 적용)
            st.markdown(f"""
                <div style="font-size: 1.15em; color: #FF4B4B; font-weight: bold; margin-top: 5px;">
                    * 수납금액: {paid_val:,}원 ({number_to_korean(paid_val)} 원)
                </div>
                """, unsafe_allow_html=True)

    content = st.text_area("📝 상담 상세 내용", height=150)
    
    if st.button("💾 상담 내역 금고에 저장하기"):
        if not patient_name or consult_item == "항목을 선택하세요":
            st.error("⚠️ 환자명과 상담항목을 모두 확인해 주세요.")
        else:
            try:
                # 🚀 주의: 수파베이스 DB에 'treatment', 'next_reservation' 컬럼이 반드시 있어야 함
                data = {
                    "branch": str(branch),
                    "patient_name": str(patient_name),
                    "patient_type": str(patient_type),
                    "treatment": str(consult_item), 
                    "inflow": str(inflow),
                    "staff_name": str(staff_name),
                    "result": str(result_status),
                    "next_reservation": str(next_reservation),
                    "price_suggested": int(sug_val),
                    "price_confirmed": int(conf_val),
                    "price_paid": int(paid_val),
                    "content": str(content)
                }
                supabase.table("counseling_logs").insert(data).execute()
                st.success(f"✅ {patient_name} 님 저장 완료! 조심히 퇴근하세요!")
                st.balloons()
            except Exception as e:
                # [Errno -2] 등 연결 에러 발생 시 출력 (image_450eba.png 참고)
                st.error(f"❌ 저장 실패: {str(e)}")
