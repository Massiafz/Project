import requests
import time
import pandas as pd

# Discogs API credentials
DISCOGS_API_URL = "https://api.discogs.com/database/search"
DISCOGS_TOKEN = "cjFlWrGyvoXUzOjeOIHnSpKiYXfsnPrrRlnAKnWE"

# Load dataset
df = pd.read_csv("cleaned_music_data.csv")  

# Function to get album cover
def get_album_cover(album, artist):
    headers = {"User-Agent": "MyMusicApp/1.0"}
    params = {
        "q": album,
        "artist": artist,
        "type": "release",
        "token": DISCOGS_TOKEN
    }

    response = requests.get(DISCOGS_API_URL, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if "results" in data and len(data["results"]) > 0:
            return data["results"][0].get("cover_image", None)
    return None

# Iterate through albums with delay
if __name__ == "__main__":
    for index, row in df.iterrows():
        if pd.notna(row.get("Cover URL")) and row["Cover URL"].startswith("http"):
            print(f"Skipping {row['Album']} - Cover already exists.")
            continue  # Skip albums with a cover

        cover_url = get_album_cover(row["Album"], row["Artist Name"])
        df.at[index, "Cover URL"] = cover_url
        
        print(f"Fetched cover for {row['Album']}: {cover_url}")

        
        time.sleep(1)  

    # Save updated CSV
    df.to_csv("cleaned_music_data.csv", index=False)
