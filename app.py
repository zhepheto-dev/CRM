import streamlit as st
import datetime
import re

# 페이지 설정
st.set_page_config(page_title="Clinic Admin System", layout="wide")

# 숫자에 콤마를 찍어주는 함수
def format_currency(value):
    if not value: return ""
    # 숫자만 추출
    num = re.sub(r'[^0-9]', '', str(value))
    if num == "": return ""
    return f"{int(num):,}"

st.title("🏥 지점별 상담 및 성과 관리 시스템")

# 1. 지점 선택
branch = st.sidebar.selectbox("지점 선택", ["지원을 선택하세요", "강남점", "서초점"])

if branch != "지원을 선택하세요":
    st.header(f"📍 {branch} 상담 입력")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("기본 정보")
        patient_name = st.text_input("환자명", placeholder="이름을 입력하세요")
        patient_type = st.radio("환자 구분", ["신환", "구환"], horizontal=True)
        inflow = st.selectbox("유입 경로", ["온라인", "소개환자", "외부영업", "워크-인", "기타"])
        staff_name = st.selectbox("상담자", ["우선혜", "전누리", "임예린"])

        
    with col2:
        st.subheader("상담 결과 및 금액")
        result = st.selectbox("상담 결과", ["성공", "실패", "부재", "상담없음"])
        
        # 텍스트 입력창으로 변경하여 0을 없애고 콤마를 지원하게 만듭니다.
        val_suggested = st.text_input("상담 금액 (제시액)", key="sug", placeholder="예: 1,000,000")
        val_confirmed = st.text_input("확정 금액 (총액)", key="conf", placeholder="예: 800,000")
        val_paid = st.text_input("당일 수납 금액", key="paid", placeholder="예: 500,000")
        
        # 입력된 값에서 숫자만 추출하여 실제 데이터로 변환 (저장용)
        def to_int(s):
            try: return int(re.sub(r'[^0-9]', '', s))
            except: return 0

        price_suggested = to_int(val_suggested)
        price_confirmed = to_int(val_confirmed)
        price_paid = to_int(val_paid)

        # 입력 직후 콤마가 포함된 서식으로 안내
        if val_suggested or val_confirmed or val_paid:
            st.caption(f"✅ 입력 확인: 제시({price_suggested:,}원) / 확정({price_confirmed:,}원) / 수납({price_paid:,}원)")
        
    st.subheader("상담 상세 내용")
    content = st.text_area("상담 일지 및 특이사항")
    
    recall_date = st.date_input("리콜 예정일", datetime.date.today() + datetime.timedelta(days=7))
    
    if st.button("상담 내역 저장하기"):
        if not patient_name:
            st.error("환자명을 입력해 주세요.")
        else:
            st.success(f"✅ {patient_name} 님의 상담 내역이 임시 저장되었습니다.")
            st.write(f"최종 수납액: {price_paid:,}원")

else:
    st.info("왼쪽 사이드바에서 근무하시는 지점을 먼저 선택해 주세요.")
