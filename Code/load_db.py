import sqlite3
import pandas as pd
import pandas as pd
import sqlite3

def load_data(csv_file):
    conn = sqlite3.connect("music.db")
    df = pd.read_csv(csv_file)

    # Rename columns to match your SQLite table
    df.columns = ["ranking", "album", "artist_name", "release_date", "genres", 
                  "average_rating", "num_ratings", "num_reviews", "cover_url"]

    df.to_sql("albums", conn, if_exists="append", index=False)
    conn.close()

load_data("cleaned_music_data.csv")


if __name__ == "__main__":
    load_data("cleaned_music_data.csv")
