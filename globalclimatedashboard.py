import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Climate Events Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

  .main-title {
    font-size: 52px;
    font-weight: 700;
    color: #1a3a5c;
    line-height: 1.1;
    margin-bottom: 4px;
  }
  .main-subtitle {
    font-size: 16px;
    color: #6b7c93;
    margin-bottom: 0;
  }

  /* KPI cards */
  .kpi-container {
    background: linear-gradient(135deg, #f0f7ff 0%, #e8f4f8 100%);
    border-radius: 16px;
    padding: 20px 24px;
    border: 1px solid #d0e8f5;
    text-align: center;
    height: 100%;
  }
  .kpi-label {
    font-size: 12px;
    font-weight: 600;
    color: #6b7c93;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
  }
  .kpi-value {
    font-size: 32px;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 4px;
  }
  .kpi-sub {
    font-size: 12px;
    color: #6b7c93;
  }

  /* Section headers */
  .section-header {
    font-size: 22px;
    font-weight: 700;
    color: #1a3a5c;
    margin-top: 8px;
    margin-bottom: 4px;
  }
  .section-divider {
    border: none;
    border-top: 2px solid #e2eaf3;
    margin-bottom: 20px;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: #0f2742;
  }
  [data-testid="stSidebar"] * { color: #c8dff5 !important; }
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stMultiSelect label,
  [data-testid="stSidebar"] .stSlider label { color: #7ab3de !important; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.06em; }

  /* Insight box */
  .insight-box {
    background: #fff8e6;
    border-left: 4px solid #f5a623;
    border-radius: 0 12px 12px 0;
    padding: 16px 20px;
    margin-top: 8px;
  }
  .insight-box p { margin: 0; font-size: 14px; color: #5a4a1a; line-height: 1.6; }

  /* Tab content */
  [data-testid="stTab"] { font-weight: 600; font-size: 14px; }

  div[data-testid="metric-container"] {
    background: #f0f7ff;
    border: 1px solid #d0e8f5;
    border-radius: 12px;
    padding: 12px 16px;
  }
</style>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────────────────────
COUNTRY_ISO3 = {
    "Afghanistan": "AFG", "Albania": "ALB", "Algeria": "DZA", "Argentina": "ARG",
    "Australia": "AUS", "Austria": "AUT", "Bangladesh": "BGD", "Belgium": "BEL",
    "Brazil": "BRA", "Canada": "CAN", "Chile": "CHL", "China": "CHN",
    "Colombia": "COL", "Czech Republic": "CZE", "Denmark": "DNK", "Egypt": "EGY",
    "Finland": "FIN", "France": "FRA", "Germany": "DEU", "Greece": "GRC",
    "Hungary": "HUN", "India": "IND", "Indonesia": "IDN", "Iraq": "IRQ",
    "Ireland": "IRL", "Israel": "ISR", "Italy": "ITA", "Japan": "JPN",
    "Kazakhstan": "KAZ", "Malaysia": "MYS", "Mexico": "MEX", "Netherlands": "NLD",
    "New Zealand": "NZL", "Nigeria": "NGA", "Pakistan": "PAK", "Peru": "PER",
    "Philippines": "PHL", "Poland": "POL", "Portugal": "PRT", "Qatar": "QAT",
    "Romania": "ROU", "Russia": "RUS", "Saudi Arabia": "SAU", "Singapore": "SGP",
    "South Africa": "ZAF", "South Korea": "KOR", "Sweden": "SWE",
    "Switzerland": "CHE", "Thailand": "THA", "Turkey": "TUR", "UAE": "ARE",
    "United Kingdom": "GBR", "United States": "USA", "Vietnam": "VNM",
}

@st.cache_data
def load_data():
    df = pd.read_csv("global_climate_events_economic_impact_2020_2025.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["aid_efficiency"] = (
        df["international_aid_million_usd"] / df["economic_impact_million_usd"].replace(0, np.nan)
    ).fillna(0).round(4)
    df["iso3"] = df["country"].map(COUNTRY_ISO3)
    return df

df = load_data()

# ── Color palette ──────────────────────────────────────────────────────────────
EVENT_COLORS = {
    "Tsunami":          "#1e6091",
    "Hurricane":        "#2a9d8f",
    "Drought":          "#e9c46a",
    "Heatwave":         "#f4a261",
    "Wildfire":         "#e76f51",
    "Cold Wave":        "#90e0ef",
    "Earthquake":       "#8d99ae",
    "Landslide":        "#6d4c41",
    "Hailstorm":        "#a8dadc",
    "Volcanic Eruption":"#d62828",
    "Flood":            "#457b9d",
    "Tornado":          "#7b2d8b",
}

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌍 Climate Dashboard")
    st.markdown("---")

    st.markdown("### Filters")

    year_range = st.slider(
        "Year range",
        int(df["year"].min()), int(df["year"].max()),
        (int(df["year"].min()), int(df["year"].max()))
    )

    all_types = sorted(df["event_type"].unique())
    selected_types = st.multiselect(
        "Event types",
        options=all_types,
        default=all_types,
    )

    all_countries = ["All countries"] + sorted(df["country"].unique())
    selected_country = st.selectbox("Country", all_countries)

    sev_range = st.slider("Severity level", 1, 9, (1, 9))

    st.markdown("---")
    st.markdown("### Color metric")
    map_metric = st.radio(
        "World map shows",
        ["Economic impact (M USD)", "Deaths", "Affected population"],
        index=0
    )

    st.markdown("---")
    st.caption("Data: Global Climate Events 2020–2025 · 3,000 records · 51 countries")

# ── Apply filters ──────────────────────────────────────────────────────────────
mask = (
    df["year"].between(*year_range) &
    df["event_type"].isin(selected_types) &
    df["severity"].between(*sev_range)
)
if selected_country != "All countries":
    mask &= df["country"] == selected_country

fdf = df[mask].copy()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(
    "<p class='main-title'>🌪 Global Climate Events</p>"
    "<p class='main-subtitle'>Economic impact & humanitarian analysis · 2020–2025</p>",
    unsafe_allow_html=True
)
st.markdown("---")

# ── KPI Row ────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)

total_events    = len(fdf)
total_deaths    = int(fdf["deaths"].sum())
total_econ      = fdf["economic_impact_million_usd"].sum()
avg_response    = fdf["response_time_hours"].mean()
total_affected  = int(fdf["affected_population"].sum())
total_aid       = fdf["international_aid_million_usd"].sum()

def kpi(col, label, value, sub, color):
    col.markdown(
        f"<div class='kpi-container'>"
        f"<div class='kpi-label'>{label}</div>"
        f"<div class='kpi-value' style='color:{color}'>{value}</div>"
        f"<div class='kpi-sub'>{sub}</div>"
        f"</div>",
        unsafe_allow_html=True
    )

kpi(k1, "Total Events",        f"{total_events:,}",                    "climate events",            "#1a3a5c")
kpi(k2, "Total Deaths",        f"{total_deaths:,}",                    "fatalities recorded",        "#c0392b")
kpi(k3, "Economic Impact",     f"${total_econ:,.0f}M",                 "USD millions",               "#e67e22")
kpi(k4, "Avg Response Time",   f"{avg_response:.0f} hrs",              "per event",                  "#16a085")
kpi(k5, "Affected Population", f"{total_affected/1e6:.1f}M",           "people affected",            "#8e44ad")
kpi(k6, "International Aid",   f"${total_aid:,.0f}M",                  "USD millions received",      "#27ae60")

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview", "🌍 Geography", "🔬 Analysis", "📋 Data Explorer"
])

# ─────────────────────────────────────────────────────
# TAB 1 · OVERVIEW
# ─────────────────────────────────────────────────────
with tab1:

    # Row 1: Line + Donut
    c1, c2 = st.columns([2, 1])

    with c1:
        st.markdown("<p class='section-header'>Event frequency over time</p>", unsafe_allow_html=True)
        trend = (
            fdf.groupby(["year", "event_type"])
            .size()
            .reset_index(name="count")
        )
        fig_line = px.line(
            trend, x="year", y="count", color="event_type",
            color_discrete_map=EVENT_COLORS,
            markers=True,
            labels={"year": "Year", "count": "Number of events", "event_type": "Event type"},
        )
        fig_line.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            legend_title_text="",
            font_family="Space Grotesk",
            height=340,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        fig_line.update_xaxes(showgrid=False)
        fig_line.update_yaxes(gridcolor="#e2eaf3")
        st.plotly_chart(fig_line, use_container_width=True)

    with c2:
        st.markdown("<p class='section-header'>Event type share</p>", unsafe_allow_html=True)
        pie_data = fdf["event_type"].value_counts().reset_index()
        pie_data.columns = ["event_type", "count"]
        fig_pie = px.pie(
            pie_data, names="event_type", values="count",
            color="event_type", color_discrete_map=EVENT_COLORS,
            hole=0.45,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label",
                              textfont_size=10)
        fig_pie.update_layout(
            showlegend=False,
            font_family="Space Grotesk",
            height=340,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Row 2: Economic impact bar + Heatmap
    c3, c4 = st.columns([1, 1])

    with c3:
        st.markdown("<p class='section-header'>Economic impact by country (top 15)</p>", unsafe_allow_html=True)
        top_countries = (
            fdf.groupby("country")["economic_impact_million_usd"]
            .sum()
            .nlargest(15)
            .reset_index()
            .sort_values("economic_impact_million_usd")
        )
        fig_bar = px.bar(
            top_countries, x="economic_impact_million_usd", y="country",
            orientation="h",
            color="economic_impact_million_usd",
            color_continuous_scale=["#d0e8f5", "#1a3a5c"],
            labels={"economic_impact_million_usd": "USD millions", "country": ""},
        )
        fig_bar.update_coloraxes(showscale=False)
        fig_bar.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_family="Space Grotesk",
            height=380,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        fig_bar.update_xaxes(gridcolor="#e2eaf3")
        fig_bar.update_yaxes(showgrid=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    with c4:
        st.markdown("<p class='section-header'>Seasonal heatmap — month × event type</p>", unsafe_allow_html=True)
        heat = (
            fdf.groupby(["event_type", "month"])
            .size()
            .reset_index(name="count")
        )
        heat_pivot = heat.pivot(index="event_type", columns="month", values="count").fillna(0)
        month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        heat_pivot.columns = [month_names[m-1] for m in heat_pivot.columns]

        fig_heat = px.imshow(
            heat_pivot,
            color_continuous_scale=["#f0f7ff", "#1e6091"],
            aspect="auto",
            labels=dict(color="Events"),
        )
        fig_heat.update_layout(
            font_family="Space Grotesk",
            height=380,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Month",
            yaxis_title="",
            coloraxis_colorbar=dict(thickness=10, len=0.6),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # Insight
    top_type = fdf["event_type"].value_counts().idxmax()
    top_country_name = fdf.groupby("country")["economic_impact_million_usd"].sum().idxmax()
    st.markdown(
        f"<div class='insight-box'>"
        f"<p>💡 <strong>Key insight:</strong> Within the selected filters, <strong>{top_type}</strong> is the most frequent "
        f"disaster type. <strong>{top_country_name}</strong> bears the highest total economic impact. "
        f"The seasonal heatmap above reveals which months see clustered activity — useful for pre-positioning aid resources.</p>"
        f"</div>",
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────────────
# TAB 2 · GEOGRAPHY
# ─────────────────────────────────────────────────────
with tab2:

    metric_map = {
        "Economic impact (M USD)": ("economic_impact_million_usd", "Economic impact (M USD)"),
        "Deaths":                  ("deaths",                       "Deaths"),
        "Affected population":     ("affected_population",          "Affected population"),
    }
    col_name, col_label = metric_map[map_metric]

    country_agg = (
        fdf.groupby(["country", "iso3"])
        .agg(
            total_value=(col_name, "sum"),
            total_events=("event_id", "count"),
            total_deaths=("deaths", "sum"),
            total_economic_impact=("economic_impact_million_usd", "sum"),
        )
        .reset_index()
    )

    st.markdown(f"<p class='section-header'>World map — {col_label} by country</p>", unsafe_allow_html=True)

    fig_map = px.choropleth(
        country_agg,
        locations="iso3",
        locationmode="ISO-3",
        color="total_value",
        hover_name="country",
        hover_data={
            "iso3": False,
            "total_events": True,
            "total_deaths": True,
            "total_economic_impact": ":.1f",
        },
        color_continuous_scale=["#e8f4f8", "#1a3a5c"],
        labels={
            "total_value": col_label,
            "total_events": "Events",
            "total_deaths": "Deaths",
            "total_economic_impact": "Economic impact (M USD)",
        },
    )
    fig_map.update_layout(
        geo=dict(showframe=False, showcoastlines=True, coastlinecolor="#ccc",
                 bgcolor="rgba(0,0,0,0)", projection_type="natural earth",
                 showland=True, landcolor="#f5f5f5",
                 showocean=True, oceancolor="#eaf4fb",
                 showcountries=True, countrycolor="#d0d0d0"),
        paper_bgcolor="rgba(0,0,0,0)",
        font_family="Space Grotesk",
        margin=dict(l=0, r=0, t=0, b=0),
        height=480,
        coloraxis_colorbar=dict(thickness=12, len=0.5, title=col_label),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Event scatter map
    st.markdown("<p class='section-header'>Individual event locations</p>", unsafe_allow_html=True)
    fig_scatter_map = px.scatter_geo(
        fdf,
        lat="latitude", lon="longitude",
        color="event_type",
        size="economic_impact_million_usd",
        hover_name="country",
        hover_data={"event_type": True, "severity": True,
                    "deaths": True, "economic_impact_million_usd": ":.2f",
                    "latitude": False, "longitude": False},
        color_discrete_map=EVENT_COLORS,
        size_max=20,
        opacity=0.7,
        labels={"economic_impact_million_usd": "Economic impact (M USD)", "event_type": "Event type"},
    )
    fig_scatter_map.update_layout(
        geo=dict(showframe=False, showcoastlines=True, coastlinecolor="#ccc",
                 bgcolor="rgba(0,0,0,0)", projection_type="natural earth"),
        paper_bgcolor="rgba(0,0,0,0)",
        font_family="Space Grotesk",
        legend_title_text="Event type",
        margin=dict(l=0, r=0, t=0, b=0),
        height=420,
    )
    st.plotly_chart(fig_scatter_map, use_container_width=True)

# ─────────────────────────────────────────────────────
# TAB 3 · ANALYSIS
# ─────────────────────────────────────────────────────
with tab3:

    # Row 1: Bubble + Scatter
    c5, c6 = st.columns(2)

    with c5:
        st.markdown("<p class='section-header'>Severity vs. economic impact</p>", unsafe_allow_html=True)
        fig_bubble = px.scatter(
            fdf,
            x="severity",
            y="economic_impact_million_usd",
            size="deaths",
            color="event_type",
            hover_name="country",
            hover_data={"deaths": True, "severity": True,
                        "economic_impact_million_usd": ":.2f"},
            color_discrete_map=EVENT_COLORS,
            size_max=30,
            opacity=0.75,
            labels={
                "severity": "Severity (1–9)",
                "economic_impact_million_usd": "Economic impact (M USD)",
                "event_type": "Event type",
            },
        )
        fig_bubble.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_family="Space Grotesk",
            height=360,
            margin=dict(l=0, r=0, t=10, b=0),
            legend_title_text="",
        )
        fig_bubble.update_xaxes(gridcolor="#e2eaf3", dtick=1)
        fig_bubble.update_yaxes(gridcolor="#e2eaf3")
        st.plotly_chart(fig_bubble, use_container_width=True)
        st.caption("Bubble size = deaths. Higher severity doesn't always mean higher economic impact.")

    with c6:
        st.markdown("<p class='section-header'>Response time vs. casualties</p>", unsafe_allow_html=True)
        fig_resp = px.scatter(
            fdf,
            x="response_time_hours",
            y="total_casualties",
            color="event_type",
            trendline="ols",
            trendline_scope="overall",
            trendline_color_override="#c0392b",
            hover_name="country",
            color_discrete_map=EVENT_COLORS,
            opacity=0.65,
            labels={
                "response_time_hours": "Response time (hours)",
                "total_casualties": "Total casualties",
                "event_type": "Event type",
            },
        )
        fig_resp.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_family="Space Grotesk",
            height=360,
            margin=dict(l=0, r=0, t=10, b=0),
            legend_title_text="",
        )
        fig_resp.update_xaxes(gridcolor="#e2eaf3")
        fig_resp.update_yaxes(gridcolor="#e2eaf3")
        st.plotly_chart(fig_resp, use_container_width=True)
        st.caption("Red line = overall trend. Positive slope would suggest delayed response worsens outcomes.")

    # Row 2: Box + Aid efficiency
    c7, c8 = st.columns(2)

    with c7:
        st.markdown("<p class='section-header'>Casualty distribution by event type</p>", unsafe_allow_html=True)
        fig_box = px.box(
            fdf,
            x="event_type",
            y="total_casualties",
            color="event_type",
            color_discrete_map=EVENT_COLORS,
            points="outliers",
            labels={"event_type": "", "total_casualties": "Total casualties"},
        )
        fig_box.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_family="Space Grotesk",
            height=360,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            xaxis_tickangle=-35,
        )
        fig_box.update_yaxes(gridcolor="#e2eaf3")
        st.plotly_chart(fig_box, use_container_width=True)
        st.caption("Boxes show median and IQR. Dots are outlier events.")

    with c8:
        st.markdown("<p class='section-header'>Aid efficiency by country (top 15)</p>", unsafe_allow_html=True)
        aid_df = (
            fdf[fdf["economic_impact_million_usd"] > 0]
            .groupby("country")
            .agg(
                total_aid=("international_aid_million_usd", "sum"),
                total_impact=("economic_impact_million_usd", "sum"),
            )
            .assign(efficiency=lambda x: (x["total_aid"] / x["total_impact"] * 100).round(2))
            .nlargest(15, "efficiency")
            .reset_index()
            .sort_values("efficiency")
        )
        fig_aid = px.bar(
            aid_df, x="efficiency", y="country",
            orientation="h",
            color="efficiency",
            color_continuous_scale=["#d5f5e3", "#1e8449"],
            labels={"efficiency": "Aid / Impact (%)", "country": ""},
            hover_data={"total_aid": ":.1f", "total_impact": ":.1f"},
        )
        fig_aid.update_coloraxes(showscale=False)
        fig_aid.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_family="Space Grotesk",
            height=360,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        fig_aid.update_xaxes(gridcolor="#e2eaf3")
        fig_aid.update_yaxes(showgrid=False)
        st.plotly_chart(fig_aid, use_container_width=True)
        st.caption("Aid efficiency = international aid ÷ economic impact × 100. Higher = better coverage.")

    # Infrastructure damage by severity
    st.markdown("<p class='section-header'>Infrastructure damage score vs. severity</p>", unsafe_allow_html=True)
    infra = fdf.groupby(["severity", "event_type"])["infrastructure_damage_score"].mean().reset_index()
    fig_infra = px.line(
        infra, x="severity", y="infrastructure_damage_score",
        color="event_type",
        markers=True,
        color_discrete_map=EVENT_COLORS,
        labels={
            "severity": "Severity level (1–9)",
            "infrastructure_damage_score": "Avg infrastructure damage score",
            "event_type": "Event type",
        },
    )
    fig_infra.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_family="Space Grotesk",
        height=320,
        margin=dict(l=0, r=0, t=10, b=0),
        legend_title_text="",
    )
    fig_infra.update_xaxes(showgrid=False, dtick=1)
    fig_infra.update_yaxes(gridcolor="#e2eaf3")
    st.plotly_chart(fig_infra, use_container_width=True)

    # Insight
    best_aid_country = aid_df.sort_values("efficiency", ascending=False).iloc[0]["country"] if len(aid_df) > 0 else "N/A"
    highest_casualties = fdf.groupby("event_type")["total_casualties"].median().idxmax()
    st.markdown(
        f"<div class='insight-box'>"
        f"<p>💡 <strong>Analysis insight:</strong> <strong>{highest_casualties}</strong> events show the highest "
        f"median casualties. <strong>{best_aid_country}</strong> receives the most proportional international aid "
        f"relative to its economic impact — suggesting effective aid channeling. Consider whether high-severity "
        f"events in your selected filters are receiving adequate response.</p>"
        f"</div>",
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────────────
# TAB 4 · DATA EXPLORER
# ─────────────────────────────────────────────────────
with tab4:

    st.markdown("<p class='section-header'>Top 10 deadliest events (filtered)</p>", unsafe_allow_html=True)
    top10 = (
        fdf.nlargest(10, "deaths")[
            ["event_id", "date", "country", "event_type", "severity",
             "deaths", "injuries", "economic_impact_million_usd",
             "affected_population", "response_time_hours"]
        ]
        .rename(columns={
            "event_id": "Event ID",
            "date": "Date",
            "country": "Country",
            "event_type": "Event type",
            "severity": "Severity",
            "deaths": "Deaths",
            "injuries": "Injuries",
            "economic_impact_million_usd": "Economic impact (M USD)",
            "affected_population": "Affected population",
            "response_time_hours": "Response time (hrs)",
        })
    )
    st.dataframe(top10, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("<p class='section-header'>Full dataset explorer</p>", unsafe_allow_html=True)

    search_col, sort_col, sort_dir_col = st.columns([2, 2, 1])
    with search_col:
        search_text = st.text_input("Search by country or event type", placeholder="e.g. Japan, Flood…")
    with sort_col:
        sort_by = st.selectbox(
            "Sort by",
            ["date", "deaths", "economic_impact_million_usd", "severity", "affected_population"],
        )
    with sort_dir_col:
        sort_asc = st.radio("Order", ["Desc", "Asc"], horizontal=True) == "Asc"

    display_df = fdf.copy()
    if search_text:
        mask_search = (
            display_df["country"].str.contains(search_text, case=False, na=False) |
            display_df["event_type"].str.contains(search_text, case=False, na=False)
        )
        display_df = display_df[mask_search]

    display_df = display_df.sort_values(sort_by, ascending=sort_asc)

    show_cols = [
        "event_id", "date", "country", "event_type", "year", "month",
        "severity", "duration_days", "affected_population", "deaths",
        "injuries", "economic_impact_million_usd",
        "infrastructure_damage_score", "response_time_hours",
        "international_aid_million_usd", "total_casualties",
        "impact_per_capita", "aid_percentage", "aid_efficiency",
    ]

    st.dataframe(
        display_df[show_cols].reset_index(drop=True),
        use_container_width=True,
        height=420,
        column_config={
            "economic_impact_million_usd": st.column_config.NumberColumn("Econ. impact (M USD)", format="$%.2f"),
            "international_aid_million_usd": st.column_config.NumberColumn("Intl. aid (M USD)", format="$%.2f"),
            "aid_efficiency": st.column_config.ProgressColumn("Aid efficiency", min_value=0, max_value=1, format="%.3f"),
            "severity": st.column_config.NumberColumn("Severity", format="%d ⚡"),
        },
        hide_index=True,
    )

    st.caption(f"Showing {len(display_df):,} of {len(fdf):,} filtered records.")

    col_dl1, col_dl2 = st.columns([1, 5])
    with col_dl1:
        csv_data = display_df[show_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇ Download CSV",
            data=csv_data,
            file_name="climate_events_filtered.csv",
            mime="text/csv",
        )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """
    <div style='text-align:center; padding: 16px 0 8px;'>
        <p style='color:#6b7c93; font-size:13px; margin-bottom:6px;'>
            🌍 Global Climate Events Dashboard &nbsp;·&nbsp; Built with Streamlit &amp; Plotly &nbsp;·&nbsp; 2020–2025
        </p>
        <p style='font-size:13px; margin: 0;'>
            <span style='color:#6b7c93;'>Data source: </span>
            <a href='https://www.kaggle.com/datasets/waqi786/climate-change-impact-on-agriculture'
               target='_blank'
               style='color:#1a3a5c; font-weight:600; text-decoration:none;'>
                🌍 Climate Change Impact on Agriculture 🌱
            </a>
            <span style='color:#6b7c93;'> &nbsp;·&nbsp; via Kaggle</span>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)