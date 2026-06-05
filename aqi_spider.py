import os
import time
import requests
import pandas as pd
from tqdm import tqdm
from city_config import CITIES


RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

SAVE_PATH = os.path.join(
    RAW_DIR,
    "aqi_20cities_2023_2025.csv"
)

CHECKPOINT_PATH = os.path.join(
    RAW_DIR,
    "aqi_done_tasks.txt"
)

AQI_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

YEARS = [2023, 2024, 2025]

AQI_HOURLY_VARS = [
    "pm2_5",
    "pm10",
    "carbon_monoxide",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "ozone",
    "dust"
]


def get_year_range(year):
    return f"{year}-01-01", f"{year}-12-31"


def load_existing_data():
    if os.path.exists(SAVE_PATH):
        df = pd.read_csv(SAVE_PATH, low_memory=False)
        print(f"检测到已有AQI数据：{len(df)} 条")
        return df

    return pd.DataFrame()


def load_done_tasks():
    if not os.path.exists(CHECKPOINT_PATH):
        return set()

    with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def save_done_task(task_id):
    with open(CHECKPOINT_PATH, "a", encoding="utf-8") as f:
        f.write(task_id + "\n")


def save_data(df):
    if df.empty:
        return

    df = df.drop_duplicates(
        subset=["city", "time"]
    )

    df.to_csv(
        SAVE_PATH,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"已保存AQI数据：{SAVE_PATH}，当前数据量：{len(df)}")


def fetch_aqi(city_info, year, max_retry=3):
    start_date, end_date = get_year_range(year)

    params = {
        "latitude": city_info["lat"],
        "longitude": city_info["lon"],
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join(AQI_HOURLY_VARS),
        "timezone": "Asia/Shanghai"
    }

    for retry in range(1, max_retry + 1):
        try:
            response = requests.get(
                AQI_URL,
                params=params,
                timeout=60
            )

            if response.status_code != 200:
                print(
                    f"AQI状态码异常：{response.status_code}，"
                    f"城市={city_info['city']}，年份={year}，retry={retry}"
                )
                time.sleep(5)
                continue

            data = response.json()

            if "hourly" not in data:
                print(f"无AQI hourly数据：{city_info['city']}，年份={year}")
                return pd.DataFrame()

            df_hourly = pd.DataFrame(data["hourly"])

            if df_hourly.empty:
                return pd.DataFrame()

            # 防止某些字段没有返回，比如 dust
            for col in AQI_HOURLY_VARS:
                if col not in df_hourly.columns:
                    df_hourly[col] = None

            df_hourly["time"] = pd.to_datetime(df_hourly["time"])
            df_hourly["date"] = df_hourly["time"].dt.strftime("%Y-%m-%d")

            aqi_daily = (
                df_hourly
                .groupby("date")[AQI_HOURLY_VARS]
                .mean()
                .reset_index()
                .rename(columns={"date": "time"})
            )

            valid_count = (
                aqi_daily[AQI_HOURLY_VARS]
                .notna()
                .sum()
                .sum()
            )

            if valid_count == 0:
                print(
                    f"AQI全为空：{city_info['city']}，年份={year}"
                )
                return pd.DataFrame()

            aqi_daily["city"] = city_info["city"]
            aqi_daily["lat"] = city_info["lat"]
            aqi_daily["lon"] = city_info["lon"]
            aqi_daily["year"] = year

            return aqi_daily

        except Exception as e:
            print(
                f"AQI请求失败：城市={city_info['city']}，年份={year}，"
                f"retry={retry}，错误={e}"
            )
            time.sleep(5)

    return pd.DataFrame()


def main():
    existing_df = load_existing_data()
    done_tasks = load_done_tasks()

    print(f"已完成AQI任务数：{len(done_tasks)}")

    all_rows = [existing_df] if not existing_df.empty else []

    tasks = []

    for city in CITIES:
        for year in YEARS:
            task_id = f"{city['city']}_{year}"
            tasks.append((task_id, city, year))

    for task_id, city, year in tqdm(
        tasks,
        desc="AQI断点爬取"
    ):

        if task_id in done_tasks:
            print(f"跳过已完成AQI任务：{task_id}")
            continue

        print(f"\n开始AQI任务：{task_id}")

        df_task = fetch_aqi(city, year)

        if df_task.empty:
            print(f"{task_id} AQI获取失败或为空，保存已有数据后停止")
            if all_rows:
                temp_df = pd.concat(all_rows, ignore_index=True)
                save_data(temp_df)
            return

        all_rows.append(df_task)

        temp_df = pd.concat(all_rows, ignore_index=True)

        save_data(temp_df)

        save_done_task(task_id)

        print(f"{task_id} AQI完成：{len(df_task)} 条")

        time.sleep(1)

    final_df = pd.concat(all_rows, ignore_index=True)

    save_data(final_df)

    print("\n全部AQI任务完成")
    print("保存路径：", SAVE_PATH)
    print("最终数据量：", len(final_df))
    print("字段：", final_df.columns.tolist())


if __name__ == "__main__":
    main()