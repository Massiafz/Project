import pandas as pd

def test_data_cleaning():
    df = pd.read_csv("cleaned_music_data.csv")
    assert not df.isnull().values.any(), "Data contains null values"