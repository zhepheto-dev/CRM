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

# 🎨 [긴급교정] 보류는 절대 빨간색이 될 수 없는 무결점 스타일 함수
def apply_final_style(row):
    # 1. '상담결과' 값을 안전하게 추출 (결과가 없으면 빈 문자열)
    val = str(row.get('상담결과', '')).strip()
    
    # 2. 기본값은 스타일 없음 (공백 문자열)
    # 리스트 컴프리헨션을 사용하여 행 전체에 동일 스타일 적용
    styles = [''] * len(row)
    
    # 3. 오직 '확정'일 때만 노란색
    if val == "확정":
        styles = ['color: #E6B400; font-weight: bold;'] * len(row)
    
    # 4. 오직 '미확정'일 때만 빨간색 (보류, 상담없음, None은 절대 통과 못함)
    elif val == "미확정":
        styles = ['color: #D32F2F; font-weight: bold;'] * len(row)
        
    return styles

st.title("🏥 상담 내역 관리 및 조회 시스템")

tab1, tab2 = st.tabs(["📝 상담 내역 입력", "📊 저장 데이터 조회"])

# --- 탭 1: 입력 (기존 로직 유지) ---
with tab1:
    branch = st.sidebar.selectbox("지점 선택", ["지점을 선택하세요", "강남점", "서초점"])
    if branch != "지점을 선택하세요":
        st.header(f"📍 {branch} 입력창")
        col1, col2 = st.columns(2)
        with col1:
            p_name = st.text_input("환자명")
            p_type = st.radio("구분", ["신환", "구환"], horizontal=True)
            c_item = st.selectbox("상담항목", ["항목을 선택하세요", "임플란트", "교정", "미백/라미네이트", "충치/보철", "턱관절/이갈이", "기타"])
            inflow = st.selectbox("경로", ["온라인", "소개", "워크인", "기타"])
            s_name = st.selectbox("상담자", ["우선혜", "전누리", "임예린"])
        with col2:
            res_status = st.selectbox("상담결과", ["확정", "미확정", "보류", "상담없음"])
            next_res = st.radio("다음 예약 여부", ["예약 완료", "미예약", "추후 연락"], horizontal=True)
            
            def clean_num(val):
                c = re.sub(r'[^0-9]', '', str(val))
                return int(c) if c else 0

            s_r = clean_num(st.text_input("상담금액", "0"))
            c_r = clean_num(st.text_input("확정금액", "0"))
            p_r = clean_num(st.text_input("수납금액", "0"))

        if st.button("💾 저장하기"):
            if not p_name or c_item == "항목을 선택하세요":
                st.error("⚠️ 필수 항목 입력 필요")
            else:
                try:
                    d = {"branch": branch, "patient_name": p_name, "patient_type": p_type, "treatment": c_item, "inflow": inflow, "staff_name": s_name, "result": res_status, "next_reservation": next_res, "price_suggested": s_r, "price_confirmed": c_r, "price_paid": p_r, "content": st.text_area("📝 상담 상세 내용")}
                    supabase.table("counseling_logs").insert(d).execute()
                    st.success("✅ 저장 성공!")
                except Exception as e:
                    st.error(f"저장 실패: {e}")

# --- 탭 2: 조회 (스타일링 오류 완전 해결) ---
with tab2:
    st.header("🔍 전체 상담 내역 조회")
    if st.button("🔄 최신 데이터 불러오기"):
        try:
            res = supabase.table("counseling_logs").select("*").order("created_at", desc=True).execute()
            df = pd.DataFrame(res.data)
            
            if not df.empty:
                # 데이터 전처리
                df['created_at'] = pd.to_datetime(df['created_at']).dt.date
                for col in ['price_suggested', 'price_confirmed', 'price_paid']:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                
                # [순서] 상담항목을 구분 뒤로 배치
                df_view = df[['created_at', 'branch', 'patient_name', 'patient_type', 'treatment', 'inflow', 'staff_name', 'result', 'price_suggested', 'price_confirmed', 'price_paid', 'content']]
                
                # [한글 컬럼]
                df_view.columns = ['일자', '지점', '환자명', '구분', '상담항목', '내원경로', '상담자', '상담결과', '상담금액', '확정금액', '수납금액', '상담내용']

                # 금액 콤마 포맷팅 (스타일링과 충돌 방지를 위해 별도 apply 사용)
                for col in ['상담금액', '확정금액', '수납금액']:
                    df_view[col] = df_view[col].apply(lambda x: f"{x:,}원")
                
                # 🎨 스타일 적용: 보류는 그 어떤 if문도 통과하지 못해 무조건 기본색 유지
                st.dataframe(df_view.style.apply(apply_final_style, axis=1), use_container_width=True)
                
                st.divider()
                
                # 하단 지표 순서: 상담 -> 확정 -> 수납
                m1, m2, m3 = st.columns(3)
                m1.metric("총 상담 금액 합계", f"{df['price_suggested'].sum():,}원")
                m2.metric("총 확정 금액 합계", f"{df['price_confirmed'].sum():,}원")
                m3.metric("총 수납 금액 합계", f"{df['price_paid'].sum():,}원")
        except Exception as e:
            st.error(f"오류: {str(e)}")
