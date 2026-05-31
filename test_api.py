import requests

url = "https://itunes.apple.com/tw/rss/topsongs/limit=50/json"

response = requests.get(url)
data = response.json()

songs = data["feed"]["entry"]

genres = set()
for song in songs:
    genre = song["category"]["attributes"]["label"]
    genres.add(genre)

for g in sorted(genres):
    print(g)

