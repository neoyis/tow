import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Streamlit 페이지 설정
st.set_page_config(page_title="상위 5개 행정구역 인구 지도", page_icon="🗺️", layout="wide")

st.title("🗺️ 상위 5개 행정구역 인구수 지도 시각화")

# CSV 파일 읽기
df = pd.read_csv("202505_202505_연령별인구현황_월간.csv", encoding='euc-kr')

# 행정구역 열에서 괄호 안 숫자 제거
df['행정구역'] = df['행정구역'].str.replace(r"\s*\(\d+\)", "", regex=True).str.strip()

# 인구수 전처리
df['총인구수'] = df['2025년05월_계_총인구수'].str.replace(',', '').astype(int)

# 연령별 컬럼 전처리
age_columns = [col for col in df.columns if col.startswith('2025년05월_계_') and ('세' in col or '100세 이상' in col)]
new_columns = []
for col in age_columns:
    if '100세 이상' in col:
        new_columns.append('100세 이상')
    else:
        new_columns.append(col.replace('2025년05월_계_', '').replace('세', '') + '세')

df_age = df[['행정구역', '총인구수'] + age_columns].copy()
df_age.columns = ['행정구역', '총인구수'] + new_columns

# 상위 5개 행정구역 추출
top5_df = df_age.sort_values(by='총인구수', ascending=False).head(5)

# 원 표시할 좌표 (행정구역명 수정 후 사용)
region_coords = {
    "경기도": [37.4138, 127.5183],
    "서울특별시": [37.5665, 126.9780],
    "부산광역시": [35.1796, 129.0756],
    "경상남도": [35.4606, 128.2132],
    "인천광역시": [37.4563, 126.7052]
}

# 지도 생성
m = folium.Map(location=[36.5, 127.5], zoom_start=7)

# 크고 선명한 원(circle) 추가
for _, row in top5_df.iterrows():
    region = row['행정구역']
    pop = row['총인구수']
    coords = region_coords.get(region)
    if coords:
        folium.Circle(
            location=coords,
            radius=int(pop) / 300,   # 원 크기 조정 (필요 시 /15 ~ /30 사이에서 조절)
            color='Deeppink',
            fill=True,
            fill_color='Lightpink',
            fill_opacity=0.6,       # 불투명하게 표시
            popup=f"{region} : {pop:,}명",
            tooltip=region
        ).add_to(m)

# 지도 출력
st.subheader("🗺️ 지도에서 상위 5개 행정구역 인구수 확인")
st_folium(m, width=900, height=600)

# 원본 데이터도 출력
st.subheader("📊 원본 데이터 (상위 5개 행정구역)")
st.dataframe(top5_df)
