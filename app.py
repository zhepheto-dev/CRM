import streamlit as st
import datetime
import re
from supabase import create_client, Client

# 🔐 Supabase 설정 (주소와 키를 다시 한번 확인해서 넣어주세요)
SUPABASE_URL = "https://xptuxxzwvwjxpzeelsjf.supabase.co"
SUPABASE_KEY = "sb_publishable_ZAcVzMbVwwl1A-YNZIJucA_D6gTqcd8"

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = get_supabase()
except Exception as e:
    st.error(f"연결 오류: {e}")

st.set_page_config(page_title="Clinic Admin System", layout="wide")

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

st.title("🏥 지점별 상담 및 성과 관리 시스템")

branch = st.sidebar.selectbox("지점 선택", ["지점을 선택하세요", "강남점", "서초점"])

if branch != "지점을 선택하세요":
    st.header(f"📍 {branch} 상담 입력")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 기본 정보")
        patient_name = st.text_input("환자명")
        patient_type = st.radio("환자 구분", ["신환", "구환"], horizontal=True)
        inflow = st.selectbox("유입 경로", ["온라인", "소개환자", "외부영업", "워크-인", "기타"])
        staff_name = st.selectbox("상담사", ["우선혜", "전누리", "임예린"])
        
    with col2:
        st.subheader("💰 상담 결과 및 금액")
        result_status = st.selectbox("상담 결과", ["확정", "미확정", "보류", "상담없음"])
        
        def get_num(val):
            clean_val = re.sub(r'[^0-9]', '', val)
            return int(clean_val) if clean_val else 0

        sug_val = get_num(st.text_input("상담 금액 (제시액)"))
        conf_val = get_num(st.text_input("확정 금액 (총액)"))
        paid_val = get_num(st.text_input("당일 수납 금액"))

        if sug_val > 0 or conf_val > 0 or paid_val > 0:
            st.info(f"💡 수납 확인: {paid_val:,}원 ({number_to_korean(paid_val)} 원)")

    content = st.text_area("📝 상담 상세 내용 및 특이사항", height=150)
    
    if st.button("💾 상담 내역 저장하기"):
        if not patient_name:
            st.error("⚠️ 환자명을 입력해 주세요.")
        else:
            # 🚀 한글 인코딩 문제를 방지하기 위해 딕셔너리 형태로 안전하게 전달
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
                
                # 전송 전송!
                supabase.table("counseling_logs").insert(data).execute()
                st.success(f"✅ {patient_name} 님의 기록이 저장되었습니다!")
                st.balloons()
            except Exception as e:
                # 에러 메시지를 더 자세히 보기 위해 e를 출력
                st.error(f"❌ 저장 실패: {str(e)}")

else:
    st.info("지점을 선택해 주세요.")
