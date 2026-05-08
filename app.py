import streamlit as st
import datetime

# 페이지 설정
st.set_page_config(page_title="Clinic Admin System", layout="wide")

st.title("🏥 지점별 상담 및 성과 관리 시스템")

# 1. 지점 선택 (A안 반영)
branch = st.sidebar.selectbox("지점 선택", ["지점을 선택하세요", "강남점", "서초점"])

if branch != "지점을 선택하세요":
    st.header(f"📍 {branch} 상담 입력")
    
    # 레이아웃 나누기
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("기본 정보")
        patient_name = st.text_input("환자명")
        patient_type = st.radio("환자 구분", ["신환", "구환"], horizontal=True)
        inflow = st.selectbox("유입 경로", ["네이버 GFA", "네이버 SA", "네이버 카페", "지인소개", "기타"])
        staff_name = st.selectbox("상담사", ["김실장", "이실장", "박실장"]) # 나중에 관리자 기능에서 수정 가능하게 변경
        
    with col2:
        st.subheader("상담 결과 및 금액")
        result = st.selectbox("상담 결과", ["성공", "실패", "부재", "상담없음"])
        price_suggested = st.number_input("상담 금액 (제시액)", min_value=0, step=10000)
        price_confirmed = st.number_input("확정 금액 (총액)", min_value=0, step=10000)
        price_paid = st.number_input("당일 수납 금액", min_value=0, step=10000)
        
    st.subheader("상담 상세 내용")
    content = st.text_area("상담 일지 및 특이사항")
    
    recall_date = st.date_input("리콜 예정일", datetime.date.today() + datetime.timedelta(days=7))
    
    if st.button("상담 내역 저장하기"):
        st.success(f"{patient_name} 님의 상담 내역이 임시 저장되었습니다. (DB 연결 예정)")

else:
    st.info("왼쪽 사이드바에서 근무하시는 지점을 먼저 선택해 주세요.")
