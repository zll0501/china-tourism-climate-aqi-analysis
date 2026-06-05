# -*- coding: utf-8 -*-
"""
DS01 城市聚类画像最终版（5图）
------------------------------------------------
输出图表：
DS01_1_city_cluster_pca.png              PCA聚类图
DS01_2_type_radar.png                    城市类型雷达图
DS01_3_city_type_geo_distribution.png    地理分布图
DS01_4_type_feature_heatmap.png          类型特征热力图
DS01_5_city_type_pie.png                 城市类型占比饼图

核心修改：
1. 不再根据 KMeans 自动命名类型，改为按城市人工指定类型，避免“名称与常识不符”。
2. DS01_2 雷达图使用 StandardScaler + clip(-2,2) + 映射到 0~1，避免 MinMaxScaler 造成贴边。
3. DS01_5 改为城市类型占比饼图，更适合 PPT 展示。
4. 只生成 DS01 规划中的 5 张图，不再额外生成排行榜图，避免图表堆叠混乱。
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


# =========================
# 1. 路径配置
# =========================
PROJECT_ROOT = Path(".")
FEATURE_DIR = PROJECT_ROOT / "data" / "features"
FIGURE_DIR = PROJECT_ROOT / "data" / "figures"
RESULT_DIR = PROJECT_ROOT / "data" / "results"

FIGURE_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# 2. 全局绘图风格
# =========================
def set_plot_style():
    """设置统一绘图风格，并解决中文显示异常问题。"""
    import matplotlib

    font_candidates = [
        "Microsoft YaHei",
        "SimHei",
        "SimSun",
        "KaiTi",
        "Arial Unicode MS",
    ]

    available_fonts = {f.name for f in matplotlib.font_manager.fontManager.ttflist}

    selected_font = None
    for font in font_candidates:
        if font in available_fonts:
            selected_font = font
            break

    if selected_font is None:
        print("警告：未检测到常见中文字体，中文可能显示异常。")
        selected_font = "DejaVu Sans"
    else:
        print(f"当前使用中文字体：{selected_font}")

    # 关键：seaborn.set_theme 也要指定 font，否则可能覆盖 Matplotlib 的中文字体设置
    sns.set_theme(style="whitegrid", font=selected_font)

    plt.rcParams["font.sans-serif"] = [selected_font]
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.unicode_minus"] = False

    plt.rcParams["figure.dpi"] = 120
    plt.rcParams["savefig.dpi"] = 300
    plt.rcParams["axes.titlesize"] = 20
    plt.rcParams["axes.labelsize"] = 15
    plt.rcParams["xtick.labelsize"] = 12
    plt.rcParams["ytick.labelsize"] = 12
    plt.rcParams["legend.fontsize"] = 12


# 固定城市类型颜色，后续 DS02/DS03 也建议沿用
TYPE_COLORS = {
    "高原避暑型": "#66c2a5",
    "滨海暖冬度假型": "#8da0cb",
    "湿润宜居综合型": "#fc8d62",
    "北方大陆四季型": "#e78ac3",
}


# =========================
# 3. 城市类型人工指定
# =========================
CITY_TYPE_MAP = {
    # 高原气候、夏季凉爽
    "昆明": "高原避暑型",
    "大理": "高原避暑型",
    "丽江": "高原避暑型",

    # 低纬度/沿海城市，冬季温暖
    "三亚": "滨海暖冬度假型",
    "海口": "滨海暖冬度假型",
    "深圳": "滨海暖冬度假型",
    "广州": "滨海暖冬度假型",
    "厦门": "滨海暖冬度假型",

    # 东部、华南、西南部分城市，整体湿润，综合旅游适宜性较均衡
    "上海": "湿润宜居综合型",
    "南京": "湿润宜居综合型",
    "苏州": "湿润宜居综合型",
    "杭州": "湿润宜居综合型",
    "成都": "湿润宜居综合型",
    "重庆": "湿润宜居综合型",
    "西安": "湿润宜居综合型",
    "青岛": "湿润宜居综合型",
    "桂林": "湿润宜居综合型",

    # 纬度较高或大陆性气候特征明显
    "北京": "北方大陆四季型",
    "哈尔滨": "北方大陆四季型",
    "乌鲁木齐": "北方大陆四季型",
}


# =========================
# 4. 数据读取与基础处理
# =========================
def load_data():
    """读取 city_profile.csv，并加入人工指定城市类型。"""
    file_path = FEATURE_DIR / "city_profile.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            f"没有找到 {file_path}，请先运行特征工程代码生成 city_profile.csv"
        )

    df = pd.read_csv(file_path)
    print("读取城市总体画像数据...")
    print("city_profile:", df.shape)

    if "city" not in df.columns:
        raise ValueError("city_profile.csv 中缺少 city 字段")

    # pandas 新版本不再推荐 errors='ignore'，这里安全转换为数值
    for col in df.columns:
        if col != "city":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    missing_cities = sorted(set(df["city"]) - set(CITY_TYPE_MAP.keys()))
    if missing_cities:
        raise ValueError(
            "以下城市没有在 CITY_TYPE_MAP 中指定类型，请补充："
            + "、".join(missing_cities)
        )

    df["city_type"] = df["city"].map(CITY_TYPE_MAP)
    df["type_color"] = df["city_type"].map(TYPE_COLORS)

    out_path = RESULT_DIR / "DS01_city_profile_with_type.csv"
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"已保存：{out_path}")

    return df


# =========================
# 5. 通用指标处理函数
# =========================
def normalize_0_100(series, higher_better=True):
    """将指标归一化到 0~100。"""
    s = pd.to_numeric(series, errors="coerce")
    min_v, max_v = s.min(), s.max()

    if pd.isna(min_v) or pd.isna(max_v) or max_v == min_v:
        return pd.Series(np.full(len(s), 50.0), index=s.index)

    score = (s - min_v) / (max_v - min_v) * 100
    if not higher_better:
        score = 100 - score

    return score


def add_analysis_scores(df):
    """增加 DS01 内部展示使用的综合指标，不修改原始特征工程文件。"""
    df = df.copy()

    if "air_quality_score" in df.columns:
        df["air_quality_display_score"] = normalize_0_100(df["air_quality_score"], True)
    elif "pollution_index" in df.columns:
        df["air_quality_display_score"] = normalize_0_100(df["pollution_index"], False)
    else:
        df["air_quality_display_score"] = 50

    if "climate_comfort_index" in df.columns:
        df["climate_comfort_display_score"] = normalize_0_100(df["climate_comfort_index"], True)
    else:
        df["climate_comfort_display_score"] = 50

    if "summer_escape_index" in df.columns:
        df["summer_escape_display_score"] = normalize_0_100(df["summer_escape_index"], True)
    else:
        df["summer_escape_display_score"] = normalize_0_100(df["avg_temp"], False)

    if "winter_retirement_index" in df.columns:
        df["winter_retirement_display_score"] = normalize_0_100(df["winter_retirement_index"], True)
    else:
        df["winter_retirement_display_score"] = normalize_0_100(df["avg_temp_min"], True)

    if "avg_sunshine_hour" in df.columns:
        df["sunshine_display_score"] = normalize_0_100(df["avg_sunshine_hour"], True)
    else:
        df["sunshine_display_score"] = 50

    penalty_cols = [
        "extreme_hot_days",
        "freezing_days",
        "heavy_rain_days",
        "dusty_days",
        "polluted_days",
    ]
    existing_penalty_cols = [c for c in penalty_cols if c in df.columns]
    if existing_penalty_cols:
        penalty_norm = pd.DataFrame({
            c: normalize_0_100(df[c], True) for c in existing_penalty_cols
        })
        df["extreme_weather_penalty"] = penalty_norm.mean(axis=1)
    else:
        df["extreme_weather_penalty"] = 0

    # 只给 DS01_5 代表城市排序使用；DS01_4 不再做综合排行榜，避免与 DS03 重复
    df["tourism_suitability_score_ds01"] = (
        0.30 * df["climate_comfort_display_score"]
        + 0.20 * df["summer_escape_display_score"]
        + 0.20 * df["winter_retirement_display_score"]
        + 0.20 * df["air_quality_display_score"]
        + 0.10 * df["sunshine_display_score"]
        - 0.10 * df["extreme_weather_penalty"]
    )
    df["tourism_suitability_score_ds01"] = normalize_0_100(
        df["tourism_suitability_score_ds01"], True
    )

    return df


# =========================
# 6. DS01_1 PCA聚类图
# =========================
def plot_ds01_1_pca(df):
    """DS01_1 PCA 城市类型分布图。"""
    feature_cols = [
        "avg_temp",
        "avg_humidity",
        "avg_sunshine_hour",
        "air_quality_score",
        "climate_comfort_index",
        "summer_escape_index",
        "winter_retirement_index",
    ]
    feature_cols = [c for c in feature_cols if c in df.columns]

    if len(feature_cols) < 2:
        raise ValueError("PCA 所需数值指标不足，请检查 city_profile.csv")

    X = df[feature_cols].fillna(df[feature_cols].median())
    X_scaled = StandardScaler().fit_transform(X)

    pca = PCA(n_components=2, random_state=42)
    pca_result = pca.fit_transform(X_scaled)

    plot_df = df.copy()
    plot_df["PC1"] = pca_result[:, 0]
    plot_df["PC2"] = pca_result[:, 1]

    fig, ax = plt.subplots(figsize=(12, 7))

    for city_type, sub in plot_df.groupby("city_type"):
        ax.scatter(
            sub["PC1"], sub["PC2"],
            s=130, color=TYPE_COLORS[city_type],
            edgecolor="black", linewidth=0.8,
            label=city_type, alpha=0.9,
        )

        for _, row in sub.iterrows():
            ax.text(row["PC1"] + 0.04, row["PC2"] + 0.04, row["city"], fontsize=11)

    ax.axhline(0, color="gray", linewidth=0.8, alpha=0.5)
    ax.axvline(0, color="gray", linewidth=0.8, alpha=0.5)
    ax.set_title("DS01_1  中国热门旅游城市聚类画像PCA图", pad=16)
    ax.set_xlabel(f"PC1（解释方差 {pca.explained_variance_ratio_[0] * 100:.1f}%）")
    ax.set_ylabel(f"PC2（解释方差 {pca.explained_variance_ratio_[1] * 100:.1f}%）")
    ax.legend(title="城市类型", loc="best", frameon=True)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out_path = FIGURE_DIR / "DS01_1_city_cluster_pca.png"
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"已保存：{out_path}")


# =========================
# 7. DS01_2 类型雷达图
# =========================
def plot_ds01_2_radar(df):
    """DS01_2 城市类型雷达图：StandardScaler + clip + 映射到 0~1。"""
    radar_items = {
        "平均气温": "avg_temp",
        "湿度": "avg_humidity",
        "日照": "avg_sunshine_hour",
        "空气质量": "air_quality_display_score",
        "气候舒适": "climate_comfort_display_score",
        "夏季避暑": "summer_escape_display_score",
        "冬季养老": "winter_retirement_display_score",
    }

    radar_items = {k: v for k, v in radar_items.items() if v in df.columns}
    labels = list(radar_items.keys())
    cols = list(radar_items.values())

    scaler = StandardScaler()
    scaler.fit(df[cols].fillna(df[cols].median()))

    type_mean_raw = df.groupby("city_type")[cols].mean()
    type_z = pd.DataFrame(
        scaler.transform(type_mean_raw),
        index=type_mean_raw.index,
        columns=cols,
    )

    type_score = ((type_z.clip(-2, 2) + 2) / 4).clip(0, 1)

    ordered_types = ["高原避暑型", "滨海暖冬度假型", "湿润宜居综合型", "北方大陆四季型"]
    ordered_types = [t for t in ordered_types if t in type_score.index]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig = plt.figure(figsize=(10.5, 8))
    ax = plt.subplot(111, polar=True)

    for city_type in ordered_types:
        values = type_score.loc[city_type, cols].tolist()
        values += values[:1]
        ax.plot(angles, values, linewidth=2.5, label=city_type, color=TYPE_COLORS[city_type])
        ax.fill(angles, values, color=TYPE_COLORS[city_type], alpha=0.12)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=13)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=10)
    ax.set_title("DS01_2  不同旅游城市类型的综合画像雷达图", pad=25)
    ax.legend(title="城市类型", loc="upper right", bbox_to_anchor=(1.35, 1.15), frameon=True)

    plt.tight_layout()
    out_path = FIGURE_DIR / "DS01_2_type_radar.png"
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"已保存：{out_path}")

    type_score_out = type_score.copy()
    type_score_out.columns = labels
    type_score_out.to_csv(RESULT_DIR / "DS01_2_type_radar_score.csv", encoding="utf-8-sig")


# =========================
# 8. DS01_3 地理分布图
# =========================
def plot_ds01_3_geo_distribution(df):
    """DS01_3 城市类型地理空间分布图。"""
    if "lon" not in df.columns or "lat" not in df.columns:
        raise ValueError("city_profile.csv 中缺少 lon/lat 字段，无法绘制地理分布图")

    fig, ax = plt.subplots(figsize=(10.5, 8))

    for city_type, sub in df.groupby("city_type"):
        ax.scatter(
            sub["lon"], sub["lat"],
            s=150, color=TYPE_COLORS[city_type],
            edgecolor="black", linewidth=0.8,
            label=city_type, alpha=0.9,
        )
        for _, row in sub.iterrows():
            ax.text(row["lon"] + 0.15, row["lat"] + 0.15, row["city"], fontsize=11)

    ax.set_title("DS01_3  中国热门旅游城市聚类空间分布图", pad=16)
    ax.set_xlabel("经度")
    ax.set_ylabel("纬度")
    ax.legend(title="城市类型", loc="best", frameon=True)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out_path = FIGURE_DIR / "DS01_3_city_type_geo_distribution.png"
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"已保存：{out_path}")


# =========================
# 9. DS01_4 类型特征热力图
# =========================
def plot_ds01_4_type_feature_heatmap(df):
    """DS01_4 城市类型特征热力图，突出类型画像，避免与 DS03 排行榜重复。"""
    heatmap_items = {
        "平均气温": "avg_temp",
        "湿度": "avg_humidity",
        "日照": "avg_sunshine_hour",
        "空气质量\n(2023-2025)": "air_quality_display_score",
        "气候舒适": "climate_comfort_display_score",
        "夏季避暑": "summer_escape_display_score",
        "冬季养老": "winter_retirement_display_score",
    }
    heatmap_items = {k: v for k, v in heatmap_items.items() if v in df.columns}

    labels = list(heatmap_items.keys())
    cols = list(heatmap_items.values())

    type_mean = df.groupby("city_type")[cols].mean()

    z = pd.DataFrame(
        StandardScaler().fit_transform(type_mean),
        index=type_mean.index,
        columns=labels,
    )

    ordered_types = ["高原避暑型", "滨海暖冬度假型", "湿润宜居综合型", "北方大陆四季型"]
    ordered_types = [t for t in ordered_types if t in z.index]
    z = z.loc[ordered_types]

    fig, ax = plt.subplots(figsize=(11, 6.5))
    sns.heatmap(
        z, cmap="RdYlBu_r", annot=True, fmt=".2f",
        linewidths=0.8, linecolor="white",
        cbar_kws={"label": "标准化得分（Z-score）"}, ax=ax,
    )

    ax.set_title("DS01_4  不同旅游城市类型特征热力图", pad=16)
    ax.set_xlabel("指标")
    ax.set_ylabel("城市类型")
    ax.tick_params(axis="x", rotation=0)
    ax.tick_params(axis="y", rotation=0)

    plt.tight_layout()
    out_path = FIGURE_DIR / "DS01_4_type_feature_heatmap.png"
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"已保存：{out_path}")

    z.to_csv(RESULT_DIR / "DS01_4_type_feature_heatmap_zscore.csv", encoding="utf-8-sig")


# =========================
# 10. DS01_5 城市类型占比饼图
# =========================
def plot_ds01_5_type_pie(df):
    """DS01_5 城市类型占比饼图，替代纯文字信息图。"""
    count_df = (
        df.groupby("city_type")["city"]
        .apply(lambda x: "、".join(x.tolist()))
        .reset_index(name="member_cities")
    )
    count_df["city_count"] = count_df["member_cities"].apply(lambda x: len(x.split("、")))
    count_df["percentage"] = count_df["city_count"] / count_df["city_count"].sum() * 100

    ordered_types = ["高原避暑型", "滨海暖冬度假型", "湿润宜居综合型", "北方大陆四季型"]
    count_df["order"] = count_df["city_type"].apply(lambda x: ordered_types.index(x))
    count_df = count_df.sort_values("order").drop(columns="order")

    labels = [
        f"{row.city_type}\n{int(row.city_count)}城 / {row.percentage:.1f}%"
        for _, row in count_df.iterrows()
    ]
    sizes = count_df["city_count"].values
    colors = [TYPE_COLORS[t] for t in count_df["city_type"]]

    fig, ax = plt.subplots(figsize=(9.5, 8))

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        startangle=90,
        counterclock=False,
        autopct="%1.1f%%",
        pctdistance=0.72,
        labeldistance=1.08,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        textprops={"fontsize": 12},
    )

    centre_circle = plt.Circle((0, 0), 0.45, fc="white")
    ax.add_artist(centre_circle)
    ax.text(0, 0.04, "20个城市", ha="center", va="center", fontsize=18, fontweight="bold")
    ax.text(0, -0.11, "4类旅游画像", ha="center", va="center", fontsize=13)

    for autotext in autotexts:
        autotext.set_fontsize(12)
        autotext.set_color("black")

    ax.set_title("DS01_5  不同旅游城市类型数量占比图", pad=20)

    note_lines = []
    for _, row in count_df.iterrows():
        note_lines.append(f"{row.city_type}：{row.member_cities}")
    note = "\n".join(note_lines)

    fig.text(0.5, 0.02, note, ha="center", va="bottom", fontsize=10.5, linespacing=1.5)

    plt.tight_layout(rect=[0, 0.12, 1, 1])
    out_path = FIGURE_DIR / "DS01_5_city_type_pie.png"
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"已保存：{out_path}")

    count_df.to_csv(RESULT_DIR / "DS01_5_city_type_count.csv", index=False, encoding="utf-8-sig")


# =========================
# 11. 主函数
# =========================
def main():
    set_plot_style()

    df = load_data()
    df = add_analysis_scores(df)

    final_csv = RESULT_DIR / "DS01_city_profile_final.csv"
    df.to_csv(final_csv, index=False, encoding="utf-8-sig")
    print(f"已保存：{final_csv}")

    print("\n开始生成 DS01 图表...")

    plot_ds01_1_pca(df)
    plot_ds01_2_radar(df)
    plot_ds01_3_geo_distribution(df)
    plot_ds01_4_type_feature_heatmap(df)
    plot_ds01_5_type_pie(df)

    print("\nDS01 完成：共生成 5 张图")
    print("图表目录：", FIGURE_DIR)
    print("结果目录：", RESULT_DIR)


if __name__ == "__main__":
    main()
