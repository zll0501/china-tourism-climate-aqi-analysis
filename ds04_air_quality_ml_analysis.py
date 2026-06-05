# -*- coding: utf-8 -*-
"""
DS04 气象因素对空气污染物的预测与驱动机制分析

输入：
    data/raw/weather_20cities_2016_2025.csv
    data/raw/aqi_20cities_2023_2025.csv

输出：
    DS04_1_pollutant_prediction_performance.png
    DS04_2_feature_importance_heatmap.png
    DS04_3_shap_summary.png

运行：
    python ds04_air_quality_ml_analysis.py

说明：
    仅使用天气与AQI重叠时间段 2023-2025。
    只使用天气变量预测多种污染物，并比较不同污染物的预测效果；不使用经纬度和城市名作为模型输入。
"""

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import GroupShuffleSplit
from sklearn.inspection import permutation_importance

warnings.filterwarnings("ignore")

RAW_DIR = Path("data/raw")
FIGURE_DIR = Path("data/figures")
RESULT_DIR = Path("data/results")

FIGURE_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

WEATHER_PATH = RAW_DIR / "weather_20cities_2016_2025.csv"
AQI_PATH = RAW_DIR / "aqi_20cities_2023_2025.csv"

RANDOM_STATE = 42

POLLUTANT_NAME_MAP = {
    "pm2_5": "PM2.5",
    "pm10": "PM10",
    "nitrogen_dioxide": "NO2",
    "sulphur_dioxide": "SO2",
    "ozone": "O3",
    "dust": "Dust",
    "carbon_monoxide": "CO",
}

FEATURE_NAME_MAP = {
    "temperature_2m_mean": "平均气温",
    "temperature_2m_max": "最高气温",
    "temperature_2m_min": "最低气温",
    "apparent_temperature_mean": "体感温度",
    "relative_humidity_2m_mean": "相对湿度",
    "precipitation_sum": "降水量",
    "rain_sum": "降雨量",
    "wind_speed_10m_max": "最大风速",
    "wind_gusts_10m_max": "最大阵风",
    "sunshine_duration": "日照时长",
    "shortwave_radiation_sum": "短波辐射",
    "month": "月份",
    "season_code": "季节",
    "dayofyear": "年内日序",
}


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


def save_fig(filename):
    out_path = FIGURE_DIR / filename
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"已保存：{out_path}")


def add_note(fig, text, y=0.01):
    fig.text(0.5, y, text, ha="center", va="bottom", fontsize=11, color="#333333")


def get_season_code(month):
    if month in [3, 4, 5]:
        return 1
    if month in [6, 7, 8]:
        return 2
    if month in [9, 10, 11]:
        return 3
    return 4


def read_data():
    if not WEATHER_PATH.exists():
        raise FileNotFoundError(f"找不到天气数据文件：{WEATHER_PATH}")
    if not AQI_PATH.exists():
        raise FileNotFoundError(f"找不到AQI数据文件：{AQI_PATH}")

    weather = pd.read_csv(WEATHER_PATH, encoding="utf-8-sig")
    aqi = pd.read_csv(AQI_PATH, encoding="utf-8-sig")

    print("weather:", weather.shape)
    print("aqi:", aqi.shape)

    weather["time"] = pd.to_datetime(weather["time"])
    aqi["time"] = pd.to_datetime(aqi["time"])

    weather = weather[(weather["time"] >= "2023-01-01") & (weather["time"] <= "2025-12-31")].copy()
    aqi = aqi[(aqi["time"] >= "2023-01-01") & (aqi["time"] <= "2025-12-31")].copy()

    merged = pd.merge(
        weather,
        aqi,
        on=["time", "city", "lat", "lon", "year"],
        how="inner"
    )

    merged["month"] = merged["time"].dt.month
    merged["dayofyear"] = merged["time"].dt.dayofyear
    merged["season_code"] = merged["month"].apply(get_season_code)

    for col in merged.columns:
        if col not in ["time", "city"]:
            merged[col] = pd.to_numeric(merged[col], errors="coerce")

    merged = merged.sort_values(["city", "time"]).reset_index(drop=True)

    print("merged:", merged.shape)
    print("时间范围:", merged["time"].min(), "至", merged["time"].max())

    merged.to_csv(
        RESULT_DIR / "DS04_merged_weather_aqi_2023_2025.csv",
        index=False,
        encoding="utf-8-sig"
    )

    return merged


def get_feature_and_targets(df):
    feature_candidates = [
        "temperature_2m_mean",
        "temperature_2m_max",
        "temperature_2m_min",
        "apparent_temperature_mean",
        "relative_humidity_2m_mean",
        "precipitation_sum",
        "rain_sum",
        "wind_speed_10m_max",
        "wind_gusts_10m_max",
        "sunshine_duration",
        "shortwave_radiation_sum",
        "month",
        "season_code",
        "dayofyear",
    ]

    pollutant_candidates = [
        "pm2_5",
        "pm10",
        "nitrogen_dioxide",
        "sulphur_dioxide",
        "ozone",
        "dust",
    ]

    features = [c for c in feature_candidates if c in df.columns]
    pollutants = [c for c in pollutant_candidates if c in df.columns]

    forbidden = {"lat", "lon", "city"}
    leaked = forbidden.intersection(set(features))
    if leaked:
        raise ValueError(f"错误：模型输入特征中仍包含禁止字段：{leaked}")

    if len(features) < 5:
        raise ValueError("可用天气特征不足，请检查天气原始数据字段。")
    if len(pollutants) < 3:
        raise ValueError("可用污染物指标不足，请检查AQI原始数据字段。")

    print("\n模型输入特征（已严格去除 lat / lon / city）：")
    for f in features:
        print(" -", f)
    print("\n预测污染物:", pollutants)

    return features, pollutants


def train_one_model(df, features, target):
    model_df = df[["city"] + features + [target]].dropna().copy()

    X = model_df[features]
    y = model_df[target]
    groups = model_df["city"]

    forbidden = {"lat", "lon", "city"}
    leaked = forbidden.intersection(set(X.columns))
    if leaked:
        raise ValueError(f"错误：模型训练输入X中仍包含禁止字段：{leaked}")

    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.25,
        random_state=RANDOM_STATE
    )

    train_idx, test_idx = next(splitter.split(X, y, groups=groups))

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]
    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    model = RandomForestRegressor(
        n_estimators=350,
        random_state=RANDOM_STATE,
        max_depth=14,
        min_samples_leaf=3,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    r2 = r2_score(y_test, pred)
    try:
        rmse = mean_squared_error(y_test, pred, squared=False)
    except TypeError:
        rmse = np.sqrt(mean_squared_error(y_test, pred))
    mae = mean_absolute_error(y_test, pred)

    importance = pd.DataFrame({
        "feature": features,
        "importance": model.feature_importances_,
        "target": target,
    })

    pred_df = pd.DataFrame({
        "target": target,
        "actual": y_test.values,
        "predicted": pred,
        "city": model_df.iloc[test_idx]["city"].values,
    })

    return model, {
        "target": target,
        "target_name": POLLUTANT_NAME_MAP.get(target, target),
        "r2": r2,
        "rmse": rmse,
        "mae": mae,
        "n_train": len(X_train),
        "n_test": len(X_test),
    }, importance, pred_df, X_train, X_test, y_train, y_test


def train_all_models(df, features, pollutants):
    models = {}
    performance_rows = []
    importance_list = []
    pred_list = {}
    model_data = {}

    for target in pollutants:
        print(f"\n训练模型：{target}...")
        model, perf, importance, pred_df, X_train, X_test, y_train, y_test = train_one_model(df, features, target)

        models[target] = model
        performance_rows.append(perf)
        importance_list.append(importance)
        pred_list[target] = pred_df
        model_data[target] = {
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
        }

        print(
            f"{POLLUTANT_NAME_MAP.get(target, target)}: "
            f"R2={perf['r2']:.3f}, RMSE={perf['rmse']:.3f}, MAE={perf['mae']:.3f}"
        )

    performance = pd.DataFrame(performance_rows)
    importance_all = pd.concat(importance_list, ignore_index=True)

    performance.to_csv(RESULT_DIR / "DS04_weather_only_model_performance.csv", index=False, encoding="utf-8-sig")
    importance_all.to_csv(RESULT_DIR / "DS04_weather_only_feature_importance.csv", index=False, encoding="utf-8-sig")

    pred_all = pd.concat(pred_list.values(), ignore_index=True)
    pred_all.to_csv(RESULT_DIR / "DS04_weather_only_predictions.csv", index=False, encoding="utf-8-sig")

    return models, performance, importance_all, pred_list, model_data


def plot_ds04_1_performance(performance):
    print("\nDS04_1 多污染物预测性能比较...")

    perf = performance.copy()
    perf["污染物"] = perf["target"].map(POLLUTANT_NAME_MAP).fillna(perf["target"])
    perf = perf.sort_values("r2", ascending=False)

    fig, ax1 = plt.subplots(figsize=(12.5, 7))

    bars = ax1.bar(
        perf["污染物"],
        perf["r2"],
        color="#74add1",
        edgecolor="white",
        linewidth=1.0,
        alpha=0.92,
        label="R²"
    )

    ax1.axhline(0, color="#333333", linewidth=1)
    ax1.set_ylabel("R²（解释度）")
    ymin = min(-0.2, perf["r2"].min() - 0.1)
    ymax = min(1.0, max(0.2, perf["r2"].max() + 0.15))
    ax1.set_ylim(ymin, ymax)
    ax1.set_title("DS04_1 多污染物预测性能比较", pad=18, fontweight="bold")
    ax1.grid(axis="y", alpha=0.25)

    for bar, value in zip(bars, perf["r2"]):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            value + (0.03 if value >= 0 else -0.05),
            f"{value:.2f}",
            ha="center",
            va="bottom" if value >= 0 else "top",
            fontsize=11,
            fontweight="bold",
        )

    ax2 = ax1.twinx()
    ax2.plot(
        perf["污染物"],
        perf["rmse"],
        color="#d95f02",
        marker="o",
        linewidth=2.5,
        label="RMSE"
    )
    ax2.set_ylabel("RMSE")
    ax2.grid(False)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", frameon=True)

    add_note(
        fig,
        "说明：R²越高表示天气因素对该污染物的解释能力越强；测试集按城市分组划分，避免同一城市数据泄漏。",
        y=0.01,
    )

    plt.tight_layout(rect=[0, 0.05, 1, 1])
    save_fig("DS04_1_weather_only_pollutant_prediction_performance.png")


def plot_ds04_2_importance_heatmap(importance_all):
    print("\nDS04_2 特征重要性热力图...")

    imp = importance_all.copy()
    imp["污染物"] = imp["target"].map(POLLUTANT_NAME_MAP).fillna(imp["target"])
    imp["特征"] = imp["feature"].map(FEATURE_NAME_MAP).fillna(imp["feature"])

    forbidden_labels = {"lat", "lon", "city", "纬度", "经度"}
    leaked = forbidden_labels.intersection(set(imp["特征"]))
    if leaked:
        raise ValueError(f"错误：特征重要性图中仍包含经纬度或城市字段：{leaked}")

    pivot = imp.pivot_table(
        index="特征",
        columns="污染物",
        values="importance",
        aggfunc="mean"
    ).fillna(0)

    pivot = pivot.loc[pivot.mean(axis=1).sort_values(ascending=False).index]

    fig, ax = plt.subplots(figsize=(12, 8.5))

    sns.heatmap(
        pivot,
        annot=True,
        fmt=".3f",
        cmap="YlOrRd",
        linewidths=0.7,
        linecolor="white",
        cbar_kws={"label": "Random Forest 特征重要性"},
        ax=ax,
    )

    ax.set_title("DS04_2 天气因素对不同污染物预测的重要性热力图", pad=18, fontweight="bold")
    ax.set_xlabel("污染物")
    ax.set_ylabel("天气特征")
    ax.tick_params(axis="x", rotation=0)
    ax.tick_params(axis="y", rotation=0)

    add_note(
        fig,
        "说明：颜色越深表示该特征对对应污染物预测贡献越大；特征重要性反映模型解释，不等同于严格因果关系。",
        y=0.01,
    )

    pivot.to_csv(RESULT_DIR / "DS04_weather_only_feature_importance_pivot.csv", encoding="utf-8-sig")

    plt.tight_layout(rect=[0, 0.05, 1, 1])
    save_fig("DS04_2_weather_feature_importance_heatmap.png")


def plot_ds04_3_shap_or_fallback(models, performance, model_data, features):
    print("\n生成 DS04_3 Top3污染物SHAP解释图...")

    try:
        import shap
    except Exception as e:
        print("未安装 shap，无法生成 SHAP 图。错误：", e)
        return

    # 按 R² 选出预测效果最好的前三个污染物
    top3_targets = (
        performance
        .sort_values("r2", ascending=False)
        .head(3)["target"]
        .tolist()
    )

    print("Top3污染物：", top3_targets)

    safe_name_map = {
        "PM2.5": "PM25",
        "PM10": "PM10",
        "NO2": "NO2",
        "SO2": "SO2",
        "O3": "O3",
        "Dust": "Dust",
    }

    feature_name_list = [
        FEATURE_NAME_MAP.get(f, f)
        for f in features
    ]

    for idx, target in enumerate(top3_targets):
        pollutant_name = POLLUTANT_NAME_MAP.get(target, target)
        safe_name = safe_name_map.get(pollutant_name, pollutant_name)

        print(f"正在生成 {pollutant_name} 的 SHAP 图...")

        model = models[target]
        X_test = model_data[target]["X_test"].copy()

        # 再次确认没有经纬度
        forbidden = {"lat", "lon", "city"}
        leaked = forbidden.intersection(set(X_test.columns))
        if leaked:
            raise ValueError(f"错误：SHAP输入中仍包含禁止字段：{leaked}")

        # 抽样，避免运行太慢
        if len(X_test) > 800:
            X_sample = X_test.sample(800, random_state=RANDOM_STATE)
        else:
            X_sample = X_test

        X_show = X_sample.copy()
        X_show.columns = feature_name_list

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_sample)

        plt.figure(figsize=(11, 8))

        shap.summary_plot(
            shap_values,
            X_show,
            show=False,
            max_display=12,
            plot_size=(11, 8)
        )

        plt.title(
            f"DS04_3{chr(65 + idx)} SHAP解释图：{pollutant_name}预测模型",
            fontsize=18,
            fontweight="bold",
            pad=18
        )

        plt.tight_layout()

        save_path = FIGURE_DIR / f"DS04_3{chr(65 + idx)}_{safe_name}_SHAP.png"

        plt.savefig(
            save_path,
            dpi=300,
            bbox_inches="tight",
            facecolor="white"
        )

        plt.close()

        print(f"已保存：{save_path}")


def main():
    setup_style()

    print("\n读取并合并天气与AQI数据...")
    df = read_data()

    features, pollutants = get_feature_and_targets(df)

    print("\n训练多污染物预测模型...")
    models, performance, importance_all, pred_list, model_data = train_all_models(df, features, pollutants)

    plot_ds04_1_performance(performance)
    plot_ds04_2_importance_heatmap(importance_all)
    plot_ds04_3_shap_or_fallback(models, performance, model_data, features)

    print("\nDS04完成")
    print("输出图表目录：", FIGURE_DIR)
    print("输出结果目录：", RESULT_DIR)
    print("\n模型性能：")
    print(performance[["target_name", "r2", "rmse", "mae", "n_train", "n_test"]])


if __name__ == "__main__":
    main()
