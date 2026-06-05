# -*- coding: utf-8 -*-
"""
DS02 城市年度与季节画像分析（最终修正版）
修正内容：
1. 中文字体设置放在 seaborn 主题之后，避免被覆盖
2. DS02_2 自动识别/转换 season 字段，避免空图
3. DS02_1 图例放右侧，避免遮挡
4. DS02_4 优化指标配色、趋势线和末端标注

输出图：
DS02_1_temperature_trend_2016_2025.png
DS02_2_season_comfort_distribution.png
DS02_3_air_quality_heatmap_2023_2025.png
DS02_4_extreme_weather_trend.png
"""

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager

warnings.filterwarnings("ignore")


# =========================
# 1. 路径配置
# =========================

FEATURE_DIR = Path("data/features")
FIGURE_DIR = Path("data/figures")
RESULT_DIR = Path("data/results")

FIGURE_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

CITY_YEAR_PATH = FEATURE_DIR / "city_year_profile.csv"
CITY_SEASON_PATH = FEATURE_DIR / "city_season_profile.csv"


# =========================
# 2. 城市类型配置
# =========================

TYPE_COLOR = {
    "高原避暑型": "#66C2A5",
    "滨海暖冬度假型": "#8DA0CB",
    "湿润宜居综合型": "#FC8D62",
    "北方大陆四季型": "#E78AC3",
}

CITY_TYPE_MAP = {
    "昆明": "高原避暑型",
    "大理": "高原避暑型",
    "丽江": "高原避暑型",

    "三亚": "滨海暖冬度假型",
    "海口": "滨海暖冬度假型",
    "深圳": "滨海暖冬度假型",
    "广州": "滨海暖冬度假型",
    "厦门": "滨海暖冬度假型",
    "桂林": "滨海暖冬度假型",

    "上海": "湿润宜居综合型",
    "南京": "湿润宜居综合型",
    "苏州": "湿润宜居综合型",
    "杭州": "湿润宜居综合型",
    "成都": "湿润宜居综合型",
    "重庆": "湿润宜居综合型",
    "西安": "湿润宜居综合型",
    "青岛": "湿润宜居综合型",

    "北京": "北方大陆四季型",
    "哈尔滨": "北方大陆四季型",
    "乌鲁木齐": "北方大陆四季型",
}


# =========================
# 3. 中文字体与全局风格
# =========================

def setup_chinese_font():
    """
    Windows Anaconda 常见中文字体修复。
    注意：必须在 sns.set_theme() 之后再设置，否则容易被 seaborn 覆盖。
    """
    candidate_fonts = [
        "Microsoft YaHei",
        "SimHei",
        "SimSun",
        "KaiTi",
        "Noto Sans CJK SC",
        "WenQuanYi Micro Hei",
        "Arial Unicode MS",
    ]

    installed_fonts = {f.name for f in font_manager.fontManager.ttflist}

    selected_font = None
    for font in candidate_fonts:
        if font in installed_fonts:
            selected_font = font
            break

    if selected_font is None:
        selected_font = "SimHei"
        print("警告：未检测到常见中文字体。若仍乱码，请在 Windows 安装/启用 SimHei 或 Microsoft YaHei。")
    else:
        print(f"已使用中文字体：{selected_font}")

    plt.rcParams["font.sans-serif"] = [selected_font]
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.unicode_minus"] = False

    return selected_font


def set_plot_style():
    # 先设置 seaborn，再设置中文字体，顺序不能反
    sns.set_theme(style="whitegrid")
    setup_chinese_font()

    plt.rcParams["figure.dpi"] = 120
    plt.rcParams["savefig.dpi"] = 300
    plt.rcParams["font.size"] = 13
    plt.rcParams["axes.titlesize"] = 22
    plt.rcParams["axes.labelsize"] = 16
    plt.rcParams["xtick.labelsize"] = 13
    plt.rcParams["ytick.labelsize"] = 13
    plt.rcParams["legend.fontsize"] = 12
    plt.rcParams["legend.title_fontsize"] = 13
    plt.rcParams["axes.unicode_minus"] = False


def save_fig(filename):
    out_path = FIGURE_DIR / filename
    plt.savefig(out_path, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"已保存：{out_path}")


def add_caption(fig, text):
    fig.text(
        0.5, 0.01,
        text,
        ha="center",
        va="bottom",
        fontsize=12,
        color="#333333"
    )


# =========================
# 4. 数据读取与字段处理
# =========================

def get_col(df, candidates, required=True):
    for col in candidates:
        if col in df.columns:
            return col
    if required:
        raise KeyError(f"找不到字段，候选字段：{candidates}")
    return None


def normalize_season_name(x):
    """
    兼容不同季节写法：
    spring / 春 / 春季 -> 春季
    summer / 夏 / 夏季 -> 夏季
    autumn/fall / 秋 / 秋季 -> 秋季
    winter / 冬 / 冬季 -> 冬季
    """
    if pd.isna(x):
        return np.nan

    s = str(x).strip().lower()

    mapping = {
        "spring": "春季",
        "spr": "春季",
        "春": "春季",
        "春季": "春季",

        "summer": "夏季",
        "sum": "夏季",
        "夏": "夏季",
        "夏季": "夏季",

        "autumn": "秋季",
        "fall": "秋季",
        "aut": "秋季",
        "秋": "秋季",
        "秋季": "秋季",

        "winter": "冬季",
        "win": "冬季",
        "冬": "冬季",
        "冬季": "冬季",
    }

    return mapping.get(s, x)


def load_data():
    if not CITY_YEAR_PATH.exists():
        raise FileNotFoundError(f"缺少文件：{CITY_YEAR_PATH}")
    if not CITY_SEASON_PATH.exists():
        raise FileNotFoundError(f"缺少文件：{CITY_SEASON_PATH}")

    city_year = pd.read_csv(CITY_YEAR_PATH, encoding="utf-8-sig")
    city_season = pd.read_csv(CITY_SEASON_PATH, encoding="utf-8-sig")

    city_year["year"] = city_year["year"].astype(int)
    city_season["year"] = city_season["year"].astype(int)

    city_year["city_type"] = city_year["city"].map(CITY_TYPE_MAP)
    city_season["city_type"] = city_season["city"].map(CITY_TYPE_MAP)

    if "season" in city_season.columns:
        city_season["season"] = city_season["season"].apply(normalize_season_name)
        season_order = ["春季", "夏季", "秋季", "冬季"]
        city_season["season"] = pd.Categorical(
            city_season["season"],
            categories=season_order,
            ordered=True
        )
    else:
        raise KeyError("city_season_profile.csv 中缺少 season 字段")

    print("读取DS02数据完成")
    print("city_year:", city_year.shape)
    print("city_season:", city_season.shape)
    print("season取值：", city_season["season"].dropna().unique())

    return city_year, city_season


def linear_trend(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    return slope, intercept + slope * x


# =========================
# 5. DS02_1 十年平均气温趋势
# =========================

def plot_ds02_1_temperature_trend(city_year):
    print("\n生成 DS02_1...")

    temp_col = get_col(city_year, ["avg_temp", "mean_temp", "temperature_2m_mean"])

    selected_cities = ["哈尔滨", "北京", "上海", "广州", "三亚", "昆明"]
    selected_cities = [c for c in selected_cities if c in city_year["city"].unique()]

    year_avg = (
        city_year.groupby("year", as_index=False)[temp_col]
        .mean()
        .sort_values("year")
    )

    slope, trend = linear_trend(year_avg["year"], year_avg[temp_col])

    fig, ax = plt.subplots(figsize=(14, 7.5))

    palette = sns.color_palette("Set2", n_colors=len(selected_cities))

    for city, color in zip(selected_cities, palette):
        temp_df = city_year[city_year["city"] == city].sort_values("year")
        ax.plot(
            temp_df["year"],
            temp_df[temp_col],
            marker="o",
            linewidth=2,
            markersize=6,
            alpha=0.78,
            color=color,
            label=city
        )

    ax.plot(
        year_avg["year"],
        year_avg[temp_col],
        color="#333333",
        marker="o",
        linewidth=4,
        markersize=8,
        label="20城平均"
    )

    ax.plot(
        year_avg["year"],
        trend,
        color="#666666",
        linestyle="--",
        linewidth=2.5,
        label=f"平均趋势线：{slope:.3f}℃/年"
    )

    ax.set_title("DS02_1 中国热门旅游城市十年平均气温变化趋势（2016-2025）", pad=18)
    ax.set_xlabel("年份")
    ax.set_ylabel("平均气温（℃）")
    ax.set_xticks(sorted(city_year["year"].unique()))
    ax.grid(True, linestyle="-", alpha=0.25)

    # 图例放图外
    ax.legend(
        title="城市",
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=True
    )

    first_year = int(year_avg["year"].min())
    last_year = int(year_avg["year"].max())
    first_val = year_avg.loc[year_avg["year"] == first_year, temp_col].iloc[0]
    last_val = year_avg.loc[year_avg["year"] == last_year, temp_col].iloc[0]

    ax.annotate(f"{first_val:.1f}℃", xy=(first_year, first_val),
                xytext=(first_year + 0.1, first_val + 0.35),
                fontsize=12, color="#333333")

    ax.annotate(f"{last_val:.1f}℃", xy=(last_year, last_val),
                xytext=(last_year - 0.85, last_val + 0.35),
                fontsize=12, color="#333333")

    add_caption(fig, "说明：粗黑线表示20个城市年均气温，虚线表示线性趋势；彩色折线展示典型城市差异。")

    plt.tight_layout(rect=[0, 0.05, 0.82, 1])
    save_fig("DS02_1_temperature_trend_2016_2025.png")


# =========================
# 6. DS02_2 季节舒适度分布箱线图
# =========================

def plot_ds02_2_season_comfort_box(city_season):
    print("\n生成 DS02_2...")

    comfort_col = get_col(
        city_season,
        ["climate_comfort_index", "tourism_comfort_index", "comfort_index"]
    )

    df = city_season.dropna(subset=["season", comfort_col, "city_type"]).copy()

    if df.empty:
        raise ValueError(
            "DS02_2 数据为空。请检查 city_season_profile.csv 中 season、climate_comfort_index、city 字段是否正常。"
        )

    season_order = ["春季", "夏季", "秋季", "冬季"]

    fig, ax = plt.subplots(figsize=(13.5, 7.5))

    sns.boxplot(
        data=df,
        x="season",
        y=comfort_col,
        order=season_order,
        color="#D9EAF7",
        width=0.55,
        showfliers=False,
        linewidth=1.4,
        ax=ax
    )

    sns.stripplot(
        data=df,
        x="season",
        y=comfort_col,
        order=season_order,
        hue="city_type",
        palette=TYPE_COLOR,
        size=4.2,
        alpha=0.65,
        jitter=0.24,
        ax=ax
    )

    ax.set_title("DS02_2 不同季节气候舒适度分布（2016-2025）", pad=18)
    ax.set_xlabel("季节")
    ax.set_ylabel("气候舒适度指数")
    ax.grid(True, axis="y", linestyle="-", alpha=0.25)

    handles, labels = ax.get_legend_handles_labels()
    unique = {}
    for h, l in zip(handles, labels):
        if l in TYPE_COLOR and l not in unique:
            unique[l] = h

    ax.legend(
        unique.values(),
        unique.keys(),
        title="城市类型",
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=True
    )

    add_caption(fig, "说明：箱线图展示20城在不同季节的舒适度分布，散点表示城市-年份样本。")

    plt.tight_layout(rect=[0, 0.05, 0.82, 1])
    save_fig("DS02_2_season_comfort_distribution.png")


# =========================
# 7. DS02_3 AQI年度变化热力图
# =========================

def plot_ds02_3_air_quality_heatmap(city_year):
    print("\n生成 DS02_3...")

    aq_col = get_col(city_year, ["air_quality_score"])

    df = city_year[city_year["year"].between(2023, 2025)].copy()
    if df.empty:
        raise ValueError("DS02_3 没有2023-2025年AQI数据。")

    pivot = df.pivot_table(
        index="city",
        columns="year",
        values=aq_col,
        aggfunc="mean"
    )

    pivot["三年均值"] = pivot.mean(axis=1)
    pivot = pivot.sort_values("三年均值", ascending=False)
    pivot = pivot.drop(columns=["三年均值"])

    fig, ax = plt.subplots(figsize=(10.5, 11))

    sns.heatmap(
        pivot,
        cmap="YlGnBu",
        annot=True,
        fmt=".1f",
        linewidths=0.8,
        linecolor="white",
        cbar_kws={"label": "空气质量得分"},
        ax=ax
    )

    ax.set_title("DS02_3 近三年城市空气质量得分变化热力图（2023-2025）", pad=18)
    ax.set_xlabel("年份")
    ax.set_ylabel("城市")

    add_caption(fig, "说明：空气质量相关指标仅基于2023-2025年AQI数据，颜色越深表示空气质量得分越高。")

    plt.tight_layout(rect=[0, 0.05, 1, 1])
    save_fig("DS02_3_air_quality_heatmap_2023_2025.png")


# =========================
# 8. DS02_4 极端天气变化趋势
# =========================

def plot_ds02_4_extreme_weather_trend(city_year):
    print("\n生成 DS02_4...")

    hot_col = get_col(city_year, ["hot_days"])
    extreme_hot_col = get_col(city_year, ["extreme_hot_days"])
    freeze_col = get_col(city_year, ["freezing_days", "frost_days"])

    yearly = (
        city_year.groupby("year", as_index=False)[[hot_col, extreme_hot_col, freeze_col]]
        .mean()
        .sort_values("year")
    )

    years = yearly["year"]

    hot_slope, hot_trend = linear_trend(years, yearly[hot_col])
    extreme_slope, extreme_trend = linear_trend(years, yearly[extreme_hot_col])
    freeze_slope, freeze_trend = linear_trend(years, yearly[freeze_col])

    colors = {
        "高温天数": "#E64A19",
        "极端高温天数": "#8E24AA",
        "冰冻天数": "#1E88E5",
    }

    fig, ax = plt.subplots(figsize=(13.5, 7.5))

    series_info = [
        (hot_col, "高温天数", "o", hot_slope, hot_trend),
        (extreme_hot_col, "极端高温天数", "s", extreme_slope, extreme_trend),
        (freeze_col, "冰冻天数", "^", freeze_slope, freeze_trend),
    ]

    for col, label, marker, slope, trend in series_info:
        ax.plot(
            years,
            yearly[col],
            marker=marker,
            linewidth=3,
            markersize=8,
            color=colors[label],
            label=label
        )

        ax.plot(
            years,
            trend,
            linestyle="--",
            linewidth=2,
            alpha=0.55,
            color=colors[label]
        )

        last_val = yearly[col].iloc[-1]
        ax.annotate(
            f"{last_val:.1f}",
            xy=(years.iloc[-1], last_val),
            xytext=(years.iloc[-1] + 0.12, last_val),
            fontsize=12,
            fontweight="bold",
            color=colors[label],
            va="center"
        )

    trend_text = (
        "趋势斜率\n"
        f"高温天数：{hot_slope:.2f} 天/年\n"
        f"极端高温：{extreme_slope:.2f} 天/年\n"
        f"冰冻天数：{freeze_slope:.2f} 天/年"
    )

    ax.text(
        0.73,
        0.68,
        trend_text,
        transform=ax.transAxes,
        fontsize=13,
        va="top",
        ha="left",
        bbox=dict(boxstyle="round,pad=0.45", facecolor="white", edgecolor="#CCCCCC", alpha=0.9)
    )

    ax.set_title("DS02_4 中国热门旅游城市极端天气变化趋势（2016-2025）", pad=18)
    ax.set_xlabel("年份")
    ax.set_ylabel("平均天数")
    ax.set_xticks(sorted(city_year["year"].unique()))
    ax.grid(True, linestyle="-", alpha=0.25)

    ax.legend(
        title="指标",
        loc="upper left",
        frameon=True
    )

    add_caption(fig, "说明：曲线表示20个城市年度平均极端天气天数，虚线表示线性变化趋势。")

    plt.tight_layout(rect=[0, 0.05, 1, 1])
    save_fig("DS02_4_extreme_weather_trend.png")

    yearly.to_csv(RESULT_DIR / "DS02_4_extreme_weather_yearly.csv", index=False, encoding="utf-8-sig")


# =========================
# 9. 主函数
# =========================

def main():
    set_plot_style()

    city_year, city_season = load_data()

    plot_ds02_1_temperature_trend(city_year)
    plot_ds02_2_season_comfort_box(city_season)
    plot_ds02_3_air_quality_heatmap(city_year)
    plot_ds02_4_extreme_weather_trend(city_year)

    city_year.to_csv(RESULT_DIR / "DS02_city_year_with_type.csv", index=False, encoding="utf-8-sig")
    city_season.to_csv(RESULT_DIR / "DS02_city_season_with_type.csv", index=False, encoding="utf-8-sig")

    print("\nDS02 完成")
    print("输出图表目录：", FIGURE_DIR)
    print("输出结果目录：", RESULT_DIR)


if __name__ == "__main__":
    main()
