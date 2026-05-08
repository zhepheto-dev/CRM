import streamlit as st
from supabase import create_client, Client
import re
import pandas as pd

# 🔐 수파베이스 설정 (유지)
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

# 🎨 폰트 색상 함수 (보류는 절대 색상이 바뀌지 않도록 수정)
def font_style(row):
    # 기본은 색상 없음
    color = "color: inherit;"
    
    # 상담결과 값 추출 (공백 제거하여 정확히 비교)
    res_val = str(row['상담결과']).strip()
    
    if res_val == '확정':
        color = 'color: #E6B400;' # 노란색
    elif res_val == '미확정':
        color = 'color: #D32F2F;' # 빨간색
    else:
        # 보류, 상담없음 등 그 외 모든 경우는 기본 색상 유지
        color = 'color: inherit;'
        
    return [color] * len(row)

st.title("🏥 상담 내역 관리 및 조회 시스템")

tab1, tab2 = st.tabs(["📝 상담 내역 입력", "📊 저장 데이터 조회"])

# --- 탭 1: 입력부 (기존 로직 유지) ---
with tab1:
    branch = st.sidebar.selectbox("지점 선택", ["지점을 선택하세요", "강남점", "서초점"])
    if branch != "지점을 선택하세요":
        st.header(f"📍 {branch} 입력창")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("👤 환자 및 상담 정보")
            p_name = st.text_input("환자명")
            p_type = st.radio("구분", ["신환", "구환"], horizontal=True)
            c_item = st.selectbox("상담항목", ["항목을 선택하세요", "임플란트", "교정", "미백/라미네이트", "충치/보철", "턱관절/이갈이", "기타"])
            inflow = st.selectbox("경로", ["온라인", "소개", "워크인", "기타"])
            s_name = st.selectbox("상담자", ["우선혜", "전누리", "임예린"])
        with col2:
            st.subheader("💰 금액 및 예약 정보")
            res_status = st.selectbox("상담결과", ["확정", "미확정", "보류", "상담없음"])
            next_res = st.radio("다음 예약 여부", ["예약 완료", "미예약", "추후 연락"], horizontal=True)
            
            def clean_num(val):
                c = re.sub(r'[^0-9]', '', str(val))
                return int(c) if c else 0

            s_r, c_r, p_r = st.text_input("상담금액", "0"), st.text_input("확정금액", "0"), st.text_input("수납금액", "0")
            sv, cv, pv = clean_num(s_r), clean_num(c_r), clean_num(p_r)

            if sv > 0 or cv > 0 or pv > 0:
                st.info("📊 금액 요약")
                st.write(f"* 상담: {sv:,}원 / * 확정: {cv:,}원 / ✅ 수납: {pv:,}원")

        content = st.text_area("📝 상담 상세 내용")
        if st.button("💾 저장하기"):
            if not p_name or c_item == "항목을 선택하세요":
                st.error("⚠️ 필수 항목을 입력해주세요.")
            else:
                try:
                    d = {"branch": branch, "patient_name": p_name, "patient_type": p_type, "treatment": c_item, "inflow": inflow, "staff_name": s_name, "result": res_status, "next_reservation": next_res, "price_suggested": sv, "price_confirmed": cv, "price_paid": pv, "content": content}
                    supabase.table("counseling_logs").insert(d).execute()
                    st.success("✅ 저장 성공!")
                except Exception as e:
                    st.error(f"저장 실패: {e}")

# --- 탭 2: 조회부 ---
with tab2:
    st.header("🔍 전체 상담 내역 조회")
    if st.button("🔄 최신 데이터 불러오기"):
        try:
            res = supabase.table("counseling_logs").select("*").order("created_at", desc=True).execute()
            df = pd.DataFrame(res.data)
            
            if not df.empty:
                # 1. 데이터 전처리
                df['created_at'] = pd.to_datetime(df['created_at']).dt.date
                for col in ['price_suggested', 'price_confirmed', 'price_paid']:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                
                # 2. 합계 미리 계산
                sum_s, sum_c, sum_p = df['price_suggested'].sum(), df['price_confirmed'].sum(), df['price_paid'].sum()

                # 3. [요청반영] 순서: 구분 다음 상담항목
                df_view = df[[
                    'created_at', 'branch', 'patient_name', 'patient_type', 'treatment',
                    'inflow', 'staff_name', 'result', 'price_suggested', 'price_confirmed',
                    'price_paid', 'content'
                ]]

                # 4. 한글 컬럼명 매핑
                df_view.columns = [
                    '일자', '지점', '환자명', '구분', '상담항목',
                    '내원경로', '상담자', '상담결과', '상담금액', '확정금액',
                    '수납금액', '상담내용'
                ]

                # 5. 금액 포맷팅
                display_df = df_view.copy()
                for c in ['상담금액', '확정금액', '수납금액']:
                    display_df[c] = display_df[c].apply(lambda x: f"{x:,}원")
                
                # 6. 스타일 적용 (확정 노랑, 미확정 빨강만!)
                styled_df = display_df.style.apply(font_style, axis=1)
                st.dataframe(styled_df, use_container_width=True)
                
                st.divider()
                
                # 7. [요청반영] 합계 순서: 상담 -> 확정 -> 수납
                m1, m2, m3 = st.columns(3)
                m1.metric("총 상담 금액 합계", f"{sum_s:,}원")
                m2.metric("총 확정 금액 합계", f"{sum_c:,}원")
                m3.metric("총 수납 금액 합계", f"{sum_p:,}원")
            else:
                st.warning("데이터가 없습니다.")
        except Exception as e:
            st.error(f"조회 실패: {str(e)}")
