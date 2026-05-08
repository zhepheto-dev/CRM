import streamlit as st
import datetime
from streamlit_components_dot_ai import st_javascript # 필요시 자동설치되거나 무시됨

# 페이지 설정
st.set_page_config(page_title="Clinic Admin System", layout="wide")

# 실시간 콤마 입력을 위한 자바스크립트 주입
st.markdown("""
    <script>
    function formatNumber(el) {
        // 숫자만 남기기
        let val = el.value.replace(/[^0-9]/g, '');
        // 3자리마다 콤마 추가
        el.value = val.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    // 모든 입력창을 감시하며 숫자 입력 시 콤마 적용
    document.addEventListener('input', function (e) {
        if (e.target.tagName === 'INPUT' && e.target.type === 'text') {
            if (e.target.placeholder.includes('000')) {
                formatNumber(e.target);
            }
        }
    });
    </script>
""", unsafe_allow_html=True)

st.title("🏥 지점별 상담 및 성과 관리 시스템")

# 1. 지점 선택
branch = st.sidebar.selectbox("지점 선택", ["지점을 선택하세요", "강남점", "서초점"])

if branch != "지점을 선택하세요":
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
        result = st.selectbox("상담 결과", ["확정", "미확정", "보류", "상담없음"])
        
        # 입력창 안에서 실시간으로 콤마가 작동하도록 placeholder에 000을 넣었습니다.
        val_suggested = st.text_input("상담 금액 (제시액)", key="sug", placeholder="000,000")
        val_confirmed = st.text_input("확정 금액 (총액)", key="conf", placeholder="000,000")
        val_paid = st.text_input("당일 수납 금액", key="paid", placeholder="000,000")

        # 저장용 데이터 변환 함수 (콤마 제거 후 숫자로)
        def parse_money(val):
            if not val: return 0
            return int(val.replace(',', ''))

        price_suggested = parse_money(val_suggested)
        price_confirmed = parse_money(val_confirmed)
        price_paid = parse_money(val_paid)

    st.subheader("상담 상세 내용")
    content = st.text_area("상담 일지 및 특이사항")
    
    recall_date = st.date_input("리콜 예정일", datetime.date.today() + datetime.timedelta(days=7))
    
    if st.button("상담 내역 저장하기"):
        if not patient_name:
            st.error("환자명을 입력해 주세요.")
        else:
            st.success(f"✅ {patient_name} 님의 데이터가 준비되었습니다.")
            st.info(f"수납액 확인: {price_paid:,}원 (성공적으로 숫자로 인식됨)")

else:
    st.info("왼쪽 사이드바에서 근무하시는 지점을 먼저 선택해 주세요.")
