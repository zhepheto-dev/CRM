import streamlit as st
import datetime
import re

# 페이지 설정
st.set_page_config(page_title="Clinic Admin System", layout="wide")

# 숫자를 한글 읽기로 변환하는 함수
def number_to_korean(num):
    if num == 0: return "0"
    units = ["", "만", "억", "조"]
    result = []
    idx = 0
    while num > 0:
        num, mod = divmod(num, 10000)
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
        inflow = st.selectbox("유입 경로", ["온라인", "소개환자", "외부영업", "워크-인", "기타"])
        staff_name = st.selectbox("상담자", ["우선혜", "전누리", "임예린"])
        
    with col2:
        st.subheader("💰 상담 결과 및 금액")
        result = st.selectbox("상담 결과", ["확정", "미확정", "보류", "상담없음"])
        
        # 숫자 추출 함수
        def get_num(val):
            clean_val = re.sub(r'[^0-9]', '', val)
            return int(clean_val) if clean_val else 0

        # 금액 입력창
        sug_raw = st.text_input("상담 금액 (제시액)", placeholder="숫자만 입력")
        conf_raw = st.text_input("확정 금액 (총액)", placeholder="숫자만 입력")
        paid_raw = st.text_input("당일 수납 금액", placeholder="숫자만 입력")

        # 실시간 큰 글씨 요약 (콤마 + 한글 읽기)
        sug_val = get_num(sug_raw)
        conf_val = get_num(conf_raw)
        paid_val = get_num(paid_raw)
        
        if sug_val > 0 or conf_val > 0 or paid_val > 0:
            st.markdown("---")
            st.markdown(f"**상담 제시:** <span style='font-size:20px; color:#2E86C1;'>**{sug_val:,}**원</span> <span style='color:gray;'>({number_to_korean(sug_val)}원)</span>", unsafe_allow_html=True)
            st.markdown(f"**최종 확정:** <span style='font-size:20px; color:#28B463;'>**{conf_val:,}**원</span> <span style='color:gray;'>({number_to_korean(conf_val)}원)</span>", unsafe_allow_html=True)
            st.markdown(f"**당일 수납:** <span style='font-size:24px; color:#E74C3C;'>**{paid_val:,}**원</span> <span style='color:gray;'>({number_to_korean(paid_val)}원)</span>", unsafe_allow_html=True)
            st.markdown("---")
        
    st.subheader("📝 상담 상세 내용")
    content = st.text_area("상담 일지 및 특이사항", height=150)
    
    recall_date = st.date_input("리콜 예정일", datetime.date.today() + datetime.timedelta(days=7))
    
    if st.button("💾 상담 내역 저장하기"):
        if not patient_name:
            st.error("⚠️ 환자명을 입력해 주세요.")
        else:
            st.success(f"✅ {patient_name} 님의 상담 내역이 준비되었습니다.")
            st.write(f"**[요약]** {branch} / {patient_type} / 수납액: {paid_val:,}원 ({number_to_korean(paid_val)}원)")

else:
    st.info("왼쪽 사이드바에서 근무하시는 지점을 먼저 선택해 주세요.")
