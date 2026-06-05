import pandas as pd

files = [
    "city_profile.csv",
    "city_year_profile.csv",
    "city_month_profile.csv",
    "city_season_profile.csv"
]

for f in files:
    df = pd.read_csv("data/features/" + f)
    print("\n", "="*50)
    print(f)
    print(df.columns.tolist())