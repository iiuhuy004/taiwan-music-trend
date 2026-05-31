import requests
import os
from supabase import create_client
from datetime import date

# Supabase 設定
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://akqeufbhwqkseazfozyu.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFrcWV1ZmJod3Frc2VhemZvenl1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODAyMDk0MDEsImV4cCI6MjA5NTc4NTQwMX0.mphDsRtAj74Okw5HQqNwEOFa_9E-2wVuhPC45RI_Y4k")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 曲風對應表
genre_map = {
    "流行樂": "西洋流行",
    "舞曲": "西洋流行",
    "台灣流行樂": "華語流行",
    "華語流行樂": "華語流行",
    "華語音樂": "華語流行",
    "韓國流行樂": "韓國流行",
    "韓國嘻哈": "韓國流行",
    "日本流行樂": "日語流行",
    "原聲帶": "其他",
    "動畫": "其他",
}

def fetch_and_store():
    url = "https://itunes.apple.com/tw/rss/topsongs/limit=50/json"
    response = requests.get(url)
    data = response.json()
    songs = data["feed"]["entry"]

    today = date.today().isoformat()

    # 檢查今天是否已經抓過了
    existing = supabase.table("daily_charts").select("id").eq("fetch_date", today).execute()
    if existing.data:
        print("今天已經抓過資料了，跳過。")
        return

    rows = []
    for i, song in enumerate(songs[:50]):
        name = song["im:name"]["label"]
        artist = song["im:artist"]["label"]
        genre_original = song["category"]["attributes"]["label"]
        genre_clean = genre_map.get(genre_original, "其他")
        cover_url = song["im:image"][2]["label"]

        rows.append({
            "fetch_date": today,
            "rank": i + 1,
            "song_name": name,
            "artist": artist,
            "genre_original": genre_original,
            "genre_clean": genre_clean,
            "cover_url": cover_url,
        })

    supabase.table("daily_charts").insert(rows).execute()
    print(f"成功儲存 {len(rows)} 筆資料！日期：{today}")

fetch_and_store()