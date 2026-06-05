# -*- coding: utf-8 -*-
"""
generate_city_data_js.py

作用：
    将 data/features 下的城市画像数据转换为前端可直接读取的 JS 文件。

输入：
    data/features/city_profile.csv
    data/features/city_year_profile.csv
    data/features/city_month_profile.csv
    data/features/city_season_profile.csv

输出：
    js/city_data.js

运行：
    python generate_city_data_js.py

说明：
    生成的 city_data.js 可以被 index.html 直接引用：
        <script src="js/city_data.js"></script>
"""

from pathlib import Path
import json
import math

import pandas as pd


# =========================
# 1. 路径配置
# =========================

BASE_DIR = Path(__file__).resolve().parent
FEATURE_DIR = BASE_DIR / "data" / "features"
JS_DIR = BASE_DIR / "js"
JS_DIR.mkdir(parents=True, exist_ok=True)

PROFILE_PATH = FEATURE_DIR / "city_profile.csv"
YEAR_PATH = FEATURE_DIR / "city_year_profile.csv"
MONTH_PATH = FEATURE_DIR / "city_month_profile.csv"
SEASON_PATH = FEATURE_DIR / "city_season_profile.csv"

OUTPUT_PATH = JS_DIR / "city_data.js"


# =========================
# 2. 城市类型映射
# =========================

CITY_TYPE_MAP = {
    "昆明": "高原避暑型",
    "大理": "高原避暑型",
    "丽江": "高原避暑型",

    "三亚": "滨海暖冬度假型",
    "海口": "滨海暖冬度假型",
    "深圳": "滨海暖冬度假型",
    "广州": "滨海暖冬度假型",
    "厦门": "滨海暖冬度假型",

    "上海": "湿润宜居综合型",
    "南京": "湿润宜居综合型",
    "苏州": "湿润宜居综合型",
    "杭州": "湿润宜居综合型",
    "成都": "湿润宜居综合型",
    "重庆": "湿润宜居综合型",
    "西安": "湿润宜居综合型",
    "青岛": "湿润宜居综合型",
    "桂林": "湿润宜居综合型",

    "北京": "北方大陆四季型",
    "哈尔滨": "北方大陆四季型",
    "乌鲁木齐": "北方大陆四季型",
}


SEASON_NAME_MAP = {
    "spring": "春季",
    "summer": "夏季",
    "autumn": "秋季",
    "winter": "冬季",
    "Spring": "春季",
    "Summer": "夏季",
    "Autumn": "秋季",
    "Winter": "冬季",
    "春": "春季",
    "夏": "夏季",
    "秋": "秋季",
    "冬": "冬季",
    "春季": "春季",
    "夏季": "夏季",
    "秋季": "秋季",
    "冬季": "冬季",
}


# =========================
# 3. 字段筛选
# =========================

COMMON_KEEP_COLUMNS = [
    "city",
    "year",
    "month",
    "season",
    "lat",
    "lon",
    "records",

    # 温度
    "avg_temp",
    "avg_temp_max",
    "avg_temp_min",
    "avg_temp_range",
    "avg_apparent_temp",
    "avg_apparent_gap",

    # 湿度降水
    "avg_humidity",
    "total_precipitation",
    "avg_precipitation",
    "rainy_days",
    "heavy_rain_days",

    # 风与光照
    "avg_wind",
    "avg_wind_gust",
    "windy_days",
    "gusty_days",
    "avg_sunshine_hour",
    "sunny_days",
    "low_sunshine_days",
    "avg_shortwave",

    # 极端天气
    "hot_days",
    "extreme_hot_days",
    "cold_days",
    "freezing_days",

    # AQI
    "avg_pm25",
    "avg_pm10",
    "avg_co",
    "avg_no2",
    "avg_so2",
    "avg_ozone",
    "avg_dust",
    "good_air_days",
    "polluted_days",
    "dusty_days",
    "ozone_high_days",

    # 指数
    "climate_comfort_index",
    "air_quality_score",
    "tourism_comfort_index",
    "pollution_index",
    "summer_escape_index",
    "winter_retirement_index",
]


FIELD_LABELS = {
    "records": "记录数",

    "avg_temp": "平均气温",
    "avg_temp_max": "平均最高气温",
    "avg_temp_min": "平均最低气温",
    "avg_temp_range": "平均温差",
    "avg_apparent_temp": "体感温度",
    "avg_apparent_gap": "体感温差",

    "avg_humidity": "平均湿度",
    "total_precipitation": "总降水量",
    "avg_precipitation": "平均降水量",
    "rainy_days": "雨天数",
    "heavy_rain_days": "大雨天数",

    "avg_wind": "平均风速",
    "avg_wind_gust": "平均阵风",
    "windy_days": "大风天数",
    "gusty_days": "强阵风天数",
    "avg_sunshine_hour": "平均日照时长",
    "sunny_days": "晴朗天数",
    "low_sunshine_days": "低日照天数",
    "avg_shortwave": "平均短波辐射",

    "hot_days": "高温天数",
    "extreme_hot_days": "极端高温天数",
    "cold_days": "寒冷天数",
    "freezing_days": "冰冻天数",

    "avg_pm25": "PM2.5",
    "avg_pm10": "PM10",
    "avg_co": "CO",
    "avg_no2": "NO2",
    "avg_so2": "SO2",
    "avg_ozone": "O3",
    "avg_dust": "Dust",
    "good_air_days": "优良空气天数",
    "polluted_days": "污染天数",
    "dusty_days": "沙尘天数",
    "ozone_high_days": "臭氧偏高天数",

    "climate_comfort_index": "气候舒适度",
    "air_quality_score": "空气质量得分",
    "tourism_comfort_index": "旅游舒适度",
    "pollution_index": "污染指数",
    "summer_escape_index": "避暑指数",
    "winter_retirement_index": "冬季养老指数",
}


FIELD_UNITS = {
    "avg_temp": "℃",
    "avg_temp_max": "℃",
    "avg_temp_min": "℃",
    "avg_temp_range": "℃",
    "avg_apparent_temp": "℃",
    "avg_apparent_gap": "℃",

    "avg_humidity": "%",
    "total_precipitation": "mm",
    "avg_precipitation": "mm",
    "rainy_days": "天",
    "heavy_rain_days": "天",

    "avg_wind": "km/h",
    "avg_wind_gust": "km/h",
    "windy_days": "天",
    "gusty_days": "天",
    "avg_sunshine_hour": "h",
    "sunny_days": "天",
    "low_sunshine_days": "天",
    "avg_shortwave": "MJ/m²",

    "hot_days": "天",
    "extreme_hot_days": "天",
    "cold_days": "天",
    "freezing_days": "天",

    "avg_pm25": "μg/m³",
    "avg_pm10": "μg/m³",
    "avg_co": "μg/m³",
    "avg_no2": "μg/m³",
    "avg_so2": "μg/m³",
    "avg_ozone": "μg/m³",
    "avg_dust": "μg/m³",
    "good_air_days": "天",
    "polluted_days": "天",
    "dusty_days": "天",
    "ozone_high_days": "天",

    "climate_comfort_index": "分",
    "air_quality_score": "分",
    "tourism_comfort_index": "分",
    "pollution_index": "分",
    "summer_escape_index": "分",
    "winter_retirement_index": "分",
}


FIELD_GROUPS = {
    "temperature": [
        "avg_temp",
        "avg_temp_max",
        "avg_temp_min",
        "avg_temp_range",
        "avg_apparent_temp",
        "avg_apparent_gap",
    ],
    "precipitation": [
        "avg_humidity",
        "total_precipitation",
        "avg_precipitation",
        "rainy_days",
        "heavy_rain_days",
    ],
    "wind_sunshine": [
        "avg_wind",
        "avg_wind_gust",
        "windy_days",
        "gusty_days",
        "avg_sunshine_hour",
        "sunny_days",
        "low_sunshine_days",
        "avg_shortwave",
    ],
    "extreme": [
        "hot_days",
        "extreme_hot_days",
        "cold_days",
        "freezing_days",
    ],
    "air_quality": [
        "avg_pm25",
        "avg_pm10",
        "avg_co",
        "avg_no2",
        "avg_so2",
        "avg_ozone",
        "avg_dust",
        "good_air_days",
        "polluted_days",
        "dusty_days",
        "ozone_high_days",
    ],
    "index": [
        "climate_comfort_index",
        "air_quality_score",
        "tourism_comfort_index",
        "pollution_index",
        "summer_escape_index",
        "winter_retirement_index",
    ],
}


# =========================
# 4. 工具函数
# =========================

def read_csv_required(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"找不到文件：{path}")

    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(path)


def clean_value(value):
    """把 NaN / inf 转成 None，并减少小数位。"""
    if pd.isna(value):
        return None

    if isinstance(value, (float, np_float())):
        if math.isnan(float(value)) or math.isinf(float(value)):
            return None
        return round(float(value), 3)

    if isinstance(value, (int, np_int())):
        return int(value)

    # numpy 标量兜底
    if hasattr(value, "item"):
        try:
            item = value.item()
            if isinstance(item, float):
                if math.isnan(item) or math.isinf(item):
                    return None
                return round(item, 3)
            if isinstance(item, int):
                return int(item)
            return item
        except Exception:
            pass

    return value


def np_float():
    try:
        import numpy as np
        return (np.float16, np.float32, np.float64)
    except Exception:
        return (float,)


def np_int():
    try:
        import numpy as np
        return (np.int8, np.int16, np.int32, np.int64)
    except Exception:
        return (int,)


def prepare_df(df: pd.DataFrame, level: str) -> pd.DataFrame:
    df = df.copy()

    keep_cols = [c for c in COMMON_KEEP_COLUMNS if c in df.columns]
    df = df[keep_cols].copy()

    if "city" in df.columns:
        df["city_type"] = df["city"].map(CITY_TYPE_MAP).fillna("未知类型")

    if "season" in df.columns:
        df["season_name"] = df["season"].map(SEASON_NAME_MAP).fillna(df["season"].astype(str))

    # 排序
    sort_cols = []
    for c in ["city", "year", "month", "season"]:
        if c in df.columns:
            sort_cols.append(c)
    if sort_cols:
        df = df.sort_values(sort_cols).reset_index(drop=True)

    return df


def df_to_records(df: pd.DataFrame) -> list[dict]:
    records = []
    for _, row in df.iterrows():
        item = {}
        for col, val in row.items():
            item[col] = clean_value(val)
        records.append(item)
    return records


# =========================
# 5. 主程序
# =========================

def main():
    print("读取城市画像数据...")

    profile = prepare_df(read_csv_required(PROFILE_PATH), "profile")
    year = prepare_df(read_csv_required(YEAR_PATH), "year")
    month = prepare_df(read_csv_required(MONTH_PATH), "month")
    season = prepare_df(read_csv_required(SEASON_PATH), "season")

    data = {
        "meta": {
            "title": "中国热门旅游城市气候档案中心",
            "description": "包含总体、年度、月度和季节尺度的城市气候与空气质量画像。",
            "levels": ["profile", "year", "month", "season"],
        },
        "cityTypeMap": CITY_TYPE_MAP,
        "fieldLabels": FIELD_LABELS,
        "fieldUnits": FIELD_UNITS,
        "fieldGroups": FIELD_GROUPS,
        "profile": df_to_records(profile),
        "year": df_to_records(year),
        "month": df_to_records(month),
        "season": df_to_records(season),
    }

    js_content = (
        "/* Auto-generated by generate_city_data_js.py. Do not edit manually. */\n"
        "const CITY_DATA = "
        + json.dumps(data, ensure_ascii=False, indent=2)
        + ";\n"
    )

    OUTPUT_PATH.write_text(js_content, encoding="utf-8")

    print(f"已生成：{OUTPUT_PATH}")
    print("数据规模：")
    print(f"  profile: {len(profile)}")
    print(f"  year:    {len(year)}")
    print(f"  month:   {len(month)}")
    print(f"  season:  {len(season)}")


if __name__ == "__main__":
    main()
