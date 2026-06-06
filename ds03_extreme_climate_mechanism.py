# -*- coding: utf-8 -*-
"""
DS03 极端气候与形成机制分析（最终版）

定位：
    不做旅游推荐，不做舒适度循环论证。
    本模块聚焦“极端气候现象”和“城市气候差异形成机制”。

输入：
    data/features/city_profile.csv

输出图表：
    data/figures/DS03_1_extreme_weather_city_heatmap.png
    data/figures/DS03_2_extreme_weather_driver_scatter.png
    data/figures/DS03_3_extreme_weather_spatial_distribution.png
    data/figures/DS03_4_climate_mechanism_framework.png

输出结果：
    data/results/DS03_city_profile_with_type.csv
    data/results/DS03_1_extreme_weather_table.csv

运行：
    python ds03_extreme_climate_mechanism.py
"""

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

warnings.filterwarnings("ignore")


# =========================
# 1. 路径配置
# =========================

FEATURE_DIR = Path("data/features")
FIGURE_DIR = Path("data/figures")
RESULT_DIR = Path("data/results")

FIGURE_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

CITY_PROFILE_PATH = FEATURE_DIR / "city_profile.csv"


# =========================
# 2. 城市类型与配色
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

TYPE_COLORS = {
    "高原避暑型": "#66C2A5",
    "滨海暖冬度假型": "#8DA0CB",
    "湿润宜居综合型": "#FC8D62",
    "北方大陆四季型": "#E78AC3",
    "未知类型": "#BDBDBD",
}


# =========================
# 3. 全局风格
# =========================

def setup_style():
    sns.set_theme(style="whitegrid")

    font_candidates = [
        "Microsoft YaHei",
        "SimHei",
        "SimSun",
        "KaiTi",
        "Noto Sans CJK SC",
        "WenQuanYi Micro Hei",
        "Arial Unicode MS",
    ]

    available_fonts = {f.name for f in mpl.font_manager.fontManager.ttflist}
    selected_font = None

    for font in font_candidates:
        if font in available_fonts:
            selected_font = font
            break

    if selected_font is None:
        selected_font = "DejaVu Sans"
        print("警告：未检测到常见中文字体，中文可能显示异常。")
    else:
        print(f"已使用中文字体：{selected_font}")

    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = [selected_font]
    plt.rcParams["axes.unicode_minus"] = False

    plt.rcParams["figure.dpi"] = 120
    plt.rcParams["savefig.dpi"] = 300
    plt.rcParams["font.size"] = 12
    plt.rcParams["axes.titlesize"] = 20
    plt.rcParams["axes.labelsize"] = 14
    plt.rcParams["xtick.labelsize"] = 11
    plt.rcParams["ytick.labelsize"] = 11
    plt.rcParams["legend.fontsize"] = 11
    plt.rcParams["legend.title_fontsize"] = 12


def save_fig(filename):
    out_path = FIGURE_DIR / filename
    plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"已保存：{out_path}")


def add_note(fig, text, y=0.02):
    fig.text(
        0.5,
        y,
        text,
        ha="center",
        va="bottom",
        fontsize=10,
        color="#555555",
        style="italic"
    )


def safe_numeric(df, exclude=("city", "city_type")):
    df = df.copy()
    for col in df.columns:
        if col not in exclude:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def minmax_series(s):
    s = pd.to_numeric(s, errors="coerce")
    vmin, vmax = s.min(), s.max()
    if pd.isna(vmin) or pd.isna(vmax) or vmax == vmin:
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - vmin) / (vmax - vmin)


def load_data():
    if not CITY_PROFILE_PATH.exists():
        raise FileNotFoundError(f"未找到文件：{CITY_PROFILE_PATH}")

    df = pd.read_csv(CITY_PROFILE_PATH, encoding="utf-8-sig")
    if "city" not in df.columns:
        raise ValueError("city_profile.csv 缺少 city 字段。")

    df["city_type"] = df["city"].map(CITY_TYPE_MAP).fillna("未知类型")
    df = safe_numeric(df)

    print("city_profile:", df.shape)
    print("字段：", list(df.columns))

    df.to_csv(RESULT_DIR / "DS03_city_profile_with_type.csv", index=False, encoding="utf-8-sig")
    return df


# =========================
# 4. DS03_1 极端天气城市对比热力图
# =========================

def plot_ds03_1_extreme_weather_heatmap(df):
    print("\nDS03_1 极端天气城市对比热力图...")

    metric_map = {
        "高温天数": "hot_days",
        "极端高温天数": "extreme_hot_days",
        "寒冷天数": "cold_days",
        "冰冻天数": "freezing_days",
    }

    metric_map = {k: v for k, v in metric_map.items() if v in df.columns}

    if len(metric_map) < 3:
        raise ValueError("DS03_1 极端天气指标不足，请检查 hot_days、extreme_hot_days、cold_days、freezing_days 字段。")

    plot_df = df[["city", "city_type"] + list(metric_map.values())].copy()
    plot_df = plot_df.rename(columns={v: k for k, v in metric_map.items()})

    # 极端天气综合强度：高温、极端高温、寒冷、冰冻标准化后求和
    norm_cols = list(metric_map.keys())
    for col in norm_cols:
        plot_df[col + "_norm"] = minmax_series(plot_df[col])

    plot_df["极端天气综合强度"] = plot_df[[c + "_norm" for c in norm_cols]].sum(axis=1)
    plot_df = plot_df.sort_values("极端天气综合强度", ascending=False)

    heat_data = plot_df.set_index("city")[norm_cols]

    fig, ax = plt.subplots(figsize=(10.8, 9.2))

    sns.heatmap(
        heat_data,
        annot=True,
        fmt=".0f",
        cmap="YlOrRd",
        linewidths=0.8,
        linecolor="white",
        cbar_kws={"label": "天数"},
        ax=ax,
    )

    ax.set_title("中国热门旅游城市极端天气城市对比热力图", pad=18, fontweight="bold")
    ax.set_xlabel("极端天气指标")
    ax.set_ylabel("城市")

    # 在右侧增加城市类型色带
    for y, city in enumerate(heat_data.index):
        city_type = plot_df.loc[plot_df["city"] == city, "city_type"].iloc[0]
        ax.add_patch(
            plt.Rectangle(
                (len(norm_cols) + 0.05, y),
                0.18,
                1,
                color=TYPE_COLORS.get(city_type, "#BDBDBD"),
                transform=ax.transData,
                clip_on=False,
            )
        )

    legend_elements = [
        Line2D([0], [0], marker="s", color="w", label=t,
               markerfacecolor=c, markersize=10)
        for t, c in TYPE_COLORS.items()
        if t != "未知类型" and t in plot_df["city_type"].unique()
    ]

    ax.legend(
        handles=legend_elements,
        title="城市类型",
        loc="upper left",
        bbox_to_anchor=(1.12, 1.00),
        frameon=True,
    )

    add_note(
        fig,
        "说明：颜色越深表示对应极端天气天数越多；城市按极端天气综合强度排序，右侧色带表示城市类型。",
        y=0.02,
    )

    plot_df.to_csv(RESULT_DIR / "DS03_1_extreme_weather_table.csv", index=False, encoding="utf-8-sig")

    plt.subplots_adjust(bottom=0.15)
    save_fig("DS03_1_extreme_weather_city_heatmap.png")


# =========================
# 5. DS03_2 极端天气驱动关系散点矩阵
# =========================

def scatter_reg_panel(ax, df, x_col, y_col, x_label, y_label, title):
    plot_df = df[["city", "city_type", x_col, y_col]].dropna().copy()

    sns.regplot(
        data=plot_df,
        x=x_col,
        y=y_col,
        scatter=False,
        color="#444444",
        line_kws={"linestyle": "--", "linewidth": 2},
        ax=ax,
    )

    for city_type, sub in plot_df.groupby("city_type"):
        ax.scatter(
            sub[x_col],
            sub[y_col],
            s=90,
            color=TYPE_COLORS.get(city_type, "#BDBDBD"),
            edgecolor="black",
            linewidth=0.8,
            alpha=0.85,
            label=city_type,
        )

    r = plot_df[x_col].corr(plot_df[y_col]) if len(plot_df) >= 3 else np.nan

    ax.text(
        0.04,
        0.92,
        f"r={r:.2f}" if pd.notna(r) else "r=NA",
        transform=ax.transAxes,
        fontsize=11,
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#BBBBBB", alpha=0.9),
    )

    # 标注极端点
    label_cities = set()
    if len(plot_df) > 0:
        label_cities.add(plot_df.sort_values(x_col, ascending=True).iloc[0]["city"])
        label_cities.add(plot_df.sort_values(x_col, ascending=False).iloc[0]["city"])
        label_cities.add(plot_df.sort_values(y_col, ascending=True).iloc[0]["city"])
        label_cities.add(plot_df.sort_values(y_col, ascending=False).iloc[0]["city"])

    for _, row in plot_df.iterrows():
        if row["city"] in label_cities:
            ax.text(row[x_col], row[y_col], row["city"], fontsize=9, ha="left", va="bottom")

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.grid(alpha=0.25)


def plot_ds03_2_extreme_driver_scatter(df):
    print("\nDS03_2 极端天气驱动关系散点矩阵...")

    panels = []

    if "avg_temp" in df.columns and "hot_days" in df.columns:
        panels.append(("avg_temp", "hot_days", "平均气温（℃）", "高温天数", "A 平均气温与高温天数"))

    if "avg_sunshine_hour" in df.columns and "hot_days" in df.columns:
        panels.append(("avg_sunshine_hour", "hot_days", "日照时长", "高温天数", "B 日照时长与高温天数"))

    if "avg_temp" in df.columns and "freezing_days" in df.columns:
        panels.append(("avg_temp", "freezing_days", "平均气温（℃）", "冰冻天数", "C 平均气温与冰冻天数"))

    if "avg_humidity" in df.columns and "hot_days" in df.columns:
        panels.append(("avg_humidity", "hot_days", "平均湿度", "高温天数", "D 湿度与高温天数"))

    if len(panels) < 3:
        raise ValueError("DS03_2 可用字段不足，请检查 avg_temp、avg_sunshine_hour、avg_humidity、hot_days、freezing_days。")

    panels = panels[:4]

    fig, axes = plt.subplots(2, 2, figsize=(13.5, 9.5))
    axes = axes.flatten()

    for ax, panel in zip(axes, panels):
        scatter_reg_panel(ax, df, *panel)

    for ax in axes[len(panels):]:
        ax.axis("off")

    handles, labels = axes[0].get_legend_handles_labels()
    unique = {}
    for h, l in zip(handles, labels):
        if l not in unique:
            unique[l] = h

    fig.legend(
        unique.values(),
        unique.keys(),
        title="城市类型",
        loc="upper center",
        bbox_to_anchor=(0.5, 0.91),
        ncol=4,
        frameon=True,
    )

    fig.suptitle(
        "中国热门旅游城市极端天气驱动关系分析",
        fontsize=20,
        fontweight="bold",
        y=0.96
    )

    add_note(
        fig,
        "说明：每个点代表一个城市，虚线为线性趋势；该图用于识别高温和冰冻天气的主要气候关联因素。",
        y=0.02,
    )

    plt.subplots_adjust(
        top=0.82,
        bottom=0.18,
        hspace=0.42,
        wspace=0.22
    )
    save_fig("DS03_2_extreme_weather_driver_scatter.png")


# =========================
# 6. DS03_3 极端天气空间分布双图
# =========================

def plot_ds03_3_spatial_distribution(df):
    print("\nDS03_3 极端天气空间分布双图...")

    required = ["city", "lat", "lon", "hot_days", "freezing_days"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"DS03_3 缺少必要字段：{col}")

    plot_df = df[required + ["city_type"]].dropna().copy()

    fig, axes = plt.subplots(1, 2, figsize=(15, 6.8))

    configs = [
        ("hot_days", "高温天数", "中国热门旅游城市高温天数空间分布", "YlOrRd"),
        ("freezing_days", "冰冻天数", "中国热门旅游城市冰冻天数空间分布", "Blues"),
    ]

    for ax, (metric, cbar_label, title, cmap) in zip(axes, configs):
        size = 80 + minmax_series(plot_df[metric]) * 700

        sc = ax.scatter(
            plot_df["lon"],
            plot_df["lat"],
            s=size,
            c=plot_df[metric],
            cmap=cmap,
            edgecolor="black",
            linewidth=0.8,
            alpha=0.85,
        )

        for _, row in plot_df.iterrows():
            ax.text(row["lon"] + 0.25, row["lat"] + 0.15, row["city"], fontsize=9)

        ax.set_title(title, fontsize=15, fontweight="bold")
        ax.set_xlabel("经度")
        ax.set_ylabel("纬度")
        ax.grid(alpha=0.25)

        ax.set_xlim(plot_df["lon"].min() - 3, plot_df["lon"].max() + 4)
        ax.set_ylim(plot_df["lat"].min() - 2, plot_df["lat"].max() + 2)

        cbar = plt.colorbar(sc, ax=ax, shrink=0.82)
        cbar.set_label(cbar_label)

    fig.suptitle("中国热门旅游城市极端天气空间分布图", fontsize=20, fontweight="bold", y=1.02)

    add_note(
        fig,
        "说明：气泡越大、颜色越深表示对应极端天气天数越多；左图突出南方与内陆高温差异，右图突出北方冰冻天气集聚。",
        y=0.02,
    )

    plt.subplots_adjust(bottom=0.25)
    save_fig("DS03_3_extreme_weather_spatial_distribution.png")


# =========================
# 7. DS03_4 气候形成机制流程图
# =========================

def draw_box(ax, xy, width, height, text, fc, ec="#333333", fontsize=12, bold=False):
    x, y = xy
    box = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=0.025",
        linewidth=1.2,
        edgecolor=ec,
        facecolor=fc,
        alpha=0.96,
    )
    ax.add_patch(box)

    ax.text(
        x + width / 2,
        y + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight="bold" if bold else "normal",
        color="#222222",
        linespacing=1.4,
    )


def draw_arrow(ax, start, end, color="#555555"):
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="->",
        mutation_scale=16,
        linewidth=1.6,
        color=color,
        alpha=0.85,
    )
    ax.add_patch(arrow)


def plot_ds03_4_mechanism_framework(df):
    print("\nDS03_4 气候形成机制流程图...")

    fig, ax = plt.subplots(figsize=(14, 8.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.5,
        0.95,
        "中国热门旅游城市气候差异形成机制框架图",
        ha="center",
        va="center",
        fontsize=22,
        fontweight="bold",
    )

    ax.text(
        0.5,
        0.90,
        "自然地理条件通过影响气候因子与极端天气，进一步塑造不同城市气候类型",
        ha="center",
        va="center",
        fontsize=13,
        color="#444444",
    )

    # 列标题
    ax.text(0.16, 0.82, "自然地理条件", ha="center", fontsize=14, fontweight="bold", color="#555555")
    ax.text(0.42, 0.82, "气候因子", ha="center", fontsize=14, fontweight="bold", color="#555555")
    ax.text(0.66, 0.82, "极端气候表现", ha="center", fontsize=14, fontweight="bold", color="#555555")
    ax.text(0.86, 0.82, "城市气候类型", ha="center", fontsize=14, fontweight="bold", color="#555555")

    # 第一行：高原
    draw_box(ax, (0.05, 0.66), 0.22, 0.09, "高原地形\n海拔影响", "#E8F5E9", "#66C2A5", 12, True)
    draw_box(ax, (0.32, 0.66), 0.20, 0.09, "低温\n高日照", "#E8F5E9", "#66C2A5", 12)
    draw_box(ax, (0.57, 0.66), 0.18, 0.09, "高温少\n冰冻少", "#E8F5E9", "#66C2A5", 12)
    draw_box(ax, (0.80, 0.66), 0.16, 0.09, "高原避暑型", "#CDEFE3", "#66C2A5", 13, True)

    # 第二行：滨海
    draw_box(ax, (0.05, 0.50), 0.22, 0.09, "低纬度\n海洋调节", "#EEF2FA", "#8DA0CB", 12, True)
    draw_box(ax, (0.32, 0.50), 0.20, 0.09, "高温\n高湿", "#EEF2FA", "#8DA0CB", 12)
    draw_box(ax, (0.57, 0.50), 0.18, 0.09, "冬季暖\n冰冻少", "#EEF2FA", "#8DA0CB", 12)
    draw_box(ax, (0.80, 0.50), 0.16, 0.09, "滨海暖冬\n度假型", "#DCE5F6", "#8DA0CB", 13, True)

    # 第三行：湿润综合
    draw_box(ax, (0.05, 0.34), 0.22, 0.09, "季风影响\n区域过渡", "#FFF2E8", "#FC8D62", 12, True)
    draw_box(ax, (0.32, 0.34), 0.20, 0.09, "温度适中\n湿润降水", "#FFF2E8", "#FC8D62", 12)
    draw_box(ax, (0.57, 0.34), 0.18, 0.09, "极端程度\n相对均衡", "#FFF2E8", "#FC8D62", 12)
    draw_box(ax, (0.80, 0.34), 0.16, 0.09, "湿润宜居\n综合型", "#FFE1D2", "#FC8D62", 13, True)

    # 第四行：北方大陆
    draw_box(ax, (0.05, 0.18), 0.22, 0.09, "高纬度\n大陆性影响", "#FCE8F4", "#E78AC3", 12, True)
    draw_box(ax, (0.32, 0.18), 0.20, 0.09, "低温\n季节差异", "#FCE8F4", "#E78AC3", 12)
    draw_box(ax, (0.57, 0.18), 0.18, 0.09, "寒冷多\n冰冻多", "#FCE8F4", "#E78AC3", 12)
    draw_box(ax, (0.80, 0.18), 0.16, 0.09, "北方大陆\n四季型", "#F7D0E8", "#E78AC3", 13, True)

    # 横向箭头
    y_rows = [0.705, 0.545, 0.385, 0.225]
    for y in y_rows:
        draw_arrow(ax, (0.27, y), (0.32, y))
        draw_arrow(ax, (0.52, y), (0.57, y))
        draw_arrow(ax, (0.75, y), (0.80, y))

    # 底部总结
    draw_box(
        ax,
        (0.20, 0.055),
        0.60,
        0.07,
        "核心逻辑：空间条件差异 → 气候因子差异 → 极端天气差异 → 城市气候类型差异",
        "#F7F7F7",
        "#666666",
        13,
        True,
    )

    fig.text(
        0.5,
        0.015,
        "说明：该流程图用于总结 DS01 城市类型发现、DS02 时间变化与 DS03 极端气候分析之间的机制联系。",
        ha="center",
        fontsize=11,
        color="#333333",
    )

    save_fig("DS03_4_climate_mechanism_framework.png")


# =========================
# 8. 主函数
# =========================

def main():
    setup_style()

    print("\n读取DS03所需数据...")
    df = load_data()

    plot_ds03_1_extreme_weather_heatmap(df)
    plot_ds03_2_extreme_driver_scatter(df)
    plot_ds03_3_spatial_distribution(df)
    plot_ds03_4_mechanism_framework(df)

    print("\nDS03完成")
    print("输出图表目录：", FIGURE_DIR)
    print("输出结果目录：", RESULT_DIR)


if __name__ == "__main__":
    main()
