const progressBar=document.getElementById("progressBar"),backToTop=document.getElementById("backToTop");window.addEventListener("scroll",()=>{const s=window.scrollY,d=document.documentElement.scrollHeight-window.innerHeight,p=d>0?s/d*100:0;progressBar.style.width=`${p}%`;backToTop.style.display=s>640?"block":"none"});backToTop.addEventListener("click",()=>window.scrollTo({top:0,behavior:"smooth"}));const observer=new IntersectionObserver(e=>{e.forEach(t=>{t.isIntersecting&&t.target.classList.add("visible")})},{threshold:.12});document.querySelectorAll(".reveal").forEach(e=>observer.observe(e));document.querySelectorAll(".tab-btn").forEach(e=>{e.addEventListener("click",()=>{const t=e.dataset.tab;document.querySelectorAll(".tab-btn").forEach(e=>e.classList.remove("active"));e.classList.add("active");document.querySelectorAll(".tab-panel").forEach(e=>e.classList.remove("active"));document.getElementById(`tab-${t}`).classList.add("active")})});
const galleryItems=[["DS00_1","data/figures/DS00_1_climate_correlation_heatmap.png","DS00_1 气候相关性热力图"],["DS00_2","data/figures/DS00_2_aqi_correlation_heatmap.png","DS00_2 AQI相关性热力图"],["DS00_3","data/figures/DS00_3_key_indicator_boxplot.png","DS00_3 关键指标箱线图"],["DS01_1","data/figures/DS01_1_city_cluster_pca.png","DS01_1 PCA聚类图"],["DS01_2","data/figures/DS01_2_type_radar.png","DS01_2 类型雷达图"],["DS01_3","data/figures/DS01_3_city_type_geo_distribution.png","DS01_3 城市类型地理分布图"],["DS01_4","data/figures/DS01_4_type_feature_heatmap.png","DS01_4 类型特征热力图"],["DS02_1","data/figures/DS02_1_temperature_trend_2016_2025.png","DS02_1 十年气温趋势"],["DS02_2","data/figures/DS02_2_season_comfort_distribution.png","DS02_2 季节舒适度分布"],["DS02_3","data/figures/DS02_3_air_quality_heatmap_2023_2025.png","DS02_3 近三年空气质量热力图"],["DS02_4","data/figures/DS02_4_extreme_weather_trend.png","DS02_4 极端天气趋势"],["DS03_1","data/figures/DS03_1_extreme_weather_city_heatmap.png","DS03_1 极端天气城市对比"],["DS03_2","data/figures/DS03_2_extreme_weather_driver_scatter.png","DS03_2 极端天气驱动关系"],["DS03_3","data/figures/DS03_3_extreme_weather_spatial_distribution.png","DS03_3 极端天气空间分布"],["DS04_1","data/figures/DS04_1_weather_only_pollutant_prediction_performance.png","DS04_1 多污染物预测性能"],["DS04_2","data/figures/DS04_2_weather_feature_importance_heatmap.png","DS04_2 天气因素重要性热力图"],["DS04_3A","data/figures/DS04_3A_O3_SHAP.png","DS04_3A O3 SHAP解释图"],["DS04_3B","data/figures/DS04_3B_NO2_SHAP.png","DS04_3B NO2 SHAP解释图"],["DS04_3C","data/figures/DS04_3C_PM25_SHAP.png","DS04_3C PM2.5 SHAP解释图"]];
const controls=document.getElementById("galleryControls"),galleryImage=document.getElementById("galleryImage"),galleryCaption=document.getElementById("galleryCaption");if(controls&&galleryImage&&galleryCaption){galleryItems.forEach((item,index)=>{const btn=document.createElement("button");btn.textContent=item[0];if(index===5)btn.classList.add("active");btn.addEventListener("click",()=>{document.querySelectorAll(".gallery-controls button").forEach(b=>b.classList.remove("active"));btn.classList.add("active");galleryImage.src=item[1];galleryCaption.textContent=item[2]});controls.appendChild(btn)})}
const modal=document.getElementById("imageModal"),modalImage=document.getElementById("modalImage"),modalCaption=document.getElementById("modalCaption"),modalClose=document.getElementById("modalClose");document.querySelectorAll(".figure-card img, .gallery-view img").forEach(img=>{img.addEventListener("click",()=>{modal.style.display="block";modalImage.src=img.src;const fig=img.closest("figure"),cap=fig?fig.querySelector("figcaption b"):null;modalCaption.textContent=cap?cap.textContent:img.alt})});modalClose.addEventListener("click",()=>modal.style.display="none");modal.addEventListener("click",event=>{event.target===modal&&(modal.style.display="none")});

/* ================================
   Final City Explorer + Dynamic Charts + ECharts China Map
================================ */
document.addEventListener("DOMContentLoaded", initFinalCityExplorer);

function initFinalCityExplorer() {
  if (typeof CITY_DATA === "undefined") {
    console.warn("CITY_DATA 未加载");
    return;
  }

  const cityInfo = document.getElementById("cityInfo");
  if (!cityInfo) return;

  const cities = CITY_DATA.profile || [];
  const labels = CITY_DATA.fieldLabels || {};
  const units = CITY_DATA.fieldUnits || {};

  function valueOnly(v) {
    if (v === null || v === undefined || v === "" || Number.isNaN(Number(v))) return null;
    return Number(v);
  }

  function fmt(v, field = "") {
    const n = valueOnly(v);
    if (n === null) return "暂无";
    return (Number.isInteger(n) ? String(n) : n.toFixed(1)) + (units[field] || "");
  }

  function card(field, row) {
    return `
      <div class="city-metric">
        <span>${fmt(row ? row[field] : null, field)}</span>
        <p>${labels[field] || field}</p>
      </div>
    `;
  }

  function group(title, fields, row) {
    return `
      <h4 class="city-section-title">${title}</h4>
      <div class="city-metric-grid">
        ${fields.map(f => card(f, row)).join("")}
      </div>
    `;
  }

  function rows(level, cityName) {
    return (CITY_DATA[level] || []).filter(d => d.city === cityName);
  }

  function chartBox(title, id, note = "") {
    return `
      <div class="city-chart-card">
        <div class="city-chart-head">
          <h4>${title}</h4>
          ${note ? `<p>${note}</p>` : ""}
        </div>
        <div id="${id}" class="city-chart"></div>
      </div>
    `;
  }

  function drawLineChart(id, data, xField, series) {
    const el = document.getElementById(id);
    if (!el) return;

    const clean = data.filter(r => series.some(s => valueOnly(r[s.field]) !== null));
    if (!clean.length) {
      el.innerHTML = `<div class="city-chart-empty">暂无可绘制数据</div>`;
      return;
    }

    const W = 760, H = 280, L = 54, R = 24, T = 22, B = 48;
    const plotW = W - L - R;
    const plotH = H - T - B;
    const vals = [];

    clean.forEach(r => series.forEach(s => {
      const v = valueOnly(r[s.field]);
      if (v !== null) vals.push(v);
    }));

    let min = Math.min(...vals);
    let max = Math.max(...vals);

    if (min === max) {
      min -= 1;
      max += 1;
    }

    const span = max - min;
    min -= span * 0.08;
    max += span * 0.08;

    const x = i => clean.length === 1 ? L + plotW / 2 : L + i / (clean.length - 1) * plotW;
    const y = v => T + (1 - (v - min) / (max - min)) * plotH;
    const colors = ["#1f77b4", "#d97706", "#4b9b75", "#b14d4d"];

    const grid = [0, .25, .5, .75, 1].map(t => {
      const yy = T + t * plotH;
      const val = max - t * (max - min);
      return `
        <line x1="${L}" y1="${yy}" x2="${W - R}" y2="${yy}" class="chart-grid"/>
        <text x="${L - 10}" y="${yy + 4}" class="chart-axis-label" text-anchor="end">${val.toFixed(1)}</text>
      `;
    }).join("");

    const xLabels = clean.map((r, i) => {
      const show = clean.length <= 12 || i % Math.ceil(clean.length / 8) === 0 || i === clean.length - 1;
      return show ? `<text x="${x(i)}" y="${H - 18}" class="chart-axis-label" text-anchor="middle">${r[xField]}</text>` : "";
    }).join("");

    const lines = series.map((s, si) => {
      const pts = clean.map((r, i) => {
        const v = valueOnly(r[s.field]);
        return v === null ? null : { x: x(i), y: y(v), v, label: r[xField] };
      }).filter(Boolean);

      const d = pts.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");
      const dots = pts.map(p => `
        <circle cx="${p.x}" cy="${p.y}" r="4" fill="${colors[si % colors.length]}">
          <title>${s.name} ${p.label}: ${p.v.toFixed(2)}${s.unit || ""}</title>
        </circle>
      `).join("");

      return `
        <path d="${d}" fill="none" stroke="${colors[si % colors.length]}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
        ${dots}
      `;
    }).join("");

    const legend = series.map((s, i) => `
      <span class="chart-legend-item">
        <i style="background:${colors[i % colors.length]}"></i>${s.name}
      </span>
    `).join("");

    el.innerHTML = `
      <div class="chart-legend">${legend}</div>
      <svg viewBox="0 0 ${W} ${H}" class="city-svg-chart" preserveAspectRatio="none">
        ${grid}
        <line x1="${L}" y1="${H - B}" x2="${W - R}" y2="${H - B}" class="chart-axis"/>
        <line x1="${L}" y1="${T}" x2="${L}" y2="${H - B}" class="chart-axis"/>
        ${xLabels}
        ${lines}
      </svg>
    `;
  }

  function drawBarChart(id, data, xField, field) {
    const el = document.getElementById(id);
    if (!el) return;

    const clean = data.filter(r => valueOnly(r[field]) !== null);
    if (!clean.length) {
      el.innerHTML = `<div class="city-chart-empty">暂无可绘制数据</div>`;
      return;
    }

    const W = 760, H = 280, L = 54, R = 24, T = 22, B = 48;
    const plotW = W - L - R;
    const plotH = H - T - B;
    const vals = clean.map(r => valueOnly(r[field]));

    let min = Math.min(0, ...vals);
    let max = Math.max(...vals);
    if (min === max) max += 1;

    const y = v => T + (1 - (v - min) / (max - min)) * plotH;
    const gap = 12;
    const bw = Math.max(12, (plotW - gap * (clean.length - 1)) / clean.length);

    const grid = [0, .25, .5, .75, 1].map(t => {
      const yy = T + t * plotH;
      const val = max - t * (max - min);
      return `
        <line x1="${L}" y1="${yy}" x2="${W - R}" y2="${yy}" class="chart-grid"/>
        <text x="${L - 10}" y="${yy + 4}" class="chart-axis-label" text-anchor="end">${val.toFixed(1)}</text>
      `;
    }).join("");

    const bars = clean.map((r, i) => {
      const v = valueOnly(r[field]);
      const xx = L + i * (bw + gap);
      const yy = y(v);
      const h = H - B - yy;
      return `
        <rect x="${xx}" y="${yy}" width="${bw}" height="${Math.max(0, h)}" rx="8" class="chart-bar">
          <title>${r[xField]}: ${v.toFixed(2)}</title>
        </rect>
        <text x="${xx + bw / 2}" y="${H - 18}" class="chart-axis-label" text-anchor="middle">${r[xField]}</text>
      `;
    }).join("");

    el.innerHTML = `
      <svg viewBox="0 0 ${W} ${H}" class="city-svg-chart" preserveAspectRatio="none">
        ${grid}
        <line x1="${L}" y1="${H - B}" x2="${W - R}" y2="${H - B}" class="chart-axis"/>
        <line x1="${L}" y1="${T}" x2="${L}" y2="${H - B}" class="chart-axis"/>
        ${bars}
      </svg>
    `;
  }

  function renderProfile(row) {
    const detail = document.getElementById("cityDetail");
    if (!detail) return;

    detail.innerHTML =
      group("基础概览", ["records","avg_temp","avg_humidity","air_quality_score","climate_comfort_index","tourism_comfort_index"], row) +
      group("温度特征", ["avg_temp","avg_temp_max","avg_temp_min","avg_temp_range","avg_apparent_temp","avg_apparent_gap"], row) +
      group("降水湿度", ["avg_humidity","total_precipitation","avg_precipitation","rainy_days","heavy_rain_days"], row) +
      group("风与光照", ["avg_wind","avg_wind_gust","windy_days","gusty_days","avg_sunshine_hour","avg_shortwave"], row) +
      group("极端天气", ["hot_days","extreme_hot_days","cold_days","freezing_days"], row) +
      group("空气质量", ["avg_pm25","avg_pm10","avg_no2","avg_so2","avg_ozone","avg_dust","good_air_days","polluted_days"], row) +
      group("综合指数", ["climate_comfort_index","air_quality_score","tourism_comfort_index","pollution_index","summer_escape_index","winter_retirement_index"], row) +
      `<div class="city-note">说明：空气质量指标主要基于 2023—2025 年 AQI 数据。</div>`;
  }

  function renderYear(cityName) {
    const data = rows("year", cityName);
    const years = [...new Set(data.map(d => d.year))].sort((a,b) => Number(a) - Number(b));
    const detail = document.getElementById("cityDetail");

    detail.innerHTML = `
      <div class="city-select-row">
        <label>选择年份</label>
        <select id="yearSelect">${years.map(y => `<option value="${y}">${y}</option>`).join("")}</select>
      </div>
      <div id="yearContent"></div>
      <div class="city-chart-grid">
        ${chartBox("2016—2025 年平均气温趋势", "yearTempChart", "观察该城市十年气温变化。")}
        ${chartBox("2016—2025 年极端天气趋势", "yearExtremeChart", "高温天数与冰冻天数对比。")}
        ${chartBox("2023—2025 年 PM2.5 变化", "yearPmChart", "AQI 数据仅覆盖 2023—2025 年。")}
      </div>
    `;

    const select = document.getElementById("yearSelect");
    if (years.includes(2025)) select.value = "2025";

    function update() {
      const row = data.find(d => String(d.year) === String(select.value));
      document.getElementById("yearContent").innerHTML =
        group(`${select.value} 年气候概览`, ["records","avg_temp","avg_temp_max","avg_temp_min","total_precipitation","avg_humidity"], row) +
        group("极端天气", ["hot_days","extreme_hot_days","cold_days","freezing_days"], row) +
        group("空气质量与指数", ["avg_pm25","avg_pm10","avg_no2","avg_ozone","air_quality_score","climate_comfort_index"], row) +
        `<div class="city-note">注意：AQI 数据仅覆盖 2023—2025 年，较早年份空气质量字段可能为“暂无”。</div>`;
    }

    select.addEventListener("change", update);
    update();

    drawLineChart("yearTempChart", data, "year", [
      { field: "avg_temp", name: "平均气温", unit: "℃" },
      { field: "avg_temp_max", name: "平均最高气温", unit: "℃" },
      { field: "avg_temp_min", name: "平均最低气温", unit: "℃" }
    ]);

    drawLineChart("yearExtremeChart", data, "year", [
      { field: "hot_days", name: "高温天数", unit: "天" },
      { field: "freezing_days", name: "冰冻天数", unit: "天" }
    ]);

    drawLineChart("yearPmChart", data.filter(d => valueOnly(d.avg_pm25) !== null), "year", [
      { field: "avg_pm25", name: "PM2.5", unit: "μg/m³" }
    ]);
  }

  function renderMonth(cityName) {
    const data = rows("month", cityName);
    const years = [...new Set(data.map(d => d.year))].sort((a,b) => Number(a) - Number(b));
    const detail = document.getElementById("cityDetail");

    detail.innerHTML = `
      <div class="city-select-row">
        <label>年份</label>
        <select id="monthYearSelect">${years.map(y => `<option value="${y}">${y}</option>`).join("")}</select>
        <label>月份</label>
        <select id="monthSelect"></select>
      </div>
      <div id="monthContent"></div>
      <div class="city-chart-grid">
        ${chartBox("该年 1—12 月气温周期", "monthTempChart")}
        ${chartBox("该年 1—12 月降水变化", "monthRainChart")}
        ${chartBox("该年 1—12 月 PM2.5 变化", "monthPmChart")}
      </div>
    `;

    const yearSelect = document.getElementById("monthYearSelect");
    const monthSelect = document.getElementById("monthSelect");
    if (years.includes(2025)) yearSelect.value = "2025";

    function currentRows() {
      return data
        .filter(d => String(d.year) === String(yearSelect.value))
        .sort((a,b) => Number(a.month) - Number(b.month));
    }

    function updateMonths() {
      const months = currentRows().map(d => Number(d.month)).sort((a,b) => a-b);
      monthSelect.innerHTML = [...new Set(months)].map(m => `<option value="${m}">${m}月</option>`).join("");
      update();
      drawCharts();
    }

    function update() {
      const row = data.find(d =>
        String(d.year) === String(yearSelect.value) &&
        String(d.month) === String(monthSelect.value)
      );
      if (!row) return;

      document.getElementById("monthContent").innerHTML =
        group(`${yearSelect.value} 年 ${monthSelect.value} 月气候画像`, ["records","avg_temp","avg_temp_max","avg_temp_min","avg_humidity","total_precipitation"], row) +
        group("天气事件", ["rainy_days","heavy_rain_days","hot_days","extreme_hot_days","cold_days","freezing_days"], row) +
        group("空气质量与指数", ["avg_pm25","avg_pm10","avg_no2","avg_ozone","air_quality_score","climate_comfort_index"], row);
    }

    function drawCharts() {
      const r = currentRows();

      drawLineChart("monthTempChart", r, "month", [
        { field: "avg_temp", name: "平均气温", unit: "℃" },
        { field: "avg_temp_max", name: "平均最高气温", unit: "℃" },
        { field: "avg_temp_min", name: "平均最低气温", unit: "℃" }
      ]);

      drawBarChart("monthRainChart", r, "month", "total_precipitation");

      drawLineChart("monthPmChart", r.filter(d => valueOnly(d.avg_pm25) !== null), "month", [
        { field: "avg_pm25", name: "PM2.5", unit: "μg/m³" }
      ]);
    }

    yearSelect.addEventListener("change", updateMonths);
    monthSelect.addEventListener("change", update);
    updateMonths();
  }

  function renderSeason(cityName) {
    const data = rows("season", cityName);
    const years = [...new Set(data.map(d => d.year))].sort((a,b) => Number(a) - Number(b));
    const detail = document.getElementById("cityDetail");

    detail.innerHTML = `
      <div class="city-select-row">
        <label>年份</label>
        <select id="seasonYearSelect">${years.map(y => `<option value="${y}">${y}</option>`).join("")}</select>
        <label>季节</label>
        <select id="seasonSelect"></select>
      </div>
      <div id="seasonContent"></div>
      <div class="city-chart-grid">
        ${chartBox("该年四季平均气温", "seasonTempChart")}
        ${chartBox("该年四季气候舒适度", "seasonComfortChart")}
        ${chartBox("该年四季 PM2.5 变化", "seasonPmChart")}
      </div>
    `;

    const yearSelect = document.getElementById("seasonYearSelect");
    const seasonSelect = document.getElementById("seasonSelect");
    if (years.includes(2025)) yearSelect.value = "2025";

    const order = ["春季", "夏季", "秋季", "冬季"];

    function currentRows() {
      return data
        .filter(d => String(d.year) === String(yearSelect.value))
        .map(d => ({ ...d, seasonLabel: d.season_name || d.season }))
        .sort((a,b) => order.indexOf(a.seasonLabel) - order.indexOf(b.seasonLabel));
    }

    function updateSeasons() {
      const seasons = currentRows().map(d => d.seasonLabel);
      seasonSelect.innerHTML = [...new Set(seasons)].map(s => `<option value="${s}">${s}</option>`).join("");
      update();
      drawCharts();
    }

    function update() {
      const row = currentRows().find(d => String(d.seasonLabel) === String(seasonSelect.value));
      if (!row) return;

      document.getElementById("seasonContent").innerHTML =
        group(`${yearSelect.value} 年 ${seasonSelect.value} 气候画像`, ["records","avg_temp","avg_temp_max","avg_temp_min","avg_humidity","total_precipitation"], row) +
        group("极端天气", ["hot_days","extreme_hot_days","cold_days","freezing_days"], row) +
        group("空气质量与指数", ["avg_pm25","avg_pm10","avg_no2","avg_ozone","air_quality_score","climate_comfort_index"], row);
    }

    function drawCharts() {
      const r = currentRows();

      drawBarChart("seasonTempChart", r, "seasonLabel", "avg_temp");
      drawBarChart("seasonComfortChart", r, "seasonLabel", "climate_comfort_index");
      drawBarChart("seasonPmChart", r.filter(d => valueOnly(d.avg_pm25) !== null), "seasonLabel", "avg_pm25");
    }

    yearSelect.addEventListener("change", updateSeasons);
    seasonSelect.addEventListener("change", update);
    updateSeasons();
  }

  function bindTabs(cityName) {
    document.querySelectorAll(".city-tab").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".city-tab").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        const tab = btn.dataset.tabCity;

        if (tab === "profile") renderProfile(cities.find(d => d.city === cityName));
        if (tab === "year") renderYear(cityName);
        if (tab === "month") renderMonth(cityName);
        if (tab === "season") renderSeason(cityName);
      });
    });
  }

  function renderCity(cityName) {
    const profile = cities.find(d => d.city === cityName);
    if (!profile) return;

    cityInfo.innerHTML = `
      <div class="city-header">
        <div>
          <h3>${profile.city}</h3>
          <p class="city-type">${profile.city_type || "未知类型"}</p>
        </div>
        <div class="city-coord">
          纬度：${fmt(profile.lat)}<br>
          经度：${fmt(profile.lon)}
        </div>
      </div>

      <div class="city-tabs">
        <button class="city-tab active" data-tab-city="profile">总体画像</button>
        <button class="city-tab" data-tab-city="year">年度画像</button>
        <button class="city-tab" data-tab-city="month">月度画像</button>
        <button class="city-tab" data-tab-city="season">季节画像</button>
      </div>

      <div id="cityDetail"></div>
    `;

    renderProfile(profile);
    bindTabs(profile.city);
  }

  window.renderCityFromMap = function(cityName, shouldScroll = true) {
    renderCity(cityName);

    if (shouldScroll) {
      const profile = document.querySelector(".city-profile-wrapper");
      if (profile) profile.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  const defaultCity = cities.find(d => d.city === "北京") || cities[0];
  if (defaultCity) renderCity(defaultCity.city);

  initFinalChinaMap(cities, fmt);
}

function initFinalChinaMap(cities, fmt) {
  if (typeof echarts === "undefined") {
    console.warn("ECharts 未加载，跳过中国地图。");
    return;
  }

  if (typeof chinaJson === "undefined") {
    console.warn("chinaJson 未加载，请确认 index.html 中已引入 js/china_map.js");
    return;
  }

  const mapDom = document.getElementById("chinaMap");
  if (!mapDom) return;

  try {
    echarts.registerMap("china", chinaJson);

    const chart = echarts.init(mapDom);

    const cityPoints = (cities || [])
      .filter(c => Number.isFinite(Number(c.lon)) && Number.isFinite(Number(c.lat)))
      .map(c => ({
        name: c.city,
        value: [
          Number(c.lon),
          Number(c.lat),
          Number(c.tourism_comfort_index || c.climate_comfort_index || 0)
        ],
        cityType: c.city_type || "未知类型",
        avgTemp: c.avg_temp,
        pm25: c.avg_pm25,
        airScore: c.air_quality_score
      }));

    chart.setOption({
      backgroundColor: "transparent",

      tooltip: {
        trigger: "item",
        formatter: function(params) {
          if (params.seriesType === "effectScatter") {
            const d = params.data || {};
            const temp = d.avgTemp === null || d.avgTemp === undefined ? "暂无" : Number(d.avgTemp).toFixed(1) + "℃";
            const pm25 = d.pm25 === null || d.pm25 === undefined ? "暂无" : Number(d.pm25).toFixed(1);
            const air = d.airScore === null || d.airScore === undefined ? "暂无" : Number(d.airScore).toFixed(1);

            return `
              <strong>${d.name}</strong><br/>
              类型：${d.cityType}<br/>
              平均气温：${temp}<br/>
              PM2.5：${pm25}<br/>
              空气质量得分：${air}<br/>
              <span style="color:#64748b">点击查看城市档案</span>
            `;
          }
          return params.name || "";
        }
      },

      geo: {
        map: "china",
        roam: false,
        zoom: 1.13,
        center: [104.5, 35.5],
        label: {
          show: false
        },
        itemStyle: {
          areaColor: "#dbeafe",
          borderColor: "#94a3b8",
          borderWidth: 0.9
        },
        emphasis: {
          label: {
            show: false
          },
          itemStyle: {
            areaColor: "#bfdbfe"
          }
        }
      },

      series: [
        {
          name: "中国地图",
          type: "map",
          map: "china",
          geoIndex: 0,
          silent: true
        },
        {
          name: "热门旅游城市",
          type: "effectScatter",
          coordinateSystem: "geo",
          data: cityPoints,
          symbolSize: function(value) {
            const score = Number(value[2]);
            if (!Number.isFinite(score)) return 12;
            return Math.max(12, Math.min(19, 10 + score / 13));
          },
          rippleEffect: {
            brushType: "stroke",
            scale: 2.5
          },
          label: {
            show: true,
            formatter: "{b}",
            position: "right",
            color: "#1f2937",
            fontSize: 12,
            fontWeight: 700,
            backgroundColor: "rgba(255,255,255,0.82)",
            borderRadius: 4,
            padding: [2, 4]
          },
          itemStyle: {
            color: "#d97706",
            shadowBlur: 10,
            shadowColor: "rgba(217,119,6,.35)"
          },
          emphasis: {
            scale: true,
            label: {
              show: true
            }
          },
          zlevel: 3
        }
      ]
    });

    chart.on("click", function(params) {
      if (params.seriesType !== "effectScatter") return;

      if (typeof window.renderCityFromMap === "function") {
        window.renderCityFromMap(params.name, true);
      }
    });

    window.addEventListener("resize", function() {
      chart.resize();
    });

  } catch (err) {
    console.warn(err);

    mapDom.innerHTML = `
      <div class="city-chart-empty">
        中国地图加载失败。请确认 index.html 中已按顺序引入 echarts、china_map.js、city_data.js 和 script.js。
      </div>
    `;
  }
}


const sideToc = document.querySelector(".side-toc");

if (sideToc) {
  sideToc.addEventListener("click", function (event) {
    event.stopPropagation();
    sideToc.classList.toggle("open");
  });

  document.addEventListener("click", function () {
    sideToc.classList.remove("open");
  });

  sideToc.querySelectorAll("a").forEach(link => {
    link.addEventListener("click", function () {
      sideToc.classList.remove("open");
    });
  });
}