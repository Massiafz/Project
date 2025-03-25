import sqlite3
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def create_db():
    try:
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
        logging.info("Database created successfully!")
    except sqlite3.Error as e:
        logging.error(f"Database creation error: {e}")
    finally:
        conn.close()

def check_table_structure():
    try:
        conn = sqlite3.connect("music.db")
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(albums)")
        columns = cursor.fetchall()
        
        logging.info("Table structure:")
        for column in columns:
            logging.info(f"Column: {column}")
    except sqlite3.Error as e:
        logging.error(f"Error checking table structure: {e}")
    finally:
        conn.close()

def reset_table():
    try:
        conn = sqlite3.connect("music.db")
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS albums")
        conn.commit()
        logging.info("Table reset successfully!")
    except sqlite3.Error as e:
        logging.error(f"Error resetting table: {e}")
    finally:
        conn.close()

def load_data(csv_file):
    try:
        conn = sqlite3.connect("music.db")
        
        # Read CSV with error handling
        try:
            df = pd.read_csv(csv_file)
        except FileNotFoundError:
            logging.error(f"CSV file not found: {csv_file}")
            return
        except pd.errors.EmptyDataError:
            logging.error("The CSV file is empty.")
            return
        
        # Column renaming
        df.columns = [
            "ranking", "album", "artist_name", "release_date", "genres",
            "average_rating", "num_ratings", "num_reviews", "cover_url", 
            "tracklist", "deezer_id"
        ]
        
        # Optional: Data cleaning/validation
        # Example: Convert numeric columns, handle missing values
        numeric_columns = ['ranking', 'average_rating', 'num_ratings', 'num_reviews']
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
        df.fillna('', inplace=True)  # Replace NaN with empty string
        
        # Load data to SQLite
        df.to_sql("albums", conn, if_exists="replace", index=False)
        logging.info(f"Loaded {len(df)} records from {csv_file}")
    
    except sqlite3.Error as e:
        logging.error(f"Database loading error: {e}")
    finally:
        conn.close()

def query_sample_data():
    try:
        conn = sqlite3.connect("music.db")
        df = pd.read_sql_query("SELECT * FROM albums LIMIT 5", conn)
        logging.info("\nSample Data:\n" + str(df))
    except sqlite3.Error as e:
        logging.error(f"Error querying sample data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_db()
    check_table_structure()
    reset_table()
    load_data("cleaned_music_data.csv")
    query_sample_data()