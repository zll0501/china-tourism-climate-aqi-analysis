# -*- coding: utf-8 -*-
"""
DS00 数据探索与质量分析（最终精简版）
------------------------------------------------
目标：
    用 3 张图完成数据探索阶段：
    DS00_1 气候相关性热力图
    DS00_2 AQI相关性热力图
    DS00_3 关键指标分布箱线图

输入：
    data/features/city_profile.csv

输出：
    data/figures/DS00_1_climate_correlation_heatmap.png
    data/figures/DS00_2_aqi_correlation_heatmap.png
    data/figures/DS00_3_key_indicator_boxplot.png

说明：
    AQI相关指标仅基于 2023-2025 年空气质量数据。
"""

import os
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# =========================
# 0. 全局配置
# =========================

warnings.filterwarnings("ignore")

FEATURE_DIR = Path("data/features")
FIGURE_DIR = Path("data/figures")
RESULT_DIR = Path("data/results")

CITY_PROFILE_PATH = FEATURE_DIR / "city_profile.csv"

FIGURE_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.sans-serif"] = [
    "SimHei",
    "Microsoft YaHei",
    "Arial Unicode MS",
    "DejaVu Sans"
]
plt.rcParams["axes.unicode_minus"] = False

sns.set_theme(style="whitegrid", font="SimHei")


# =========================
# 1. 工具函数
# =========================

def save_fig(filename):
    path = FIGURE_DIR / filename
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"已保存：{path}")


def load_data():
    print("读取DS00所需数据...")

    if not CITY_PROFILE_PATH.exists():
        raise FileNotFoundError(f"未找到文件：{CITY_PROFILE_PATH}")

    df = pd.read_csv(CITY_PROFILE_PATH, encoding="utf-8-sig")
    print("city_profile:", df.shape)
    print("字段：", list(df.columns))

    return df


def existing_cols(df, cols):
    return [c for c in cols if c in df.columns]


# =========================
# 2. DS00_1 气候相关性热力图
# =========================

def plot_ds00_1_climate_correlation(df):
    print("\nDS00_1 气候相关性热力图...")

    climate_cols = existing_cols(
        df,
        [
            "avg_temp",
            "avg_temp_max",
            "avg_temp_min",
            "avg_temp_range",
            "avg_apparent_temp",
            "avg_apparent_gap",
            "avg_humidity",
            "total_precipitation",
            "avg_precipitation",
            "rainy_days",
            "heavy_rain_days",
            "avg_wind",
            "avg_wind_gust",
            "avg_sunshine_hour",
            "avg_shortwave",
            "hot_days",
            "extreme_hot_days",
            "cold_days",
            "freezing_days",
            "climate_comfort_index",
        ],
    )

    if len(climate_cols) < 3:
        raise ValueError("气候相关性字段不足，请检查 city_profile.csv")

    corr = df[climate_cols].corr()

    plt.figure(figsize=(14, 11))

    sns.heatmap(
        corr,
        cmap="RdBu_r",
        center=0,
        annot=True,
        fmt=".2f",
        linewidths=0.4,
        cbar_kws={"label": "相关系数"}
    )

    plt.title(
        "气候指标相关性热力图（2016-2025）",
        fontsize=20,
        fontweight="bold",
        pad=18
    )

    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(rotation=0, fontsize=10)

    save_fig("DS00_1_climate_correlation_heatmap.png")

    corr.to_csv(
        RESULT_DIR / "DS00_1_climate_correlation.csv",
        encoding="utf-8-sig"
    )


# =========================
# 3. DS00_2 AQI相关性热力图
# =========================

def plot_ds00_2_aqi_correlation(df):
    print("\nDS00_2 AQI相关性热力图...")

    aqi_cols = existing_cols(
        df,
        [
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
            "air_quality_score",
            "pollution_index",
        ],
    )

    if len(aqi_cols) < 3:
        raise ValueError("AQI相关字段不足，请确认是否已重新爬取并运行 feature_engineering.py")

    corr = df[aqi_cols].corr()

    plt.figure(figsize=(12, 10))

    sns.heatmap(
        corr,
        cmap="RdYlBu_r",
        center=0,
        annot=True,
        fmt=".2f",
        linewidths=0.4,
        cbar_kws={"label": "相关系数"}
    )

    plt.title(
        "空气质量指标相关性热力图（AQI：2023-2025）",
        fontsize=20,
        fontweight="bold",
        pad=18
    )

    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(rotation=0, fontsize=10)

    save_fig("DS00_2_aqi_correlation_heatmap.png")

    corr.to_csv(
        RESULT_DIR / "DS00_2_aqi_correlation.csv",
        encoding="utf-8-sig"
    )


# =========================
# 4. DS00_3 关键指标分布箱线图
# =========================

def plot_ds00_3_key_indicator_boxplot(df):
    print("\nDS00_3 关键指标分布箱线图...")

    key_cols = existing_cols(
        df,
        [
            "avg_temp",
            "avg_humidity",
            "total_precipitation",
            "avg_sunshine_hour",
            "avg_pm25",
            "avg_pm10",
            "air_quality_score",
            "climate_comfort_index",
            "summer_escape_index",
            "winter_retirement_index",
        ],
    )

    if len(key_cols) < 4:
        raise ValueError("关键指标字段不足，请检查 city_profile.csv")

    plot_df = df[["city"] + key_cols].copy()

    # 不同指标量纲差异较大，因此先做0-1归一化，再画箱线图；
    # 该图展示的是20个城市之间的相对分布，而非原始单位。
    norm_df = plot_df.copy()
    for col in key_cols:
        min_v = norm_df[col].min()
        max_v = norm_df[col].max()
        if max_v == min_v:
            norm_df[col] = 0.5
        else:
            norm_df[col] = (norm_df[col] - min_v) / (max_v - min_v)

    rename_map = {
        "avg_temp": "平均气温",
        "avg_humidity": "湿度",
        "total_precipitation": "降水",
        "avg_sunshine_hour": "日照",
        "avg_pm25": "PM2.5",
        "avg_pm10": "PM10",
        "air_quality_score": "空气质量",
        "climate_comfort_index": "气候舒适",
        "summer_escape_index": "避暑指数",
        "winter_retirement_index": "养老指数",
    }

    long_df = norm_df[key_cols].rename(columns=rename_map).melt(
        var_name="指标",
        value_name="归一化数值"
    )

    plt.figure(figsize=(14, 7))

    ax = sns.boxplot(
        data=long_df,
        x="指标",
        y="归一化数值",
        palette="Set3",
        linewidth=1.3
    )

    sns.stripplot(
        data=long_df,
        x="指标",
        y="归一化数值",
        color="black",
        alpha=0.45,
        size=4,
        jitter=0.18
    )

    ax.set_title(
        "关键气候与空气质量指标分布箱线图",
        fontsize=20,
        fontweight="bold",
        pad=18
    )

    ax.set_xlabel("指标", fontsize=13)
    ax.set_ylabel("归一化数值（0-1）", fontsize=13)
    plt.xticks(rotation=30, ha="right")

    ax.text(
        0.01,
        -0.3,
        "说明：箱线图用于比较20个城市在不同指标上的离散程度；空气质量相关指标仅基于2023-2025年AQI数据。",
        transform=ax.transAxes,
        fontsize=11,
        color="#555555"
    )

    save_fig("DS00_3_key_indicator_boxplot.png")


# =========================
# 5. 主程序
# =========================

def main():
    df = load_data()

    plot_ds00_1_climate_correlation(df)
    plot_ds00_2_aqi_correlation(df)
    plot_ds00_3_key_indicator_boxplot(df)

    print("\nDS00完成")
    print("输出图表目录：", FIGURE_DIR)
    print("输出结果目录：", RESULT_DIR)


if __name__ == "__main__":
    main()
