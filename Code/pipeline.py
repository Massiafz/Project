import requests
import time
import pandas as pd

# Discogs API credentials
DISCOGS_API_URL = "https://api.discogs.com/database/search"
DISCOGS_TOKEN = "cjFlWrGyvoXUzOjeOIHnSpKiYXfsnPrrRlnAKnWE"

def clean_date(date_str):
    """Clean and standardize date strings."""
    parts = date_str.strip().split()
    if len(parts) == 1:  # Year only (e.g., "1975")
        return f"1 January {parts[0]}"
    elif len(parts) == 2:  # Month + Year (e.g., "July 1963")
        return f"1 {parts[0]} {parts[1]}"
    else:  # Full date (e.g., "16 June 1997")
        return date_str

def data_cleaning_pipeline(input_csv, output_csv):
    """Pipeline to clean and transform the CSV data."""
    # Load raw data
    df = pd.read_csv(input_csv)

    # 1. Clean 'Release Date' and convert to datetime
    df['Release Date'] = df['Release Date'].apply(clean_date)
    df['Release Date'] = pd.to_datetime(df['Release Date'], format='%d %B %Y', errors='coerce')

    # 2. Convert data types
    df['Number of Ratings'] = df['Number of Ratings'].str.replace(',', '').astype(int)
    text_columns = ['Album', 'Artist Name', 'Genres']
    df[text_columns] = df[text_columns].astype("string")
    df['Ranking'] = df['Ranking'].astype(int)
    df['Average Rating'] = df['Average Rating'].astype(float)
    df['Number of Ratings'] = df['Number of Ratings'].astype(int)

    # 3. Filter the data
    df = df[df['Ranking'] <= 1000]

    # 4. Remove unnecessary columns
    if 'Descriptors' in df.columns:
        del df['Descriptors']

    # 5. Save cleaned data to a new CSV
    df.to_csv(output_csv, index=False)
    print(f"Cleaned data saved to: {output_csv}")
    return df

def get_album_cover(album, artist):
    """Fetch album cover URL from Discogs API."""
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

def fetch_album_covers(csv_file):
    """Fetch album covers and update CSV."""
    df = pd.read_csv(csv_file)

    for index, row in df.iterrows():
        if pd.notna(row.get("Cover URL")) and row["Cover URL"].startswith("http"):
            print(f"Skipping {row['Album']} - Cover already exists.")
            continue  # Skip albums with a cover

        cover_url = get_album_cover(row["Album"], row["Artist Name"])
        df.at[index, "Cover URL"] = cover_url
        print(f"Fetched cover for {row['Album']}: {cover_url}")

        time.sleep(1)  # Rate limiting

    # Save updated CSV
    df.to_csv(csv_file, index=False)
    print(f"Updated CSV with album covers: {csv_file}")

# Main execution
if __name__ == "__main__":
    input_csv = "data.csv"
    output_csv = "cleaned_music_data.csv"

    # Step 1: Clean the data
    cleaned_df = data_cleaning_pipeline(input_csv, output_csv)

    # Step 2: Fetch album covers
    fetch_album_covers(output_csv)
