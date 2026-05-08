import streamlit as st
import datetime
import re
from supabase import create_client, Client

# 🔐 Supabase 연결 설정 (앞서 확인하신 정보를 그대로 사용하세요)
SUPABASE_URL = "https://xptuxxzwvwjxpzeelsjf.supabase.co"
SUPABASE_KEY = "여기에_복사하신_긴_anon_public_key를_넣으세요"

# 금고 연결 시도
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Supabase 연결 설정 오류: {e}")

# 페이지 설정
st.set_page_config(page_title="Clinic Admin System", layout="wide")

# 숫자를 만 단위로 깔끔하게 읽어주는 함수
def number_to_korean(num):
    if num < 10000: return "1만 미만" if num > 0 else "0"
    units = ["", "만", "억", "조"]
    result = []
    man_unit_val = num // 10000 
    idx = 1 
    while man_unit_val > 0:
        man_unit_val, mod = divmod(man_unit_val, 10000)
        if mod > 0:
            result.append(f"{mod:,}{units[idx]}")
        idx += 1
    return " ".join(reversed(result))

st.title("🏥 지점별 상담 및 성과 관리 시스템")

# 1. 지점 선택
branch = st.sidebar.selectbox("지점 선택", ["지점을 선택하세요", "강남점", "서초점"])

if branch != "지점을 선택하세요":
    st.header(f"📍 {branch} 상담 입력")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 기본 정보")
        patient_name = st.text_input("환자명", placeholder="이름을 입력하세요")
        patient_type = st.radio("환자 구분", ["신환", "구환"], horizontal=True)
        # 요청하신 유입 경로 리스트 수정
        inflow = st.selectbox("유입 경로", ["온라인", "소개환자", "외부영업", "워크-인", "기타"])
        # 요청하신 상담사 리스트 수정
        staff_name = st.selectbox("상담사", ["우선혜", "전누리", "임예린"])
        
    with col2:
        st.subheader("💰 상담 결과 및 금액")
        # 요청하신 상담 결과 리스트 수정
        result_status = st.selectbox("상담 결과", ["확정", "미확정", "보류", "상담없음"])
        
        def get_num(val):
            clean_val = re.sub(r'[^0-9]', '', val)
            return int(clean_val) if clean_val else 0

        sug_raw = st.text_input("상담 금액 (제시액)", placeholder="숫자만 입력")
        conf_raw = st.text_input("확정 금액 (총액)", placeholder="숫자만 입력")
        paid_raw = st.text_input("당일 수납 금액", placeholder="숫자만 입력")

        sug_val = get_num(sug_raw)
        conf_val = get_num(conf_raw)
        paid_val = get_num(paid_raw)
        
        if sug_val > 0 or conf_val > 0 or paid_val > 0:
            st.markdown("---")
            if sug_val > 0: st.markdown(f"**제시액:** {sug_val:,}원 ({number_to_korean(sug_val)} 원)")
            if conf_val > 0: st.markdown(f"**확정액:** {conf_val:,}원 ({number_to_korean(conf_val)} 원)")
            if paid_val > 0: st.markdown(f"**수납액:** <span style='font-size:20px; color:red;'>**{paid_val:,}원**</span> ({number_to_korean(paid_val)} 원)", unsafe_allow_html=True)
            st.markdown("---")

    content = st.text_area("📝 상담 상세 내용 및 특이사항", height=150)
    
    if st.button("💾 상담 내역 금고에 저장하기"):
        if not patient_name:
            st.error("⚠️ 환자명을 입력해 주세요.")
        else:
            # 🚀 Supabase로 데이터 전송
            data = {
                "branch": branch,
                "patient_name": patient_name,
                "patient_type": patient_type,
                "inflow": inflow,
                "staff_name": staff_name,
                "result": result_status, # 변수명 중복 방지
                "price_suggested": sug_val,
                "price_confirmed": conf_val,
                "price_paid": paid_val,
                "content": content
            }
            
            try:
                response = supabase.table("counseling_logs").insert(data).execute()
                st.success(f"✅ {patient_name} 님의 기록이 금고에 저장되었습니다!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ 저장 실패: {e}")

else:
    st.info("왼쪽 사이드바에서 근무하시는 지점을 먼저 선택해 주세요.")
