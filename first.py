import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="2025년 5월 연령별 인구 현황 분석", layout="wide")

# 캐시 함수: 버전에 따라 @st.cache or @st.cache_data 사용
@st.cache  # @st.cache_data → 일부 배포 환경에서 오류 가능성
def load_data():
    """CSV 로드 및 전처리"""
    df = pd.read_csv("202505_202505_연령별인구현황_월간.csv", encoding="euc-kr")

    prefix = "2025년05월_계_"
    age_cols = [c for c in df.columns if c.startswith(prefix)]

    rename_map = {}
    age_col_names = []
    for col in age_cols:
        if col.endswith("총인구수") or col.endswith("연령구간인구수"):
            continue
        new = (
            col.replace(prefix, "")
            .replace("세", "")
            .replace(" 이상", "")
            .strip()
        )
        rename_map[col] = new
        age_col_names.append(new)

    # 총인구수 컬럼도 짧게
    rename_map[f"{prefix}총인구수"] = "총인구수"

    # 컬럼명 변경
    df = df.rename(columns=rename_map)

    # 숫자형 변환
    numeric_cols = ["총인구수"] + age_col_names
    for c in numeric_cols:
        df[c] = df[c].astype(str).str.replace(",", "", regex=False).astype(int)

    # 불필요 컬럼 제거
    df = df.drop(columns=[f"{prefix}연령구간인구수"], errors="ignore")

    # 행정구역 이름 정리
    df["행정구역"] = df["행정구역"].apply(lambda x: re.sub(r"\\s*\\(.*\\)$", "", x).strip())

    return df, age_col_names


# ---- 데이터 불러오기 ----
df, age_cols = load_data()

# ---- UI ----
st.title("2025년 5월 연령별 인구 현황 분석")

st.header("1. 원본 데이터")
st.dataframe(df, use_container_width=True)

st.header("2. 총인구수 상위 5개 행정구역")
top5 = df.nlargest(5, "총인구수").reset_index(drop=True)
st.dataframe(top5[["행정구역", "총인구수"]], use_container_width=True)

# ---- 선 그래프 ----
plot_df = top5.set_index("행정구역")[age_cols].T
plot_df.index = plot_df.index.astype(int)
plot_df = plot_df.sort_index()

st.header("3. 연령별 인구 분포 (상위 5개 행정구역)")
st.line_chart(plot_df, use_container_width=True)

st.caption(
    "※ `st.line_chart`는 기본적으로 연령을 가로축, 인구수를 세로축으로 그립니다. "
    "요청하신 ‘연령‑세로축 / 인구‑가로축’ 형태는 기본 기능으로는 회전이 어려워 표준 방향으로 시각화했습니다."
)
