
import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

# 제목
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption(
    "1년간 박스오피스 10위권에 든 영화 중 "
    "이 기간에 개봉한 216편의 자료를 분석합니다."
)

# 데이터 주소
DATA_URL = (
    "https://raw.githubusercontent.com/"
    "greatsong/modudata/main/data/kobis_movies.csv"
)


# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 필요한 열이 있는지 확인
    required_columns = [
        "movieCd",
        "movieNm",
        "openDt",
        "genre",
        "nation",
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"자료에 필요한 열이 없습니다: {missing_columns}"
        )

    # 장르가 여러 개라면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("미분류")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
        .replace("", "미분류")
    )

    return df


# 데이터 불러오기 및 오류 처리
try:
    df = load_data()

except Exception as e:
    st.error(
        "자료를 불러오는 중 문제가 발생했습니다. "
        "깃허브 주소와 자료의 열 이름을 확인해 주세요."
    )
    st.exception(e)
    st.stop()


# 데이터 요약
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("분석 대상 영화", f"{len(df):,}편")

with col2:
    st.metric("장르 종류", f"{df['genre'].nunique():,}개")

with col3:
    st.metric("제작 국가 종류", f"{df['nation'].nunique():,}개")


# --------------------------------------------------
# 그래프 1. 장르별 영화 편수
# --------------------------------------------------
st.divider()
st.header("그래프 1. 장르별 영화 편수")
st.write(
    "분석 대상 영화가 어떤 장르에 많이 분포하는지 살펴봅니다."
)

# 장르별 영화 수 계산
genre_counts = (
    df["genre"]
    .value_counts()
    .rename_axis("장르")
    .reset_index(name="영화 편수")
)

# 플롯리 도넛 그래프
fig = px.pie(
    genre_counts,
    names="장르",
    values="영화 편수",
    hole=0.48,
    title="장르별 영화 분포",
    custom_data=["영화 편수"]
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
    legend_title_text="장르",
    margin=dict(t=70, b=30, l=20, r=20)
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# 그래프 해석 구역
with st.container(border=True):
    st.subheader("이 그래프로 알 수 있는 것")
    st.text_area(
        "분석 내용",
        placeholder=(
            "장르별 영화 편수와 비율을 비교하고, "
            "가장 많은 장르와 적은 장르의 특징을 적어 보세요."
        ),
        height=100,
        key="genre_interpretation",
        label_visibility="collapsed"
    )


# --------------------------------------------------
# 원자료 확인
# --------------------------------------------------
st.divider()
st.subheader("분석에 사용한 영화 자료")
st.caption("장르 열에는 영화마다 첫 번째 장르만 표시됩니다.")

if st.checkbox("영화 자료 표 보기"):
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
