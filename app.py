# --- 탭 2: 저장 데이터 조회 (순서 교정 및 날짜 수정) ---
with tab2:
    st.header("🔍 전체 상담 내역 조회")
    if st.button("🔄 최신 데이터 불러오기"):
        try:
            res = supabase.table("counseling_logs").select("*").order("created_at", desc=True).execute()
            df = pd.DataFrame(res.data)
            
            if not df.empty:
                # 1. 시간 포맷 수정 (일자까지만 표시)
                if 'created_at' in df.columns:
                    df['created_at'] = pd.to_datetime(df['created_at']).dt.date
                
                # 2. 지정하신 대로 데이터 컬럼 순서 재배치 (밀림 현상 해결)
                # 수파베이스 테이블의 컬럼명에 맞춰 순서를 강제로 고정합니다.
                # (주의: 실제 DB 컬럼명과 일치해야 합니다. 아래는 요청하신 논리에 따른 재배치입니다.)
                cols_order = [
                    'created_at',       # 시간 (일자까지)
                    'branch',           # 지점
                    'patient_name',     # 환자명
                    'patient_type',     # 구분
                    'inflow',           # 내원경로 (기존 '상담항목' 위치)
                    'staff_name',       # 상담자 (기존 '경로' 위치)
                    'result',           # 상담결과 (기존 '상담자' 위치)
                    'price_suggested',  # 상담금액 (기존 '결과' 위치)
                    'price_confirmed',  # 확정금액 (기존 '상담금액' 위치)
                    'price_paid',       # 수납금액 (기존 '확정금액' 위치)
                    'content',          # 상담내용 (기존 '수납금액' 위치)
                    'treatment'         # 상담항목 (기존 '내용' 위치)
                ]
                
                # 존재하는 컬럼만 선별하여 순서 적용
                actual_cols = [c for c in cols_order if c in df.columns]
                df = df[actual_cols]
                
                # 3. 한글 컬럼명 매핑 (7가지 항목 수정 반영)
                df.columns = [
                    '일자', '지점', '환자명', '구분', 
                    '내원경로', '상담자', '상담결과', 
                    '상담금액', '확정금액', '수납금액', 
                    '상담내용', '상담항목'
                ]
                
                # 4. 숫자 컬럼 콤마 포맷팅 (글자로 변환하여 에러 방지)
                num_cols = ['상담금액', '확정금액', '수납금액']
                for col in num_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                
                display_df = df.copy()
                for col in num_cols:
                    display_df[col] = display_df[col].apply(lambda x: f"{x:,}원")
                
                # 5. 최종 출력
                st.table(display_df)
                
                st.divider()
                st.metric("총 수납 금액 합계", f"{int(df['수납금액'].sum()):,}원")
            else:
                st.warning("조회할 데이터가 없습니다.")
        except Exception as e:
            st.error(f"조회 중 오류 발생: {str(e)}")
