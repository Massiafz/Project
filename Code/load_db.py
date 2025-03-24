import sqlite3
import pandas as pd
import pandas as pd
import sqlite3



def create_db():
    conn = sqlite3.connect("music.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS albums (
        id INTEGER PRIMARY KEY,
        ranking INTEGER,
        album TEXT,
        artist_name TEXT,
        release_date TEXT,
        genres TEXT,
        average_rating REAL,
        num_ratings INTEGER,
        num_reviews INTEGER,
        cover_url TEXT,
        track_list TEXT,
        deezer_id INTEGER
                
    )
    """)

    conn.commit()
    conn.close()
    print("Database created successfully!")

def check_table_structure():
    conn = sqlite3.connect("music.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(albums)")
    columns = cursor.fetchall()
    print("Table structure:", columns)
    conn.close()

# If needed, drop and recreate the table
def reset_table():
    conn = sqlite3.connect("music.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS albums")
    conn.commit()
    conn.close()

# Then modify your load_data function to create a new table
def load_data(csv_file):
    conn = sqlite3.connect("music.db")
    df = pd.read_csv(csv_file)
    
    # Rename columns
    df.columns = ["ranking", "album", "artist_name", "release_date", "genres", 
                  "average_rating", "num_ratings", "num_reviews", "cover_url", "tracklist", "deezer_id"]
    
    # Use replace instead of append to recreate the table
    df.to_sql("albums", conn, if_exists="replace", index=False)
    conn.close()
if __name__ == "__main__":
    create_db()
    check_table_structure()
    reset_table()
    load_data("cleaned_music_data.csv")
