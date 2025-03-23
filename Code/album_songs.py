import requests
import time
import pandas as pd

# Deezer API endpoint
DEEZER_API_URL = "https://api.deezer.com"

def search_deezer_album(album_name, artist_name):
    """Search for an album on Deezer."""
    search_url = f"{DEEZER_API_URL}/search/album"
    params = {
        "q": f"artist:'{artist_name}' album:'{album_name}'"
    }
    
    response = requests.get(search_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("total", 0) > 0:
            return data["data"][0].get("id")
    return None

def get_album_tracklist(album_id):
    """Get the tracklist for a specific album ID."""
    if not album_id:
        return []
    
    tracklist_url = f"{DEEZER_API_URL}/album/{album_id}/tracks"
    response = requests.get(tracklist_url)
    
    if response.status_code == 200:
        data = response.json()
        tracks = []
        for track in data.get("data", []):
            tracks.append({
                "title": track.get("title"),
                "duration": track.get("duration"),
                "track_position": track.get("track_position")
            })
        return tracks
    return []

def fetch_album_tracklists(csv_file):
    """Fetch album tracklists from Deezer API and update CSV."""
    # Load the CSV file
    df = pd.read_csv(csv_file)
    
    # Add column for tracklist if it doesn't exist
    if "Tracklist" not in df.columns:
        df["Tracklist"] = None
    
    # Add column for Deezer ID if it doesn't exist
    if "Deezer_ID" not in df.columns:
        df["Deezer_ID"] = None
    
    for index, row in df.iterrows():
        # Skip if tracklist already exists
        if pd.notna(row.get("Tracklist")) and row["Tracklist"]:
            print(f"Skipping {row['Album']} - Tracklist already exists.")
            continue
        
        print(f"Processing {row['Album']} by {row['Artist Name']}...")
        
        # Step 1: Get album ID
        album_id = search_deezer_album(row["Album"], row["Artist Name"])
        df.at[index, "Deezer_ID"] = album_id
        
        if album_id:
            # Step 2: Get tracklist
            tracklist = get_album_tracklist(album_id)
            if tracklist:
                # Convert tracklist to a string representation
                tracklist_str = "; ".join([f"{t['track_position']}. {t['title']} ({t['duration']}s)" for t in tracklist])
                df.at[index, "Tracklist"] = tracklist_str
                print(f"Fetched tracklist for {row['Album']} - {len(tracklist)} tracks")
            else:
                print(f"No tracklist found for {row['Album']}")
        else:
            print(f"Album not found on Deezer: {row['Album']}")
        
        # Save after each album to prevent data loss in case of errors
        df.to_csv(csv_file, index=False)
        
        # Rate limiting to avoid API throttling
        time.sleep(1)
    
    print(f"Finished updating CSV with album tracklists: {csv_file}")

# Main execution
if __name__ == "__main__":
    csv_file = "cleaned_music_data.csv"  # Change this to your actual CSV file name
    fetch_album_tracklists(csv_file)