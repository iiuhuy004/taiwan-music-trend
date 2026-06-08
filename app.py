import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# Supabase 設定
SUPABASE_URL = "https://akqeufbhwqkseazfozyu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFrcWV1ZmJod3Frc2VhemZvenl1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODAyMDk0MDEsImV4cCI6MjA5NTc4NTQwMX0.mphDsRtAj74Okw5HQqNwEOFa_9E-2wVuhPC45RI_Y4k"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@st.cache_data(ttl=300)
def load_data():
    result = supabase.table("daily_charts").select("*").execute()
    df = pd.DataFrame(result.data)
    df["fetch_date"] = pd.to_datetime(df["fetch_date"])
    return df

df = load_data()
today_df = df[df["fetch_date"] == df["fetch_date"].max()]

# 頁面標題
st.title("🎵 台灣音樂趨勢儀表板")
st.caption(f"資料日期：{df['fetch_date'].max().strftime('%Y-%m-%d')}")

# ── 1. Top 5 歌曲卡片 ──
st.header("🎴 今日 Top 5")

top5 = today_df.sort_values("rank").head(5)
cols = st.columns(5)

for idx, (_, row) in enumerate(top5.iterrows()):
    with cols[idx]:
        st.image(row["cover_url"], use_container_width=True)
        st.markdown(f"**#{row['rank']}**")
        st.markdown(f"**{row['song_name']}**")
        st.markdown(f"{row['artist']}")
        st.markdown(f"`{row['genre_clean']}`")

# ── 2. Top 30 排行榜 ──
st.header("🏆 Top 30 排行榜")

genres = ["全部"] + sorted(today_df["genre_clean"].unique().tolist())
selected_genre = st.selectbox("依曲風篩選", genres)

if selected_genre == "全部":
    chart_df = today_df.sort_values("rank").head(30)
else:
    chart_df = today_df[today_df["genre_clean"] == selected_genre].sort_values("rank").head(30)

st.dataframe(
    chart_df[["rank", "song_name", "artist", "genre_clean"]].rename(columns={
        "rank": "排名",
        "song_name": "歌曲",
        "artist": "歌手",
        "genre_clean": "曲風",
    }).reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
)

# ── 3. 曲風佔比 ──
st.header("🥧 曲風佔比")

genre_count = today_df["genre_clean"].value_counts().reset_index()
genre_count.columns = ["曲風", "歌曲數"]

fig_pie = px.pie(
    genre_count,
    names="曲風",
    values="歌曲數",
    color_discrete_sequence=px.colors.qualitative.Pastel,
)
st.plotly_chart(fig_pie, use_container_width=True)

# ── 4. 曲風週趨勢 ──
st.header("📈 曲風趨勢")

trend_df = (
    df.groupby(["fetch_date", "genre_clean"])
    .size()
    .reset_index(name="歌曲數")
)

fig_trend = px.bar(
    trend_df,
    x="fetch_date",
    y="歌曲數",
    color="genre_clean",
    barmode="stack",
    labels={"fetch_date": "日期", "genre_clean": "曲風"},
    color_discrete_sequence=px.colors.qualitative.Pastel,
)
st.plotly_chart(fig_trend, use_container_width=True)