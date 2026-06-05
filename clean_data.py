import os
import pandas as pd


RAW_DIR = "data/raw"
CLEAN_DIR = "data/clean"
os.makedirs(CLEAN_DIR, exist_ok=True)

WEATHER_PATH = os.path.join(RAW_DIR, "weather_20cities_2016_2025.csv")
AQI_PATH = os.path.join(RAW_DIR, "aqi_20cities_2023_2025.csv")

WEATHER_CLEAN_PATH = os.path.join(CLEAN_DIR, "weather_clean.csv")
AQI_CLEAN_PATH = os.path.join(CLEAN_DIR, "aqi_clean.csv")
MERGED_PATH = os.path.join(CLEAN_DIR, "city_daily_merged.csv")


def clean_weather():
    print("开始清洗天气数据...")

    df = pd.read_csv(WEATHER_PATH, low_memory=False)

    df["time"] = pd.to_datetime(df["time"])
    df["city"] = df["city"].astype(str)

    df = df.drop_duplicates(subset=["city", "time"])

    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month
    df["day"] = df["time"].dt.day
    df["season"] = df["month"].map(get_season)

    df = df.sort_values(["city", "time"])

    print("天气数据量：", len(df))
    print("天气城市数：", df["city"].nunique())
    print("天气时间范围：", df["time"].min(), "到", df["time"].max())
    print("天气缺失值：")
    print(df.isnull().sum())

    df.to_csv(WEATHER_CLEAN_PATH, index=False, encoding="utf-8-sig")
    print("已保存：", WEATHER_CLEAN_PATH)

    return df


def clean_aqi():
    print("\n开始清洗AQI数据...")

    df = pd.read_csv(AQI_PATH, low_memory=False)

    df["time"] = pd.to_datetime(df["time"])
    df["city"] = df["city"].astype(str)

    df = df.drop_duplicates(subset=["city", "time"])

    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month
    df["day"] = df["time"].dt.day
    df["season"] = df["month"].map(get_season)

    df = df.sort_values(["city", "time"])

    print("AQI数据量：", len(df))
    print("AQI城市数：", df["city"].nunique())
    print("AQI时间范围：", df["time"].min(), "到", df["time"].max())
    print("AQI缺失值：")
    print(df.isnull().sum())

    df.to_csv(AQI_CLEAN_PATH, index=False, encoding="utf-8-sig")
    print("已保存：", AQI_CLEAN_PATH)

    return df


def get_season(month):
    if month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "autumn"
    else:
        return "winter"


def merge_data(weather_df, aqi_df):
    print("\n开始合并天气数据和AQI数据...")

    aqi_cols = [
        "time",
        "city",
        "pm2_5",
        "pm10",
        "carbon_monoxide",
        "nitrogen_dioxide",
        "sulphur_dioxide",
        "ozone",
        "dust"
    ]

    aqi_df = aqi_df[aqi_cols]

    merged = pd.merge(
        weather_df,
        aqi_df,
        on=["city", "time"],
        how="left"
    )

    merged = merged.sort_values(["city", "time"])

    print("合并后数据量：", len(merged))
    print("合并后城市数：", merged["city"].nunique())
    print("合并后时间范围：", merged["time"].min(), "到", merged["time"].max())

    print("\n合并后缺失值：")
    print(merged.isnull().sum())

    print("\n2023-2025 AQI有效数据量：")
    print(
        merged[merged["year"] >= 2023][
            ["pm2_5", "pm10", "carbon_monoxide", "nitrogen_dioxide",
             "sulphur_dioxide", "ozone", "dust"]
        ].notna().sum()
    )

    merged.to_csv(MERGED_PATH, index=False, encoding="utf-8-sig")
    print("已保存：", MERGED_PATH)

    return merged


def check_city_counts(df, name):
    print(f"\n{name} 每个城市数据量：")
    print(df.groupby("city").size().sort_values())


def main():
    weather_df = clean_weather()
    aqi_df = clean_aqi()

    check_city_counts(weather_df, "天气数据")
    check_city_counts(aqi_df, "AQI数据")

    merged = merge_data(weather_df, aqi_df)

    print("\n清洗完成")
    print("最终主表：", MERGED_PATH)
    print("最终字段：")
    print(merged.columns.tolist())


if __name__ == "__main__":
    main()