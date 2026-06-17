const progressBar=document.getElementById("progressBar"),backToTop=document.getElementById("backToTop");window.addEventListener("scroll",()=>{const s=window.scrollY,d=document.documentElement.scrollHeight-window.innerHeight,p=d>0?s/d*100:0;progressBar.style.width=`${p}%`;backToTop.style.display=s>640?"block":"none"});backToTop.addEventListener("click",()=>window.scrollTo({top:0,behavior:"smooth"}));const observer=new IntersectionObserver(e=>{e.forEach(t=>{t.isIntersecting&&t.target.classList.add("visible")})},{threshold:.12});document.querySelectorAll(".reveal").forEach(e=>observer.observe(e));document.querySelectorAll(".tab-btn").forEach(e=>{e.addEventListener("click",()=>{const t=e.dataset.tab;document.querySelectorAll(".tab-btn").forEach(e=>e.classList.remove("active"));e.classList.add("active");document.querySelectorAll(".tab-panel").forEach(e=>e.classList.remove("active"));document.getElementById(`tab-${t}`).classList.add("active")})});
const galleryItems=[
  {id:"DS00_1",src:"data/figures/DS00_1_climate_correlation_heatmap.png",title:"气候相关性",full:"DS00_1 气候相关性热力图",finding:"温度类指标高度相关，降水量与降雨天数也具有明显耦合关系。",conclusion:"气候指标体系具有稳定内部结构，可支撑后续城市分类。"},
  {id:"DS00_2",src:"data/figures/DS00_2_aqi_correlation_heatmap.png",title:"空气质量相关性",full:"DS00_2 AQI相关性热力图",finding:"PM2.5、PM10、NO₂和SO₂存在较强相关性，O₃呈现相对独立的变化机制。",conclusion:"空气污染并非单一机制驱动，需要区分颗粒物污染与光化学污染。"},
  {id:"DS00_3",src:"data/figures/DS00_3_key_indicator_boxplot.png",title:"关键指标分布",full:"DS00_3 关键指标箱线图",finding:"空气质量、避暑指数和养老指数在城市之间离散程度较大。",conclusion:"20个城市存在明显差异，适合进一步构建城市气候画像。"},
  {id:"DS01_1",src:"data/figures/DS01_1_city_cluster_pca.png",title:"城市聚类",full:"DS01_1 PCA聚类图",finding:"高原、滨海和北方城市在主成分空间中分离明显。",conclusion:"城市可归纳为具有解释意义的典型气候类型。"},
  {id:"DS01_2",src:"data/figures/DS01_2_type_radar.png",title:"类型雷达",full:"DS01_2 类型雷达图",finding:"高原城市避暑和空气质量突出，滨海城市暖冬优势明显。",conclusion:"不同城市类型具有不同旅游季节优势。"},
  {id:"DS01_3",src:"data/figures/DS01_3_city_type_geo_distribution.png",title:"类型空间分布",full:"DS01_3 城市类型地理分布图",finding:"高原型集中在西南，滨海型集中在华南和东南沿海，北方型分布在高纬或内陆。",conclusion:"城市类型与纬度、海陆位置和地形条件密切相关。"},
  {id:"DS01_4",src:"data/figures/DS01_4_type_feature_heatmap.png",title:"类型特征",full:"DS01_4 类型特征热力图",finding:"四类城市在温度、日照、空气质量、避暑和养老指数上呈现明显差异。",conclusion:"热力图解释了城市分类背后的气候特征。"},
  {id:"DS02_1",src:"data/figures/DS02_1_temperature_trend_2016_2025.png",title:"十年气温趋势",full:"DS02_1 十年气温趋势",finding:"20城平均气温由17.1℃上升至17.8℃，十年升温约0.7℃。",conclusion:"气候变暖已成为我国热门旅游城市的共同趋势。"},
  {id:"DS02_2",src:"data/figures/DS02_2_season_comfort_distribution.png",title:"季节舒适度",full:"DS02_2 季节舒适度分布",finding:"春秋季整体最舒适，夏季差异扩大，冬季城市类型差异最明显。",conclusion:"城市旅游适宜性具有明显季节互补特征。"},
  {id:"DS02_3",src:"data/figures/DS02_3_air_quality_heatmap_2023_2025.png",title:"近三年空气质量",full:"DS02_3 近三年空气质量热力图",finding:"三亚、丽江、大理等城市空气质量长期较高，多数城市近三年波动较小。",conclusion:"空气质量的空间差异大于短期时间波动。"},
  {id:"DS02_4",src:"data/figures/DS02_4_extreme_weather_trend.png",title:"极端天气趋势",full:"DS02_4 极端天气趋势",finding:"高温和极端高温天数增加，冰冻天数下降。",conclusion:"气候变暖背景下，高温风险正在增强。"},
  {id:"DS03_1",src:"data/figures/DS03_1_extreme_weather_city_heatmap.png",title:"极端天气城市对比",full:"DS03_1 极端天气城市对比",finding:"南方城市高温突出，北方城市寒冷和冰冻突出，高原城市极端天气较弱。",conclusion:"极端天气呈现南方高温、北方冰冻、高原稳定的格局。"},
  {id:"DS03_2",src:"data/figures/DS03_2_extreme_weather_driver_scatter.png",title:"极端天气驱动",full:"DS03_2 极端天气驱动关系",finding:"平均气温与高温天数强正相关，与冰冻天数强负相关。",conclusion:"温度是解释城市极端天气差异的核心变量。"},
  {id:"DS03_3",src:"data/figures/DS03_3_extreme_weather_spatial_distribution.png",title:"极端天气空间分布",full:"DS03_3 极端天气空间分布",finding:"高温集中在华南沿海和长江流域，冰冻集中在东北、西北和华北。",conclusion:"极端天气风险具有明显区域性。"},
  {id:"DS03_4",src:"data/figures/DS03_4_climate_mechanism_framework.png",title:"气候机制框架",full:"DS03_4 气候形成机制框架",finding:"自然地理条件影响气候因子，再影响极端天气和城市类型。",conclusion:"城市气候差异遵循空间条件—气候因子—极端表现—城市类型的路径。"},
  {id:"DS04_1",src:"data/figures/DS04_1_weather_only_pollutant_prediction_performance.png",title:"多污染物预测",full:"DS04_1 多污染物预测性能",finding:"O₃最容易被天气解释，Dust预测效果最差。",conclusion:"不同污染物对天气因素的敏感程度存在显著差异。"},
  {id:"DS04_2",src:"data/figures/DS04_2_weather_feature_importance_heatmap.png",title:"天气特征重要性",full:"DS04_2 天气因素重要性热力图",finding:"短波辐射主导O₃，风场条件影响NO₂、PM2.5和SO₂。",conclusion:"污染物具有不同气象控制机制。"},
  {id:"DS04_3A",src:"data/figures/DS04_3A_O3_SHAP.png",title:"O₃ SHAP",full:"DS04_3A O₃ SHAP解释图",finding:"高短波辐射和高温条件会提高臭氧预测浓度。",conclusion:"臭氧治理需要重点关注强辐射和高温天气。"},
  {id:"DS04_3B",src:"data/figures/DS04_3B_NO2_SHAP.png",title:"NO₂ SHAP",full:"DS04_3B NO₂ SHAP解释图",finding:"较强风场通常对应更低NO₂预测浓度。",conclusion:"NO₂变化受到排放和扩散条件共同影响。"},
  {id:"DS04_3C",src:"data/figures/DS04_3C_PM25_SHAP.png",title:"PM2.5 SHAP",full:"DS04_3C PM2.5 SHAP解释图",finding:"PM2.5受风场扩散、降水清除和湿度条件共同影响。",conclusion:"颗粒物污染是扩散、清除和季节条件共同作用的结果。"}
];
const controls=document.getElementById("galleryControls"),galleryImage=document.getElementById("galleryImage"),galleryCaption=document.getElementById("galleryCaption");
function renderGalleryCaption(item){
  return `<strong>${item.full}</strong><span>主要发现：${item.finding}</span><span>研究结论：${item.conclusion}</span>`;
}
if(controls&&galleryImage&&galleryCaption){galleryItems.forEach((item,index)=>{const btn=document.createElement("button");btn.textContent=item.title;if(index===5)btn.classList.add("active");btn.addEventListener("click",()=>{document.querySelectorAll(".gallery-controls button").forEach(b=>b.classList.remove("active"));btn.classList.add("active");galleryImage.src=item.src;galleryCaption.innerHTML=renderGalleryCaption(item)});controls.appendChild(btn)});const initItem=galleryItems[5]||galleryItems[0];galleryImage.src=initItem.src;galleryCaption.innerHTML=renderGalleryCaption(initItem)}
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