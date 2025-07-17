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

import folium
from streamlit_folium import st_folium

st.header("4. 상위 5개 행정구역 지도 (Folium)")

# 위도/경도 매핑
location_map = {
    "서울특별시": [37.5665, 126.9780],
    "부산광역시": [35.1796, 129.0756],
    "대구광역시": [35.8722, 128.6025],
    "인천광역시": [37.4563, 126.7052],
    "광주광역시": [35.1595, 126.8526],
    "대전광역시": [36.3504, 127.3845],
    "울산광역시": [35.5384, 129.3114],
    "세종특별자치시": [36.4800, 127.2890],
    "경기도": [37.4138, 127.5183],
    "강원특별자치도": [37.8228, 128.1555],
    "충청북도": [36.6358, 127.4911],
    "충청남도": [36.5184, 126.8000],
    "전라북도": [35.7167, 127.1442],
    "전라남도": [34.8161, 126.4630],
    "경상북도": [36.4919, 128.8889],
    "경상남도": [35.4606, 128.2132],
    "제주특별자치도": [33.4996, 126.5312],
}

# 지도 준비
m = folium.Map(location=[36.5, 127.8], zoom_start=6)

for _, row in top5.iterrows():
    name = row["행정구역"]
    population = row["총인구수"]
    coord = location_map.get(name)

    if coord:
        folium.CircleMarker(
            location=coord,
            radius=population / 1000000,  # 인구 수에 따라 반지름 조절
            color="blue",
            fill=True,
            fill_color="skyblue",
            fill_opacity=0.7,
            popup=f"{name} ({population:,}명)",
            tooltip=name,
        ).add_to(m)

# Streamlit에서 지도 렌더링
st_data = st_folium(m, width=700, height=500)
