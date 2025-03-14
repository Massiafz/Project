import sqlite3

def create_db():
    conn = sqlite3.connect("music.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS albums (
        id INTEGER PRIMARY KEY,
        ranking INTEGER,
        album TEXT,
        artist TEXT,
        release_date TEXT,
        genres TEXT,
        average_rating REAL,
        num_ratings INTEGER,
        num_reviews INTEGER,
        cover_url TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("Database created successfully!")

if __name__ == "__main__":
    create_db()
