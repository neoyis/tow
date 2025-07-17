import streamlit as st
import pandas as pd
import re
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="2025년 5월 연령별 인구 현황 분석", layout="wide")

@st.cache
def load_data():
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

    rename_map[f"{prefix}총인구수"] = "총인구수"
    df = df.rename(columns=rename_map)

    numeric_cols = ["총인구수"] + age_col_names
    for c in numeric_cols:
        df[c] = df[c].astype(str).str.replace(",", "", regex=False).astype(int)

    df = df.drop(columns=[f"{prefix}연령구간인구수"], errors="ignore")

    df["행정구역"] = df["행정구역"].apply(lambda x: re.sub(r"\\s*\\(.*\\)$", "", x).strip())

    return df, age_col_names


# -----------------------
# 1. 데이터 불러오기
# -----------------------
df, age_cols = load_data()

st.title("2025년 5월 연령별 인구 현황 분석")

st.header("1. 원본 데이터")
st.dataframe(df, use_container_width=True)

# -----------------------
# 2. 총인구수 상위 5개
# -----------------------
st.header("2. 총인구수 상위 5개 행정구역")
top5 = df.nlargest(5, "총인구수").reset_index(drop=True)
st.dataframe(top5[["행정구역", "총인구수"]], use_container_width=True)

# -----------------------
# 3. 연령별 인구 라인차트
# -----------------------
st.header("3. 연령별 인구 분포 (상위 5개 행정구역)")
plot_df = top5.set_index("행정구역")[age_cols].T
plot_df.index = plot_df.index.astype(int)
plot_df = plot_df.sort_index()
st.line_chart(plot_df, use_container_width=True)

st.caption(
    "※ `st.line_chart`는 기본적으로 연령을 가로축, 인구수를 세로축으로 그립니다. "
    "요청하신 ‘연령‑세로축 / 인구‑가로축’ 형태는 기본 기능으로는 회전이 어려워 표준 방향으로 시각화했습니다."
)

# -----------------------
# 4. 지도 시각화 (Folium)
# -----------------------
st.header("4. 상위 5개 행정구역 지도 (Folium)")

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

m = folium.Map(location=[36.5, 127.8], zoom_start=6)

for _, row in top5.iterrows():
    name = row["행정구역"]
    population = row["총인구수"]
    coord = location_map.get(name)

    if coord:
        folium.CircleMarker(
            location=coord,
            radius=max(population / 1000000, 5),  # 최소 반지름 설정
            color="blue",
            fill=True,
            fill_color="skyblue",
            fill_opacity=0.7,
            popup=f"{name} ({population:,}명)",
            tooltip=name,
        ).add_to(m)

st_folium(m, width=700, height=500)
