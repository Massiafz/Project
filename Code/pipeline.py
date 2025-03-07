import pandas as pd

import pandas as pd

def clean_date(date_str):
    """Clean and standardize date strings."""
    parts = date_str.strip().split()
    if len(parts) == 1:  # Year only (e.g., "1975")
        return f"1 January {parts[0]}"
    elif len(parts) == 2:  # Month + Year (e.g., "July 1963")
        return f"1 {parts[0]} {parts[1]}"
    else:  # Full date (e.g., "16 June 1997")
        return date_str

def data_cleaning_pipeline(input_csv, output_csv, handle_missing='fill'):
    """Pipeline to clean and transform the CSV data."""
    # Load raw data
    df = pd.read_csv(input_csv)
  # Remove the 'Descriptors' column
    
    # 1. Clean 'Release Date' and convert to datetime
    df['Release Date'] = df['Release Date'].apply(clean_date)
    df['Release Date'] = pd.to_datetime(
        df['Release Date'],
        format='%d %B %Y',
        errors='coerce'  # Convert invalid entries to NaT
    )

    # 3. Convert data types
    df['Number of Ratings'] = (
        df['Number of Ratings']
        .str.replace(',', '')
        .astype(int)
    )
    text_columns = ['Album', 'Artist Name', 'Genres', 'Descriptors']
    df[text_columns] = df[text_columns].astype("string")
    df['Ranking'] = df['Ranking'].astype(int)
    del df['Descriptors']
    
    # 4. Save cleaned data to a new CSV
    df.to_csv(output_csv, index=False)
    print(f"Cleaned data saved to: {output_csv}")
    print(df.head())

# Example usage
input_csv = "/Users/Bach/Documents/OTU WINTER 2025/Software Design/project/Project/Code/data.csv"
output_csv = "cleaned_music_data.csv"
data_cleaning_pipeline(input_csv, output_csv)
