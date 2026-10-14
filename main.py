
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.write("영화의 장르 분포와 데이터 사이의 관계를 살펴봅니다.")

# main.py와 같은 폴더의 CSV 파일
DATA_FILE = "kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(
        DATA_FILE,
        dtype={"movieCd": str, "openDt": str}
    )

    required = [
        "movieCd", "movieNm", "openDt", "genre", "nation",
        "first_scrn", "first_show", "first_week_audi",
        "total_audi", "days_in_top10"
    ]

    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"CSV에 필요한 열이 없습니다: {missing}")

    # 여러 장르 중 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("미분류")
        .astype(str)
        .str.split("|", regex=False)
        .str[0]
        .str.strip()
        .replace("", "미분류")
    )

    return df


try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "kobis_movies.csv 파일을 찾을 수 없습니다. "
        "main.py와 같은 폴더에 업로드했는지 확인하세요."
    )
    st.stop()
except Exception as e:
    st.error(f"자료를 읽는 중 오류가 발생했습니다: {e}")
    st.stop()


# 요약 정보
col1, col2, col3 = st.columns(3)
col1.metric("분석 대상 영화", f"{len(df):,}편")
col2.metric("장르 종류", f"{df['genre'].nunique():,}개")
col3.metric("제작 국가 종류", f"{df['nation'].nunique():,}개")


# 그래프 1. 장르별 영화 편수
st.divider()
st.header("그래프 1. 장르별 영화 편수")
st.write("각 영화의 첫 번째 장르를 기준으로 편수를 집계합니다.")

genre_counts = (
    df["genre"]
    .value_counts()
    .rename_axis("장르")
    .reset_index(name="영화 편수")
)

fig = px.pie(
    genre_counts,
    names="장르",
    values="영화 편수",
    hole=0.48,
    title="장르별 영화 분포"
)

fig.update_traces(
    textposition="inside",
    textinfo="label",
    hovertemplate=(
        "장르: %{label}<br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent:.1%}"
        "<extra></extra>"
    )
)

fig.update_layout(
    height=520,
    legend_title_text="장르"
)

st.plotly_chart(fig, use_container_width=True)

with st.container(border=True):
    st.subheader("이 그래프로 알 수 있는 것")
    st.text_area(
        "분석 내용",
        placeholder="장르별 편수와 비율을 비교해 알 수 있는 점을 한 문장으로 적어 보세요.",
        height=90,
        key="genre_interpretation",
        label_visibility="collapsed"
    )


# 원자료 확인
st.divider()
st.subheader("분석에 사용한 영화 자료")

if st.checkbox("영화 자료 표 보기"):
    st.dataframe(df, use_container_width=True, hide_index=True)


# --------------------------------------------------
# 그래프 2. 장르별 영화 총 관객 트리맵
# --------------------------------------------------
st.divider()
st.header("그래프 2. 장르별 영화 총 관객")
st.write(
    "큰 칸일수록 총 관객이 많은 영화입니다. "
    "장르 안에서 영화별 관객 규모를 비교할 수 있습니다."
)

# 총 관객 수를 숫자로 변환
treemap_df = df.copy()
treemap_df["total_audi"] = pd.to_numeric(
    treemap_df["total_audi"],
    errors="coerce"
).fillna(0)

# 영화명이 같은 경우에도 구분할 수 있도록 영화 코드를 사용
treemap_df["영화 표시명"] = (
    treemap_df["movieNm"].fillna("영화명 미상").astype(str)
    + " ("
    + treemap_df["movieCd"].fillna("").astype(str)
    + ")"
)

# 트리맵 생성: 장르 안에 영화 배치, 칸 크기는 총 관객
fig2 = px.treemap(
    treemap_df,
    path=["genre", "영화 표시명"],
    values="total_audi",
    custom_data=["movieNm", "total_audi"],
    title="장르별 영화 총 관객 분포"
)

fig2.update_traces(
    hovertemplate=(
        "영화명: %{customdata[0]}<br>"
        "총 관객: %{customdata[1]:,.0f}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    height=700,
    margin=dict(t=60, l=10, r=10, b=10)
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# 그래프 해석 구역
with st.container(border=True):
    st.subheader("이 그래프로 알 수 있는 것")
    st.text_area(
        "분석 내용",
        placeholder=(
            "장르별로 총 관객이 많은 영화와 적은 영화를 비교해 "
            "알 수 있는 점을 한 문장으로 적어 보세요."
        ),
        height=90,
        key="treemap_interpretation",
        label_visibility="collapsed"
    )

