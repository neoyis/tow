import streamlit as st
import pandas as pd

# 앱 제목
st.title("2025년 6월 기준 연령별 인구 현황 분석")

# CSV 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type="csv")

if uploaded_file is not None:
    # 데이터 읽기 (EUC-KR 인코딩)
    df = pd.read_csv(uploaded_file, encoding="euc-kr")

    # 원본 데이터 표시
    st.subheader("원본 데이터")
    st.dataframe(df)

    # '2025년06월_계_'로 시작하는 열만 추출
    age_columns = [col for col in df.columns if col.startswith("2025년06월_계_")]
    age_data = df[["행정구역", "총인구수"] + age_columns].copy()

    # 연령 숫자만 열 이름으로 정리
    age_data.rename(columns={col: col.replace("2025년06월_계_", "") for col in age_columns}, inplace=True)

    # 숫자형 변환
    for col in age_data.columns[2:]:
        age_data[col] = pd.to_numeric(age_data[col], errors="coerce")

    # '총인구수' 기준 상위 5개 지역 선택
    top5 = age_data.sort_values("총인구수", ascending=False).head(5)

    # 인구 변화 시각화
    st.subheader("상위 5개 행정구역 연령별 인구 변화")
    
    # index: 연령, columns: 행정구역 (그래프용 전처리)
    chart_data = top5.set_index("행정구역").drop(columns=["총인구수"]).T
    chart_data.index.name = "연령"

    st.line_chart(chart_data)

    # 선택 옵션으로 지역 선택
    st.subheader("개별 행정구역 인구 그래프 보기")
    selected_region = st.selectbox("행정구역을 선택하세요", top5["행정구역"])

    st.line_chart(chart_data[[selected_region]])

else:
    st.info("왼쪽 사이드바 또는 위에서 CSV 파일을 업로드해주세요.")
