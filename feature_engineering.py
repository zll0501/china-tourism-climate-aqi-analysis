import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


CLEAN_DIR = "data/clean"
FEATURE_DIR = "data/features"
os.makedirs(FEATURE_DIR, exist_ok=True)

INPUT_PATH = os.path.join(CLEAN_DIR, "city_daily_merged.csv")

DAILY_FEATURE_PATH = os.path.join(FEATURE_DIR, "city_daily_features.csv")
CITY_MONTH_PROFILE_PATH = os.path.join(FEATURE_DIR, "city_month_profile.csv")
CITY_SEASON_PROFILE_PATH = os.path.join(FEATURE_DIR, "city_season_profile.csv")
CITY_YEAR_PROFILE_PATH = os.path.join(FEATURE_DIR, "city_year_profile.csv")
CITY_PROFILE_PATH = os.path.join(FEATURE_DIR, "city_profile.csv")

SUMMER_RANK_PATH = os.path.join(FEATURE_DIR, "summer_escape_rank.csv")
WINTER_RANK_PATH = os.path.join(FEATURE_DIR, "winter_retirement_rank.csv")
AIR_QUALITY_RANK_PATH = os.path.join(FEATURE_DIR, "air_quality_rank.csv")
TOURISM_COMFORT_RANK_PATH = os.path.join(FEATURE_DIR, "tourism_comfort_rank.csv")


def minmax_positive(s):
    s = s.astype(float)
    if s.notna().sum() == 0 or s.nunique(dropna=True) <= 1:
        return pd.Series(50, index=s.index)
    return pd.Series(
        MinMaxScaler((0, 100)).fit_transform(s.values.reshape(-1, 1)).ravel(),
        index=s.index
    )


def minmax_negative(s):
    return 100 - minmax_positive(s)


def ideal_score(s, ideal, penalty):
    return (100 - (s - ideal).abs() * penalty).clip(0, 100)


def get_season(month):
    if month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "autumn"
    else:
        return "winter"


def add_daily_features(df):
    print("构建日级增强特征...")

    df = df.copy()

    df["sunshine_hour"] = df["sunshine_duration"] / 3600

    df["temp_range"] = df["temperature_2m_max"] - df["temperature_2m_min"]
    df["apparent_gap"] = (
        df["apparent_temperature_mean"] - df["temperature_2m_mean"]
    )

    df["hot_day"] = (df["temperature_2m_max"] >= 30).astype(int)
    df["extreme_hot_day"] = (df["temperature_2m_max"] >= 35).astype(int)

    df["cold_day"] = (df["temperature_2m_min"] <= 0).astype(int)
    df["freezing_day"] = (df["temperature_2m_min"] <= -5).astype(int)

    df["rainy_day"] = (df["precipitation_sum"] > 0).astype(int)
    df["heavy_rain_day"] = (df["precipitation_sum"] >= 25).astype(int)

    df["sunny_day"] = (df["sunshine_hour"] >= 8).astype(int)
    df["low_sunshine_day"] = (df["sunshine_hour"] <= 3).astype(int)

    df["windy_day"] = (df["wind_speed_10m_max"] >= 30).astype(int)
    df["gusty_day"] = (df["wind_gusts_10m_max"] >= 50).astype(int)

    aqi_mask = df["pm2_5"].notna()

    df["good_air_day"] = np.nan
    df["polluted_day"] = np.nan
    df["dusty_day"] = np.nan
    df["ozone_high_day"] = np.nan

    df.loc[aqi_mask, "good_air_day"] = (
        df.loc[aqi_mask, "pm2_5"] <= 35
    ).astype(int)

    df.loc[aqi_mask, "polluted_day"] = (
        df.loc[aqi_mask, "pm2_5"] >= 75
    ).astype(int)

    df.loc[aqi_mask, "dusty_day"] = (
        df.loc[aqi_mask, "dust"] >= 10
    ).astype(int)

    df.loc[aqi_mask, "ozone_high_day"] = (
        df.loc[aqi_mask, "ozone"] >= 100
    ).astype(int)

    return df


def add_daily_scores(df):
    print("构建日级指数...")

    df = df.copy()

    df["temp_score"] = ideal_score(df["temperature_2m_mean"], 22, 5)
    df["apparent_temp_score"] = ideal_score(df["apparent_temperature_mean"], 22, 5)
    df["humidity_score"] = ideal_score(df["relative_humidity_2m_mean"], 55, 2)

    df["rain_score"] = minmax_negative(df["precipitation_sum"].fillna(0))
    df["wind_score"] = minmax_negative(df["wind_speed_10m_max"].fillna(0))
    df["gust_score"] = minmax_negative(df["wind_gusts_10m_max"].fillna(0))

    df["sunshine_score"] = ideal_score(df["sunshine_hour"], 6, 8)
    df["radiation_score"] = ideal_score(df["shortwave_radiation_sum"], 18, 2)

    df["temp_range_score"] = ideal_score(df["temp_range"], 8, 5)
    df["apparent_gap_score"] = minmax_negative(df["apparent_gap"].abs())

    df["climate_comfort_index"] = (
        df["temp_score"] * 0.20 +
        df["apparent_temp_score"] * 0.18 +
        df["humidity_score"] * 0.14 +
        df["rain_score"] * 0.12 +
        df["wind_score"] * 0.10 +
        df["gust_score"] * 0.06 +
        df["sunshine_score"] * 0.10 +
        df["radiation_score"] * 0.04 +
        df["temp_range_score"] * 0.04 +
        df["apparent_gap_score"] * 0.02
    )

    aqi_mask = df["pm2_5"].notna()

    for col in [
        "pm25_score",
        "pm10_score",
        "co_score",
        "no2_score",
        "so2_score",
        "ozone_score",
        "dust_score",
        "air_quality_score",
        "pollution_index",
        "tourism_comfort_index"
    ]:
        df[col] = np.nan

    df.loc[aqi_mask, "pm25_score"] = minmax_negative(df.loc[aqi_mask, "pm2_5"])
    df.loc[aqi_mask, "pm10_score"] = minmax_negative(df.loc[aqi_mask, "pm10"])
    df.loc[aqi_mask, "co_score"] = minmax_negative(df.loc[aqi_mask, "carbon_monoxide"])
    df.loc[aqi_mask, "no2_score"] = minmax_negative(df.loc[aqi_mask, "nitrogen_dioxide"])
    df.loc[aqi_mask, "so2_score"] = minmax_negative(df.loc[aqi_mask, "sulphur_dioxide"])
    df.loc[aqi_mask, "ozone_score"] = minmax_negative(df.loc[aqi_mask, "ozone"])
    df.loc[aqi_mask, "dust_score"] = minmax_negative(df.loc[aqi_mask, "dust"])

    df.loc[aqi_mask, "air_quality_score"] = (
        df.loc[aqi_mask, "pm25_score"] * 0.30 +
        df.loc[aqi_mask, "pm10_score"] * 0.20 +
        df.loc[aqi_mask, "co_score"] * 0.10 +
        df.loc[aqi_mask, "no2_score"] * 0.15 +
        df.loc[aqi_mask, "so2_score"] * 0.10 +
        df.loc[aqi_mask, "ozone_score"] * 0.10 +
        df.loc[aqi_mask, "dust_score"] * 0.05
    )

    df.loc[aqi_mask, "pollution_index"] = (
        minmax_positive(df.loc[aqi_mask, "pm2_5"]) * 0.30 +
        minmax_positive(df.loc[aqi_mask, "pm10"]) * 0.20 +
        minmax_positive(df.loc[aqi_mask, "carbon_monoxide"]) * 0.10 +
        minmax_positive(df.loc[aqi_mask, "nitrogen_dioxide"]) * 0.15 +
        minmax_positive(df.loc[aqi_mask, "sulphur_dioxide"]) * 0.10 +
        minmax_positive(df.loc[aqi_mask, "ozone"]) * 0.10 +
        minmax_positive(df.loc[aqi_mask, "dust"]) * 0.05
    )

    df.loc[aqi_mask, "tourism_comfort_index"] = (
        df.loc[aqi_mask, "climate_comfort_index"] * 0.70 +
        df.loc[aqi_mask, "air_quality_score"] * 0.30
    )

    return df


def add_seasonal_indices(df):
    print("构建避暑指数和冬季养老指数...")

    df = df.copy()

    df["summer_escape_index"] = np.nan
    df["winter_retirement_index"] = np.nan

    summer_mask = df["season"] == "summer"
    winter_mask = df["season"] == "winter"

    df.loc[summer_mask, "summer_escape_index"] = (
        minmax_negative(df.loc[summer_mask, "temperature_2m_mean"]) * 0.25 +
        minmax_negative(df.loc[summer_mask, "apparent_temperature_mean"]) * 0.25 +
        minmax_negative(df.loc[summer_mask, "relative_humidity_2m_mean"]) * 0.12 +
        minmax_negative(df.loc[summer_mask, "hot_day"]) * 0.10 +
        minmax_negative(df.loc[summer_mask, "apparent_gap"].abs()) * 0.08 +
        minmax_positive(df.loc[summer_mask, "sunshine_hour"]) * 0.08 +
        minmax_negative(df.loc[summer_mask, "precipitation_sum"]) * 0.07 +
        minmax_negative(df.loc[summer_mask, "wind_speed_10m_max"]) * 0.05
    )

    df.loc[winter_mask, "winter_retirement_index"] = (
        minmax_positive(df.loc[winter_mask, "temperature_2m_mean"]) * 0.25 +
        minmax_positive(df.loc[winter_mask, "apparent_temperature_mean"]) * 0.20 +
        minmax_negative(df.loc[winter_mask, "cold_day"]) * 0.12 +
        minmax_negative(df.loc[winter_mask, "freezing_day"]) * 0.08 +
        ideal_score(df.loc[winter_mask, "relative_humidity_2m_mean"], 55, 2) * 0.12 +
        minmax_negative(df.loc[winter_mask, "precipitation_sum"]) * 0.08 +
        minmax_negative(df.loc[winter_mask, "wind_speed_10m_max"]) * 0.07 +
        minmax_positive(df.loc[winter_mask, "sunshine_hour"]) * 0.08
    )

    winter_aqi_mask = winter_mask & df["air_quality_score"].notna()

    df.loc[winter_aqi_mask, "winter_retirement_index"] = (
        df.loc[winter_aqi_mask, "winter_retirement_index"] * 0.75 +
        df.loc[winter_aqi_mask, "air_quality_score"] * 0.25
    )

    return df


def aggregate_profile(df, group_cols):
    profile = (
        df.groupby(group_cols)
        .agg(
            lat=("lat", "first"),
            lon=("lon", "first"),
            records=("time", "count"),

            avg_temp=("temperature_2m_mean", "mean"),
            avg_temp_max=("temperature_2m_max", "mean"),
            avg_temp_min=("temperature_2m_min", "mean"),
            avg_temp_range=("temp_range", "mean"),

            avg_apparent_temp=("apparent_temperature_mean", "mean"),
            avg_apparent_gap=("apparent_gap", "mean"),

            avg_humidity=("relative_humidity_2m_mean", "mean"),

            total_precipitation=("precipitation_sum", "sum"),
            avg_precipitation=("precipitation_sum", "mean"),
            rainy_days=("rainy_day", "sum"),
            heavy_rain_days=("heavy_rain_day", "sum"),

            avg_wind=("wind_speed_10m_max", "mean"),
            avg_wind_gust=("wind_gusts_10m_max", "mean"),
            windy_days=("windy_day", "sum"),
            gusty_days=("gusty_day", "sum"),

            avg_sunshine_hour=("sunshine_hour", "mean"),
            sunny_days=("sunny_day", "sum"),
            low_sunshine_days=("low_sunshine_day", "sum"),
            avg_shortwave=("shortwave_radiation_sum", "mean"),

            hot_days=("hot_day", "sum"),
            extreme_hot_days=("extreme_hot_day", "sum"),
            cold_days=("cold_day", "sum"),
            freezing_days=("freezing_day", "sum"),

            avg_pm25=("pm2_5", "mean"),
            avg_pm10=("pm10", "mean"),
            avg_co=("carbon_monoxide", "mean"),
            avg_no2=("nitrogen_dioxide", "mean"),
            avg_so2=("sulphur_dioxide", "mean"),
            avg_ozone=("ozone", "mean"),
            avg_dust=("dust", "mean"),

            good_air_days=("good_air_day", "sum"),
            polluted_days=("polluted_day", "sum"),
            dusty_days=("dusty_day", "sum"),
            ozone_high_days=("ozone_high_day", "sum"),

            climate_comfort_index=("climate_comfort_index", "mean"),
            air_quality_score=("air_quality_score", "mean"),
            tourism_comfort_index=("tourism_comfort_index", "mean"),
            pollution_index=("pollution_index", "mean"),
            summer_escape_index=("summer_escape_index", "mean"),
            winter_retirement_index=("winter_retirement_index", "mean")
        )
        .reset_index()
    )

    return profile


def build_rank_tables(city_season_profile, city_profile):
    summer_rank = (
        city_season_profile[city_season_profile["season"] == "summer"]
        .groupby("city")
        .agg(
            lat=("lat", "first"),
            lon=("lon", "first"),

            summer_escape_index=("summer_escape_index", "mean"),
            avg_temp=("avg_temp", "mean"),
            avg_apparent_temp=("avg_apparent_temp", "mean"),
            avg_humidity=("avg_humidity", "mean"),
            hot_days=("hot_days", "sum"),
            extreme_hot_days=("extreme_hot_days", "sum"),
            rainy_days=("rainy_days", "sum"),
            avg_sunshine_hour=("avg_sunshine_hour", "mean"),
            climate_comfort_index=("climate_comfort_index", "mean")
        )
        .reset_index()
        .sort_values("summer_escape_index", ascending=False)
    )

    winter_rank = (
        city_season_profile[city_season_profile["season"] == "winter"]
        .groupby("city")
        .agg(
            lat=("lat", "first"),
            lon=("lon", "first"),

            winter_retirement_index=("winter_retirement_index", "mean"),
            avg_temp=("avg_temp", "mean"),
            avg_apparent_temp=("avg_apparent_temp", "mean"),
            avg_humidity=("avg_humidity", "mean"),
            cold_days=("cold_days", "sum"),
            freezing_days=("freezing_days", "sum"),
            rainy_days=("rainy_days", "sum"),
            avg_sunshine_hour=("avg_sunshine_hour", "mean"),
            air_quality_score=("air_quality_score", "mean")
        )
        .reset_index()
        .sort_values("winter_retirement_index", ascending=False)
    )

    air_quality_rank = (
        city_profile
        .sort_values("air_quality_score", ascending=False)
        .reset_index(drop=True)
    )

    tourism_rank = (
        city_profile
        .sort_values("tourism_comfort_index", ascending=False)
        .reset_index(drop=True)
    )

    return summer_rank, winter_rank, air_quality_rank, tourism_rank


def main():
    print("读取清洗后的主表...")

    df = pd.read_csv(INPUT_PATH, low_memory=False)

    df["time"] = pd.to_datetime(df["time"])
    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month
    df["day"] = df["time"].dt.day
    df["quarter"] = df["time"].dt.quarter
    df["season"] = df["month"].apply(get_season)

    print("主表数据量：", df.shape)

    df = add_daily_features(df)
    df = add_daily_scores(df)
    df = add_seasonal_indices(df)

    print("构建 city_month_profile：城市 × 年 × 月...")
    city_month_profile = aggregate_profile(df, ["city", "year", "month"])

    print("构建 city_season_profile：城市 × 年 × 季节...")
    city_season_profile = aggregate_profile(df, ["city", "year", "season"])

    print("构建 city_year_profile：城市 × 年...")
    city_year_profile = aggregate_profile(df, ["city", "year"])

    print("构建 city_profile：城市总体画像...")
    city_profile = aggregate_profile(df, ["city"])

    summer_rank, winter_rank, air_quality_rank, tourism_rank = build_rank_tables(
        city_season_profile,
        city_profile
    )

    df.to_csv(DAILY_FEATURE_PATH, index=False, encoding="utf-8-sig")
    city_month_profile.to_csv(CITY_MONTH_PROFILE_PATH, index=False, encoding="utf-8-sig")
    city_season_profile.to_csv(CITY_SEASON_PROFILE_PATH, index=False, encoding="utf-8-sig")
    city_year_profile.to_csv(CITY_YEAR_PROFILE_PATH, index=False, encoding="utf-8-sig")
    city_profile.to_csv(CITY_PROFILE_PATH, index=False, encoding="utf-8-sig")

    summer_rank.to_csv(SUMMER_RANK_PATH, index=False, encoding="utf-8-sig")
    winter_rank.to_csv(WINTER_RANK_PATH, index=False, encoding="utf-8-sig")
    air_quality_rank.to_csv(AIR_QUALITY_RANK_PATH, index=False, encoding="utf-8-sig")
    tourism_rank.to_csv(TOURISM_COMFORT_RANK_PATH, index=False, encoding="utf-8-sig")

    print("\n特征工程完成")
    print("生成文件：")
    print(DAILY_FEATURE_PATH)
    print(CITY_MONTH_PROFILE_PATH)
    print(CITY_SEASON_PROFILE_PATH)
    print(CITY_YEAR_PROFILE_PATH)
    print(CITY_PROFILE_PATH)
    print(SUMMER_RANK_PATH)
    print(WINTER_RANK_PATH)
    print(AIR_QUALITY_RANK_PATH)
    print(TOURISM_COMFORT_RANK_PATH)

    print("\n数据规模检查：")
    print("city_daily_features:", df.shape)
    print("city_month_profile:", city_month_profile.shape)
    print("city_season_profile:", city_season_profile.shape)
    print("city_year_profile:", city_year_profile.shape)
    print("city_profile:", city_profile.shape)

    print("\ncity_month_profile 前5行：")
    print(city_month_profile.head())

    print("\ncity_season_profile 前5行：")
    print(city_season_profile.head())


if __name__ == "__main__":
    main()