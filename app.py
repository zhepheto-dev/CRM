import streamlit as st
from supabase import create_client, Client
import re
import pandas as pd

# 🔐 수파베이스 정보
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

# 💰 한글 금액 변환 함수
def number_to_korean(num):
    if num == 0: return "0"
    result = []
    temp_num = num
    if temp_num >= 100000000:
        억 = temp_num // 100000000
        result.append(f"{억:,}억")
        temp_num %= 100000000
    if temp_num >= 10000:
        만 = temp_num // 10000
        result.append(f"{만:,}만")
        temp_num %= 10000
    if temp_num >= 1000:
        천 = temp_num // 1000
        result.append(f"{천:,}천")
    return " ".join(result)

st.title("🏥 상담 내역 관리 및 조회 시스템")

tab1, tab2 = st.tabs(["📝 상담 내역 입력", "📊 저장 데이터 조회"])

# --- 탭 1: 상담 내역 입력 ---
with tab1:
    branch = st.sidebar.selectbox("지점 선택", ["지점을 선택하세요", "강남점", "서초점"])
    if branch != "지점을 선택하세요":
        st.header(f"📍 {branch} 입력창")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("👤 환자 및 상담 정보")
            p_name = st.text_input("환자명", key="p_name_final")
            p_type = st.radio("구분", ["신환", "구환"], horizontal=True)
            treatment = st.selectbox("상담항목", ["항목을 선택하세요", "임플란트", "교정", "미백/라미네이트", "충치/보철", "턱관절/이갈이", "기타"])
            inflow = st.selectbox("경로", ["온라인", "소개", "워크인", "기타"])
            staff = st.selectbox("상담자", ["우선혜", "전누리", "임예린"])
        with col2:
            st.subheader("💰 금액 및 예약 정보")
            res_status = st.selectbox("상담결과", ["확정", "미확정", "보류", "상담없음"])
            next_res = st.radio("다음 예약 여부", ["예약 완료", "미예약", "추후 연락"], horizontal=True)
            
            def get_val(v):
                c = re.sub(r'[^0-9]', '', str(v))
                return int(c) if c else 0

            s_in = st.text_input("상담금액", value="0", key="s_in")
            c_in = st.text_input("확정금액", value="0", key="c_in")
            p_in = st.text_input("수납금액", value="0", key="p_in")
            s_v, c_v, p_v = get_val(s_in), get_val(c_in), get_val(p_in)

            if s_v > 0 or c_v > 0 or p_v > 0:
                st.info("📊 **금액 상세 요약**")
                st.write(f"* 상담금액: {s_v:,}원 ({number_to_korean(s_v)} 원)")
                st.write(f"* 확정금액: {c_v:,}원 ({number_to_korean(c_v)} 원)")
                st.write(f"✅ **수납금액: {p_v:,}원 ({number_to_korean(p_v)} 원)**")

        content = st.text_area("📝 상담 상세 내용")
        if st.button("💾 상담 내역 저장하기"):
            if not p_name or treatment == "항목을 선택하세요":
                st.error("⚠️ 환자명과 상담항목을 확인해주세요.")
            else:
                try:
                    data = {"branch": branch, "patient_name": p_name, "patient_type": p_type, "treatment": treatment, "inflow": inflow, "staff_name": staff, "result": res_status, "next_reservation": next_res, "price_suggested": s_v, "price_confirmed": c_v, "price_paid": p_v, "content": content}
                    supabase.table("counseling_logs").insert(data).execute()
                    st.success("✅ 저장 완료! 고생하셨습니다!")
                    st.balloons()
                except Exception as e:
                    st.error(f"저장 실패: {e}")

# --- 탭 2: 저장 데이터 조회 (에러 박멸 구간) ---
with tab2:
    st.header("🔍 전체 상담 내역 조회")
    if st.button("🔄 최신 데이터 불러오기"):
        try:
            res = supabase.table("counseling_logs").select("*").order("created_at", desc=True).execute()
            df = pd.DataFrame(res.data)
            
            if not df.empty:
                # 1. 원본 숫자 유지용 컬럼 (합계용)
                num_cols = ['price_suggested', 'price_confirmed', 'price_paid']
                for col in num_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                
                # 2. 컬럼명 변경
                df.columns = ['ID', '시간', '지점', '환자명', '구분', '상담항목', '경로', '상담자', '결과', '상담금액', '확정금액', '수납금액', '내용', '예약여부']
                
                # 3. [에러 해결 핵심] 스타일링 함수를 쓰지 않고 데이터를 '글자'로 미리 변환
                # 이렇게 하면 스트림릿 포맷터와 충돌이 절대 안 납니다.
                df['상담금액'] = df['상담금액'].apply(lambda x: f"{x:,}원")
                df['확정금액'] = df['확정금액'].apply(lambda x: f"{x:,}원")
                df['수납금액'] = df['수납금액'].apply(lambda x: f"{x:,}원")
                
                # 4. 그냥 데이터프레임만 출력 (style.format을 안 쓰는 게 포인트!)
                st.dataframe(df, use_container_width=True)
                
                st.divider()
                # 합계 계산은 변환 전의 원본 데이터를 다시 가져오거나 변환 전 값을 활용
                total_paid = pd.to_numeric(df['수납금액'].str.replace('원','').str.replace(',','')).sum()
                st.metric("총 수납 금액 합계", f"{int(total_paid):,}원")
            else:
                st.warning("조회할 데이터가 없습니다.")
        except Exception as e:
            st.error(f"조회 중 오류 발생: {str(e)}")
