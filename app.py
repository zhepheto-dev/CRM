import streamlit as st
from supabase import create_client, Client
import re

# 🔐 [정밀 검증] image_459a39.png의 실제 ID 'xptuxxz'와 image_452c46.png의 키를 적용했습니다.
SUPABASE_URL = "https://xptuxxzsvwjxpzeelsjf.supabase.co".strip()
SUPABASE_KEY = "sb_publishable_ZAcVzMbVwwl1A-YNZIJucA_D6gTqcd8".strip()

@st.cache_resource
def get_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        return None

supabase = get_supabase()

# 페이지 설정
st.set_page_config(page_title="Clinic CRM", layout="wide")

# 숫자를 한글 만 단위로 읽어주는 함수 (zhepheto님 요청 사항)
def number_to_korean(num):
    if num < 10000: return "1만 미만" if num > 0 else "0"
    units = ["", "만", "억", "조"]
    result = []
    man_unit_val = num // 10000 
    idx = 1 
    while man_unit_val > 0:
        man_unit_val, mod = divmod(man_unit_val, 10000)
        if mod > 0: result.append(f"{mod:,}{units[idx]}")
        idx += 1
    return " ".join(reversed(result))

st.title("🏥 지점별 상담 내역 관리 시스템")

# 1. 지점 선택
branch = st.sidebar.selectbox("지점 선택", ["지점을 선택하세요", "강남점", "서초점"])

if branch != "지점을 선택하세요":
    st.header(f"📍 {branch} 상담 데이터 입력")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 기본 인적 사항")
        patient_name = st.text_input("환자명", placeholder="성함을 입력하세요")
        patient_type = st.radio("환자 구분", ["신환", "구환"], horizontal=True)
        inflow = st.selectbox("유입 경로", ["온라인", "소개환자", "외부영업", "워크-인", "기타"])
        staff_name = st.selectbox("상담사", ["우선혜", "전누리", "임예린"])
        
    with col2:
        st.subheader("💰 상담 결과 및 금액")
        result_status = st.selectbox("상담 결과", ["확정", "미확정", "보류", "상담없음"])
        
        def get_num(val):
            # 숫자 외 문자는 모두 제거 후 정수 변환
            clean_val = re.sub(r'[^0-9]', '', str(val))
            return int(clean_val) if clean_val else 0

        # 금액 입력 (제시액, 확정액 모두 누락 없이 표시하도록 고정)
        sug_raw = st.text_input("상담 금액 (제시액)", value="0")
        conf_raw = st.text_input("확정 금액 (총액)", value="0")
        paid_raw = st.text_input("당일 수납 금액", value="0")

        sug_val = get_num(sug_raw)
        conf_val = get_num(conf_raw)
        paid_val = get_num(paid_raw)

        # 🚀 실시간 금액 상세 요약창
        if sug_val > 0 or conf_val > 0 or paid_val > 0:
            st.info(f"""
            📊 **입력된 금액 확인**
            * **제시액:** {sug_val:,}원 ({number_to_korean(sug_val)} 원)
            * **확정액:** {conf_val:,}원 ({number_to_korean(conf_val)} 원)
            * **수납액:** {paid_val:,}원 ({number_to_korean(paid_val)} 원)
            """)

    content = st.text_area("📝 상담 상세 내용 및 특이사항", height=150)
    
    # 2. 저장 로직
    if st.button("💾 상담 내역 저장하기"):
        if not patient_name:
            st.error("⚠️ 환자명을 입력해 주세요.")
        elif supabase is None:
            st.error("❌ 서버 연결 실패! 주소 또는 API 키를 확인해 주세요.")
        else:
            try:
                # image_458e59.png의 테이블 컬럼명과 100% 일치시킴
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
                
                # 수파베이스 저장 실행
                supabase.table("counseling_logs").insert(data).execute()
                st.success(f"✅ {patient_name} 님 상담 기록 저장 완료!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ 저장 실패: {str(e)}")
else:
    st.info("왼쪽 사이드바에서 담당 지점을 먼저 선택해 주세요.")
