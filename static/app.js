const state = {
  analytics: null,
  selectedBuilding: "All",
};

const money = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });

function qs(selector) {
  return document.querySelector(selector);
}

function qsa(selector) {
  return [...document.querySelectorAll(selector)];
}

async function loadAnalytics(refresh = false) {
  const response = await fetch(`/api/analytics${refresh ? "?refresh=1" : ""}`);
  if (!response.ok) throw new Error("Could not load analytics");
  state.analytics = await response.json();
  render();
}

function pct(value) {
  const sign = value > 0 ? "+" : "";
  return `${sign}${value}%`;
}

function renderMetricCards(summary) {
  const metrics = [
    {
      label: "Potential weekly savings",
      value: `${money.format(summary.potential_savings_kwh)} kWh`,
      detail: `${money.format(summary.potential_emissions_lbs)} lbs CO2 avoided`,
      tone: "good",
    },
    {
      label: "24h energy trend",
      value: pct(summary.trend_pct),
      detail: `${money.format(summary.current_day_energy)} kWh in latest day`,
      tone: summary.trend_pct > 0 ? "warn" : "good",
    },
    {
      label: "Average occupancy",
      value: money.format(summary.avg_occupancy),
      detail: "people per sensor interval",
      tone: "neutral",
    },
    {
      label: "Detected anomalies",
      value: summary.anomaly_count,
      detail: "ranked by severity",
      tone: summary.anomaly_count ? "warn" : "good",
    },
  ];

  qs("#metric-grid").innerHTML = metrics
    .map(
      (metric) => `
        <section class="metric-card ${metric.tone}">
          <p>${metric.label}</p>
          <strong>${metric.value}</strong>
          <span>${metric.detail}</span>
        </section>
      `,
    )
    .join("");
}

function renderBuildingTable(buildings) {
  qs("#building-table").innerHTML = buildings
    .map(
      (building) => `
        <tr>
          <td>
            <button class="link-button" data-building="${building.name}">${building.name}</button>
            <span>${building.type}</span>
          </td>
          <td>${building.avg_energy} kWh</td>
          <td>${building.avg_occupancy}</td>
          <td>${building.energy_per_person}</td>
          <td class="${building.trend_pct > 0 ? "up" : "down"}">${pct(building.trend_pct)}</td>
        </tr>
      `,
    )
    .join("");

  qsa("[data-building]").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedBuilding = button.dataset.building;
      render();
    });
  });
}

function renderChart(hourly) {
  const maxEnergy = Math.max(...hourly.map((row) => row.energy));
  const ticks = hourly.filter((row) => row.hour % 2 === 0);
  qs("#energy-chart").innerHTML = ticks
    .map((row) => {
      const height = Math.max(6, (row.energy / maxEnergy) * 100);
      return `
        <button class="bar" title="${row.hour}:00 - ${row.energy} kWh" style="--h:${height}%">
          <span>${row.hour}</span>
        </button>
      `;
    })
    .join("");
}

function renderAnomalies(anomalies) {
  qs("#anomaly-list").innerHTML = anomalies
    .map((item) => {
      const time = new Date(item.timestamp);
      return `
        <li>
          <div>
            <strong>${item.building}</strong>
            <span>${time.toLocaleString([], { month: "short", day: "numeric", hour: "numeric" })}</span>
          </div>
          <p>${item.reason}</p>
          <em>${item.energy_kwh} kWh / ${item.occupancy} people</em>
        </li>
      `;
    })
    .join("");
}

function renderRecommendations(recommendations) {
  qs("#recommendation-list").innerHTML = recommendations
    .map(
      (item) => `
        <article class="recommendation">
          <div>
            <strong>${item.title}</strong>
            <span>${item.building}</span>
          </div>
          <p>${item.action}</p>
          <footer>
            <b>${item.impact_kwh} kWh</b>
            <span>${item.confidence}% confidence</span>
          </footer>
        </article>
      `,
    )
    .join("");
}

function renderRawSample(rows) {
  const filtered =
    state.selectedBuilding === "All"
      ? rows
      : rows.filter((row) => row.building === state.selectedBuilding);

  qs("#raw-title").textContent =
    state.selectedBuilding === "All" ? "Recent sensor readings" : `Recent readings: ${state.selectedBuilding}`;

  qs("#raw-sample").innerHTML = filtered
    .slice(-8)
    .reverse()
    .map(
      (row) => `
        <tr>
          <td>${new Date(row.timestamp).toLocaleString([], { month: "short", day: "numeric", hour: "numeric" })}</td>
          <td>${row.building}</td>
          <td>${row.occupancy}</td>
          <td>${row.energy_kwh}</td>
          <td>${row.event}</td>
        </tr>
      `,
    )
    .join("");
}

function renderBuildingFilters(buildings) {
  const names = ["All", ...buildings.map((building) => building.name)];
  qs("#building-filters").innerHTML = names
    .map(
      (name) => `
        <button class="${state.selectedBuilding === name ? "active" : ""}" data-filter="${name}">
          ${name}
        </button>
      `,
    )
    .join("");

  qsa("[data-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedBuilding = button.dataset.filter;
      render();
    });
  });
}

function render() {
  const data = state.analytics;
  if (!data) return;

  qs("#updated-at").textContent = `Updated ${new Date(data.generated_at).toLocaleTimeString([], {
    hour: "numeric",
    minute: "2-digit",
  })}`;
  renderMetricCards(data.summary);
  renderBuildingFilters(data.buildings);
  renderBuildingTable(data.buildings);
  renderChart(data.hourly);
  renderAnomalies(data.anomalies);
  renderRecommendations(data.recommendations);
  renderRawSample(data.raw_sample);
}

qs("#refresh-data").addEventListener("click", async () => {
  qs("#refresh-data").disabled = true;
  qs("#refresh-data").textContent = "Refreshing";
  await loadAnalytics(true);
  qs("#refresh-data").disabled = false;
  qs("#refresh-data").textContent = "Regenerate data";
});

loadAnalytics().catch((error) => {
  qs("main").innerHTML = `<section class="error-state"><h2>CampusPulse could not load.</h2><p>${error.message}</p></section>`;
});
