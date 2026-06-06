import os
import time
import random
from typing import Dict, List

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from city_config import CITIES


RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

# 如果你想直接替换旧 API 文件，就保持这个文件名不变。
SAVE_PATH = os.path.join(RAW_DIR, "aqi_20cities_2023_2025.csv")

# 单独使用新的断点文件，避免和旧 API 断点混用。
CHECKPOINT_PATH = os.path.join(RAW_DIR, "aqi_traditional_done_tasks_2023_2025.txt")

BASE_URL = "https://www.tianqihoubao.com/aqi/{city_code}-{yyyymm}.html"

YEARS = [2023, 2024, 2025]
MONTHS = [f"{m:02d}" for m in range(1, 13)]

# 天气后报城市路径。若你的 city_config 里有更多城市，可在这里继续补充。
CITY_CODE_MAP: Dict[str, str] = {
    "北京": "beijing",
    "上海": "shanghai",
    "广州": "guangzhou",
    "深圳": "shenzhen",
    "成都": "chengdu",
    "重庆": "chongqing",
    "杭州": "hangzhou",
    "西安": "xian",
    "南京": "nanjing",
    "苏州": "suzhou",
    "厦门": "xiamen",
    "青岛": "qingdao",
    "三亚": "sanya",
    "海口": "haikou",
    "昆明": "kunming",
    "大理": "dali",
    "丽江": "lijiang",
    "桂林": "guilin",
    "哈尔滨": "haerbin",
    "乌鲁木齐": "wulumuqi",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
}

# 原 API 最终字段顺序
OUTPUT_COLUMNS = [
    "time",
    "pm2_5",
    "pm10",
    "carbon_monoxide",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "ozone",
    "dust",
    "city",
    "lat",
    "lon",
    "year",
]


def load_existing_data() -> pd.DataFrame:
    if os.path.exists(SAVE_PATH):
        df = pd.read_csv(SAVE_PATH, low_memory=False)
        print(f"检测到已有AQI数据：{len(df)} 条")
        return df
    return pd.DataFrame(columns=OUTPUT_COLUMNS)


def load_done_tasks() -> set:
    if not os.path.exists(CHECKPOINT_PATH):
        return set()
    with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def save_done_task(task_id: str) -> None:
    with open(CHECKPOINT_PATH, "a", encoding="utf-8") as f:
        f.write(task_id + "\n")


def save_data(df: pd.DataFrame) -> None:
    if df.empty:
        return

    for col in OUTPUT_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    df = df[OUTPUT_COLUMNS].copy()
    df = df.drop_duplicates(subset=["city", "time"])
    df = df.sort_values(["city", "time"]).reset_index(drop=True)

    df.to_csv(SAVE_PATH, index=False, encoding="utf-8-sig")
    print(f"已保存AQI数据：{SAVE_PATH}，当前数据量：{len(df)}")


def _set_response_encoding(response: requests.Response) -> None:
    """尽量避免中文质量等级乱码。"""
    if response.apparent_encoding:
        response.encoding = response.apparent_encoding
    else:
        response.encoding = "utf-8"


def parse_month_table(html: str, city_info: dict, yyyymm: str, source_url: str) -> pd.DataFrame:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")

    if table is None:
        print(f"未找到表格：{city_info['city']} {yyyymm} {source_url}")
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    rows: List[List[str]] = []
    for tr in table.find_all("tr"):
        cols = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if not cols:
            continue
        rows.append(cols)

    data_rows = []
    for cols in rows:
        # 跳过表头。真实数据第一列通常是 2023-01-01 这种日期。
        if len(cols) >= 10 and "-" in cols[0] and cols[0][:4].isdigit():
            data_rows.append(cols[:10])

    if not data_rows:
        print(f"表格无有效数据：{city_info['city']} {yyyymm}")
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    # 天气后报表格实际顺序：日期, AQI指数, 质量等级, 当天AQI排名, PM2.5, PM10, NO2, SO2, CO, O3
    df_raw = pd.DataFrame(
        data_rows,
        columns=[
            "time",
            "aqi",
            "quality_level",
            "aqi_rank",
            "pm2_5",
            "pm10",
            "nitrogen_dioxide",
            "sulphur_dioxide",
            "co_mg_m3",
            "ozone",
        ],
    )

    numeric_cols = [
        "pm2_5",
        "pm10",
        "nitrogen_dioxide",
        "sulphur_dioxide",
        "co_mg_m3",
        "ozone",
    ]
    for col in numeric_cols:
        df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce")

    # 与原 API 字段对齐：carbon_monoxide 使用 μg/m³。
    # 天气后报 CO 通常为 mg/m³，因此乘以 1000。
    df_out = pd.DataFrame()
    df_out["time"] = pd.to_datetime(df_raw["time"], errors="coerce").dt.strftime("%Y-%m-%d")
    df_out["pm2_5"] = df_raw["pm2_5"]
    df_out["pm10"] = df_raw["pm10"]
    df_out["carbon_monoxide"] = df_raw["co_mg_m3"] * 1000
    df_out["nitrogen_dioxide"] = df_raw["nitrogen_dioxide"]
    df_out["sulphur_dioxide"] = df_raw["sulphur_dioxide"]
    df_out["ozone"] = df_raw["ozone"]
    df_out["dust"] = pd.NA
    df_out["city"] = city_info["city"]
    df_out["lat"] = city_info["lat"]
    df_out["lon"] = city_info["lon"]
    df_out["year"] = pd.to_datetime(df_out["time"], errors="coerce").dt.year

    df_out = df_out.dropna(subset=["time"])
    df_out = df_out[OUTPUT_COLUMNS]

    return df_out


def fetch_month(city_info: dict, yyyymm: str, max_retry: int = 3) -> pd.DataFrame:
    city_name = city_info["city"]
    city_code = CITY_CODE_MAP.get(city_name)

    if not city_code:
        raise ValueError(f"CITY_CODE_MAP 中缺少城市拼音映射：{city_name}")

    url = BASE_URL.format(city_code=city_code, yyyymm=yyyymm)

    for retry in range(1, max_retry + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            _set_response_encoding(response)

            if response.status_code != 200:
                print(f"状态码异常：{response.status_code}，城市={city_name}，月份={yyyymm}，retry={retry}")
                time.sleep(3)
                continue

            df_month = parse_month_table(response.text, city_info, yyyymm, url)
            return df_month

        except Exception as e:
            print(f"请求失败：城市={city_name}，月份={yyyymm}，retry={retry}，错误={e}")
            time.sleep(3)

    return pd.DataFrame(columns=OUTPUT_COLUMNS)


def fetch_aqi(city_info: dict, year: int) -> pd.DataFrame:
    month_rows = []

    for month in MONTHS:
        yyyymm = f"{year}{month}"
        print(f"爬取：{city_info['city']} {yyyymm}")

        df_month = fetch_month(city_info, yyyymm)

        if not df_month.empty:
            month_rows.append(df_month)
            print(f"成功：{city_info['city']} {yyyymm}，{len(df_month)} 条")
        else:
            print(f"为空或失败：{city_info['city']} {yyyymm}")

        time.sleep(random.uniform(1.2, 2.5))

    if not month_rows:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    df_year = pd.concat(month_rows, ignore_index=True)
    df_year = df_year[df_year["year"] == year]
    df_year = df_year.drop_duplicates(subset=["city", "time"])

    valid_count = df_year[[
        "pm2_5",
        "pm10",
        "carbon_monoxide",
        "nitrogen_dioxide",
        "sulphur_dioxide",
        "ozone",
    ]].notna().sum().sum()

    if valid_count == 0:
        print(f"AQI污染物字段全为空：{city_info['city']}，年份={year}")
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    return df_year[OUTPUT_COLUMNS]


def main() -> None:
    existing_df = load_existing_data()
    done_tasks = load_done_tasks()

    print(f"已完成传统AQI任务数：{len(done_tasks)}")

    all_rows = [existing_df] if not existing_df.empty else []

    tasks = []
    for city in CITIES:
        for year in YEARS:
            task_id = f"{city['city']}_{year}"
            tasks.append((task_id, city, year))

    for task_id, city, year in tqdm(tasks, desc="传统AQI断点爬取"):
        if task_id in done_tasks:
            print(f"跳过已完成传统AQI任务：{task_id}")
            continue

        print(f"\n开始传统AQI任务：{task_id}")
        df_task = fetch_aqi(city, year)

        if df_task.empty:
            print(f"{task_id} 获取失败或为空，保存已有数据后停止")
            if all_rows:
                temp_df = pd.concat(all_rows, ignore_index=True)
                save_data(temp_df)
            return

        all_rows.append(df_task)
        temp_df = pd.concat(all_rows, ignore_index=True)
        save_data(temp_df)
        save_done_task(task_id)

        print(f"{task_id} 完成：{len(df_task)} 条")
        time.sleep(random.uniform(1.5, 3.0))

    final_df = pd.concat(all_rows, ignore_index=True)
    save_data(final_df)

    print("\n全部传统AQI任务完成")
    print("保存路径：", SAVE_PATH)
    print("最终数据量：", len(final_df))
    print("字段：", final_df.columns.tolist())


if __name__ == "__main__":
    main()
