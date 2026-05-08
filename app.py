import streamlit as st
from supabase import create_client, Client
import re
import pandas as pd

# 🔐 수파베이스 설정
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

# --- 탭 1: 입력부 ---
with tab1:
    branch = st.sidebar.selectbox("지점 선택", ["지점을 선택하세요", "강남점", "서초점"])
    if branch != "지점을 선택하세요":
        st.header(f"📍 {branch} 입력창")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("👤 환자 및 상담 정보")
            patient_name = st.text_input("환자명", key="p_input")
            patient_type = st.radio("구분", ["신환", "구환"], horizontal=True)
            consult_item = st.selectbox("상담항목", ["항목을 선택하세요", "임플란트", "교정", "미백/라미네이트", "충치/보철", "턱관절/이갈이", "기타"])
            inflow = st.selectbox("경로", ["온라인", "소개", "워크인", "기타"])
            staff_name = st.selectbox("상담자", ["우선혜", "전누리", "임예린"])
        with col2:
            st.subheader("💰 금액 및 예약 정보")
            result_status = st.selectbox("상담결과", ["확정", "미확정", "보류", "상담없음"])
            next_reservation = st.radio("다음 예약 여부", ["예약 완료", "미예약", "추후 연락"], horizontal=True)
            
            def get_num(val):
                clean = re.sub(r'[^0-9]', '', str(val))
                return int(clean) if clean else 0

            s_raw = st.text_input("상담금액", value="0", key="s_raw")
            c_raw = st.text_input("확정금액", value="0", key="c_raw")
            p_raw = st.text_input("수납금액", value="0", key="p_raw")
            s_val, c_val, p_val = get_num(s_raw), get_num(c_raw), get_num(p_raw)

            if s_val > 0 or c_val > 0 or p_val > 0:
                st.info("📊 **금액 상세 요약**")
                st.write(f"* 상담금액: {s_val:,}원 ({number_to_korean(s_val)} 원)")
                st.write(f"* 확정금액: {c_val:,}원 ({number_to_korean(c_val)} 원)")
                st.write(f"✅ **수납금액: {p_val:,}원 ({number_to_korean(p_val)} 원)**")

        content = st.text_area("📝 상담 상세 내용")
        if st.button("💾 상담 내역 저장하기"):
            if not patient_name or consult_item == "항목을 선택하세요":
                st.error("⚠️ 환자명과 상담항목을 확인해주세요.")
            else:
                try:
                    data = {"branch": branch, "patient_name": patient_name, "patient_type": patient_type, "treatment": consult_item, "inflow": inflow, "staff_name": staff_name, "result": result_status, "next_reservation": next_reservation, "price_suggested": s_val, "price_confirmed": c_val, "price_paid": p_val, "content": content}
                    supabase.table("counseling_logs").insert(data).execute()
                    st.success("✅ 저장 완료!")
                    st.balloons()
                except Exception as e:
                    st.error(f"저장 실패: {e}")

# --- 탭 2: 조회부 (날짜 및 순서 교정) ---
with tab2:
    st.header("🔍 전체 상담 내역 조회")
    if st.button("🔄 최신 데이터 불러오기"):
        try:
            res = supabase.table("counseling_logs").select("*").order("created_at", desc=True).execute()
            df = pd.DataFrame(res.data)
            
            if not df.empty:
                # 1. 일자 수정 (시간 제거)
                df['created_at'] = pd.to_datetime(df['created_at']).dt.date
                
                # 2. 숫자 변환 및 합계용 데이터 준비
                for c in ['price_suggested', 'price_confirmed', 'price_paid']:
                    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(int)
                
                total_sum = df['price_paid'].sum()

                # 3. [핵심] zhepheto님이 요청하신 순서로 데이터 재배치
                # 시간, 지점, 환자명, 구분, 내원경로, 상담자, 상담결과, 상담금액, 확정금액, 수납금액, 상담내용, 상담항목
                df_reordered = df[[
                    'created_at', 'branch', 'patient_name', 'patient_type', 
                    'inflow', 'staff_name', 'result', 
                    'price_suggested', 'price_confirmed', 'price_paid', 
                    'content', 'treatment'
                ]]

                # 4. 한글 컬럼명 적용
                df_reordered.columns = [
                    '일자', '지점', '환자명', '구분', 
                    '내원경로', '상담자', '상담결과', 
                    '상담금액', '확정금액', '수납금액', 
                    '상담내용', '상담항목'
                ]

                # 5. 금액 컬럼을 미리 '글자'로 변환 (에러 박멸)
                display_df = df_reordered.copy()
                for col in ['상담금액', '확정금액', '수납금액']:
                    display_df[col] = display_df[col].apply(lambda x: f"{x:,}원")
                
                # 6. 표 출력
                st.table(display_df)
                
                st.divider()
                st.metric("총 수납 금액 합계", f"{total_sum:,}원")
            else:
                st.warning("데이터가 없습니다.")
        except Exception as e:
            st.error(f"조회 중 오류 발생: {str(e)}")
