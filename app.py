from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# page config has to come first
st.set_page_config(page_title="Café sales | 2025", page_icon="☕", layout="wide")

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
OUTLET_ORDER = ["Pune", "Jaipur", "Kochi"]
ITEM_ORDER = ["Beverages", "Bakery", "Merchandise"]
OUTLET_COLORS = {"Pune": "#C45C26", "Jaipur": "#2C6E63", "Kochi": "#C4A035"}
OUTLET_EMOJI = {"Pune": "🏛️", "Jaipur": "🏰", "Kochi": "🌊"}
ITEM_EMOJI = {"Beverages": "☕", "Bakery": "🥐", "Merchandise": "🛍️"}

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Playfair+Display:wght@400;500;600;700;800&display=swap');

      /* ── Base ────────────────────────────────────────── */
      .stApp {
        background: linear-gradient(145deg, #f8f3eb 0%, #f0e8db 35%, #efe4d4 70%, #f5eedf 100%);
        color: #2a2118;
      }
      [data-testid="stHeader"] { background: transparent; }

      h1, h2, h3 {
        font-family: 'Playfair Display', Georgia, serif !important;
        color: #2a2118;
      }
      p, span, div, label, small {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      }

      /* ── Sidebar ─────────────────────────────────────── */
      [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a150f 0%, #2c2118 40%, #382a1e 100%);
        border-right: 1px solid rgba(228, 215, 195, 0.15);
      }
      [data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #C45C26, #C4A035, #2C6E63);
      }
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
      [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
      [data-testid="stSidebar"] h2,
      [data-testid="stSidebar"] small,
      [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #e8dccb !important;
      }
      [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        font-weight: 500 !important;
        letter-spacing: 0.3px;
        text-transform: uppercase;
        font-size: 0.7rem !important;
        color: #a89680 !important;
      }

      /* ── Metric Cards ────────────────────────────────── */
      [data-testid="stMetric"] {
        background: rgba(255, 250, 243, 0.75);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(228, 215, 195, 0.6);
        border-radius: 16px;
        padding: 20px 20px 16px 20px;
        box-shadow: 0 4px 24px rgba(42, 33, 24, 0.06), 0 1px 4px rgba(42, 33, 24, 0.04);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      }
      [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(42, 33, 24, 0.12), 0 4px 12px rgba(42, 33, 24, 0.06);
        border-color: rgba(196, 92, 38, 0.3);
      }
      [data-testid="stMetricLabel"] p {
        color: #8a7a6a !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-size: 0.65rem !important;
      }
      [data-testid="stMetricValue"] {
        color: #2a2118 !important;
        font-family: 'Playfair Display', Georgia, serif !important;
        font-weight: 700 !important;
        font-size: 1.7rem !important;
      }
      [data-testid="stMetricDelta"] { color: #6d5c4d !important; }

      /* ── Hero Banner ─────────────────────────────────── */
      .hero-wrapper {
        position: relative;
        margin-bottom: 24px;
      }
      .hero {
        background: linear-gradient(135deg, rgba(255,250,243,0.85) 0%, rgba(255,247,235,0.8) 100%);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid rgba(228, 215, 195, 0.5);
        border-radius: 20px;
        padding: 32px 36px 28px 36px;
        box-shadow: 0 8px 32px rgba(42, 33, 24, 0.08);
        position: relative;
        overflow: hidden;
      }
      .hero::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #C45C26, #e8a862, #C4A035, #2C6E63);
      }
      .hero::after {
        content: '☕';
        position: absolute;
        right: 28px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 5rem;
        opacity: 0.08;
      }
      .hero .kicker {
        color: #C45C26;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        margin: 0 0 8px 0;
        font-family: 'Inter', sans-serif;
      }
      .hero h1 {
        margin: 0 0 10px 0;
        font-size: 2.4rem;
        font-weight: 800;
        line-height: 1.15;
        background: linear-gradient(135deg, #2a2118 0%, #5c4530 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
      .hero .subtitle {
        margin: 0;
        color: #7a6b5d;
        font-size: 0.92rem;
        line-height: 1.5;
        font-weight: 400;
      }

      /* ── Section Dividers ────────────────────────────── */
      .section-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #a89680;
        margin: 32px 0 16px 4px;
        display: flex;
        align-items: center;
        gap: 10px;
      }
      .section-label::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(168,150,128,0.3), transparent);
      }

      /* ── Chart Cards ─────────────────────────────────── */
      [data-testid="stPlotlyChart"] {
        background: rgba(255, 250, 243, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(228, 215, 195, 0.5);
        border-radius: 16px;
        padding: 12px;
        box-shadow: 0 4px 24px rgba(42, 33, 24, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      }
      [data-testid="stPlotlyChart"]:hover {
        box-shadow: 0 8px 32px rgba(42, 33, 24, 0.1);
        border-color: rgba(196, 92, 38, 0.2);
      }

      /* ── Expander ────────────────────────────────────── */
      [data-testid="stExpander"] {
        background: rgba(255, 250, 243, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(228, 215, 195, 0.5);
        border-radius: 16px !important;
        overflow: hidden;
      }

      /* ── Insights Container ──────────────────────────── */
      .insights-card {
        background: linear-gradient(135deg, rgba(255,250,243,0.8) 0%, rgba(255,247,235,0.7) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(228, 215, 195, 0.5);
        border-radius: 16px;
        padding: 24px 28px;
        box-shadow: 0 4px 24px rgba(42, 33, 24, 0.06);
      }
      .insights-card h3 {
        font-size: 1.2rem;
        margin: 0 0 16px 0;
        font-weight: 700;
      }
      .insight-item {
        padding: 14px 16px;
        background: rgba(255, 255, 255, 0.5);
        border-radius: 12px;
        border: 1px solid rgba(228, 215, 195, 0.3);
        transition: all 0.25s ease;
      }
      .insight-item:hover {
        background: rgba(255, 255, 255, 0.8);
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(42, 33, 24, 0.06);
      }
      .insight-label {
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #C45C26;
        margin-bottom: 6px;
        font-family: 'Inter', sans-serif;
      }
      .insight-text {
        font-size: 0.88rem;
        color: #5c4e40;
        line-height: 1.5;
        font-family: 'Inter', sans-serif;
      }

      /* ── Filter Summary Pill ─────────────────────────── */
      .filter-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(196, 92, 38, 0.08);
        border: 1px solid rgba(196, 92, 38, 0.15);
        border-radius: 100px;
        padding: 6px 14px;
        font-size: 0.75rem;
        font-family: 'Inter', sans-serif;
        color: #8a5a32;
        font-weight: 500;
        margin: 2px 3px;
      }
      .filter-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        margin: 6px 0 8px 0;
        align-items: center;
      }

      /* ── Download Button ─────────────────────────────── */
      [data-testid="stDownloadButton"] button {
        background: linear-gradient(135deg, #C45C26 0%, #d4712f 100%) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        letter-spacing: 0.4px;
        padding: 8px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 12px rgba(196, 92, 38, 0.25) !important;
      }
      [data-testid="stDownloadButton"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 24px rgba(196, 92, 38, 0.35) !important;
      }

      /* ── Caption Style ───────────────────────────────── */
      [data-testid="stCaptionContainer"] {
        font-size: 0.78rem !important;
        color: #998a7a !important;
        font-style: italic;
      }

      /* ── Footer ──────────────────────────────────────── */
      .footer {
        text-align: center;
        padding: 20px 0 10px 0;
        margin-top: 32px;
        border-top: 1px solid rgba(228, 215, 195, 0.4);
        font-size: 0.72rem;
        color: #b0a090;
        font-family: 'Inter', sans-serif;
      }

      /* ── Smooth Scrollbar ────────────────────────────── */
      ::-webkit-scrollbar { width: 6px; }
      ::-webkit-scrollbar-track { background: transparent; }
      ::-webkit-scrollbar-thumb {
        background: rgba(168, 150, 128, 0.3);
        border-radius: 3px;
      }
      ::-webkit-scrollbar-thumb:hover { background: rgba(168, 150, 128, 0.5); }

      /* ── Animations ──────────────────────────────────── */
      @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
      }
      [data-testid="stMetric"],
      [data-testid="stPlotlyChart"],
      .insights-card {
        animation: fadeInUp 0.5s ease-out both;
      }
      [data-testid="stMetric"]:nth-child(1) { animation-delay: 0.05s; }
      [data-testid="stMetric"]:nth-child(2) { animation-delay: 0.1s; }
      [data-testid="stMetric"]:nth-child(3) { animation-delay: 0.15s; }
      [data-testid="stMetric"]:nth-child(4) { animation-delay: 0.2s; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    csv_path = Path(__file__).parent / "cafe_clean.csv"
    df = pd.read_csv(csv_path, parse_dates=["Date"])
    if "Month" not in df.columns:
        df["Month"] = df["Date"].dt.month
    if "Weekday" not in df.columns:
        df["Weekday"] = df["Date"].dt.dayofweek
    return df


def inr_millions(rs_thousand):
    # csv stores revenue in Rs thousand
    value = rs_thousand / 1000
    if value >= 1:
        return f"₹{value:,.1f} million"
    return f"₹{rs_thousand:,.0f} thousand"


def polish(fig, height=380, legend_title=None, y_grid=True):
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Inter, Segoe UI, Helvetica, sans-serif", color="#2a2118", size=13),
        title=dict(
            font=dict(size=15, family="Inter, sans-serif", color="#5c4e40"),
            x=0.01,
            xanchor="left",
        ),
        margin=dict(l=8, r=12, t=56, b=8),
        height=height,
        paper_bgcolor="rgba(255,250,243,0)",
        plot_bgcolor="rgba(255,250,243,0)",
        legend_title_text=legend_title or "",
        legend=dict(
            bgcolor="rgba(255,250,243,0.8)",
            bordercolor="rgba(228,215,195,0.4)",
            borderwidth=1,
            font=dict(size=11),
        ),
        coloraxis_showscale=False,
        hoverlabel=dict(
            bgcolor="rgba(42,33,24,0.9)",
            font_color="#fff",
            font_size=12,
            font_family="Inter, sans-serif",
            bordercolor="rgba(255,255,255,0.1)",
        ),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(
        showgrid=y_grid,
        gridcolor="rgba(228, 215, 195, 0.4)",
        gridwidth=1,
        griddash="dot",
        zeroline=False,
    )
    return fig


df = load_data()

# ── Hero ───────────────────────────────────────────────
st.markdown(
    """
    <div class="hero-wrapper">
      <div class="hero">
        <p class="kicker">Daily café sales · Pune · Jaipur · Kochi</p>
        <h1>How the shops did in 2025</h1>
        <p class="subtitle">Revenue in the file is Rs thousand. Totals on this page are shown in millions of rupees.</p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ────────────────────────────────────────────
st.sidebar.markdown(
    """
    <div style="padding: 8px 0 20px 0; border-bottom: 1px solid rgba(228,215,195,0.15); margin-bottom: 20px;">
      <span style="font-size: 1.8rem;">☕</span>
      <span style="font-family: 'Playfair Display', serif; font-size: 1.15rem; font-weight: 700; color: #e8dccb; margin-left: 8px;">Café Analytics</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.caption("Everything starts selected. Change one filter at a time to see what moves.")

picked_outlets = st.sidebar.multiselect(
    "Outlets",
    options=OUTLET_ORDER,
    default=OUTLET_ORDER,
    help="Choose one or more locations to compare.",
)
picked_items = st.sidebar.multiselect(
    "Items",
    options=ITEM_ORDER,
    default=ITEM_ORDER,
    help="Choose the product categories to include.",
)
start_m, end_m = st.sidebar.select_slider(
    "Months",
    options=list(range(1, 13)),
    value=(1, 12),
    format_func=lambda m: MONTHS[m - 1],
)
start_offer, end_offer = st.sidebar.slider(
    "Offer %",
    min_value=0,
    max_value=25,
    value=(0, 25),
    step=5,
    help="Keep rows whose offer is inside this range.",
)
trend_measure = st.sidebar.radio(
    "Monthly chart shows",
    options=["Total revenue", "Average sale"],
    help="Choose total sales or the average value of one record in each month.",
)
offer_item = st.sidebar.selectbox(
    "Compare offers for",
    options=["All selected items"] + [item for item in ITEM_ORDER if item in picked_items],
    help="Offers can behave differently for different product categories.",
)

if not picked_outlets or not picked_items:
    st.warning("Pick at least one outlet and one item. The charts need both.")
    st.stop()

view = df[
    df["Outlet"].isin(picked_outlets)
    & df["Item"].isin(picked_items)
    & df["Month"].between(start_m, end_m)
    & df["Offer"].between(start_offer, end_offer)
].copy()

if view.empty:
    st.info("Nothing matches those filters. Nudge the month or offer range a bit.")
    st.stop()

outlet_totals = view.groupby("Outlet")["Revenue"].sum().reindex(picked_outlets)
top_shop = outlet_totals.idxmax()
full_total = df["Revenue"].sum()
share = view["Revenue"].sum() / full_total

# ── Filter Pills ───────────────────────────────────────
outlets_str = " ".join(
    f'<span class="filter-pill">{OUTLET_EMOJI.get(o, "")} {o}</span>' for o in picked_outlets
)
items_str = " ".join(
    f'<span class="filter-pill">{ITEM_EMOJI.get(i, "")} {i}</span>' for i in picked_items
)
st.markdown(
    f"""
    <div class="filter-bar">
      {outlets_str}
      {items_str}
      <span class="filter-pill">📅 {MONTHS[start_m - 1]}–{MONTHS[end_m - 1]}</span>
      <span class="filter-pill">🏷️ {start_offer}–{end_offer}%</span>
      <span class="filter-pill">📊 {share:.0%} of year</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── KPI Metrics ────────────────────────────────────────
st.markdown('<div class="section-label">Key Numbers</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total revenue", inr_millions(view["Revenue"].sum()))
c2.metric("Average sale row", f"₹{view['Revenue'].mean():,.0f}k", help="Each row is one item at one outlet on one date.")
c3.metric("Records in view", f"{len(view):,}")
c4.metric("Leading outlet", f"{OUTLET_EMOJI.get(top_shop, '')} {top_shop}")

# ── Charts ─────────────────────────────────────────────
st.markdown('<div class="section-label">Revenue Trends</div>', unsafe_allow_html=True)

# Keep one point per month and outlet so each line stays easy to follow.
monthly_groups = view.groupby(["Month", "Outlet"])["Revenue"]
if trend_measure == "Total revenue":
    trend = monthly_groups.sum().rename("Revenue").reset_index()
    trend_title = "📈  Monthly revenue by outlet"
    y_axis_label = "Revenue (Rs thousand)"
else:
    trend = monthly_groups.mean().rename("Revenue").reset_index()
    trend_title = "📈  Average monthly sale by outlet"
    y_axis_label = "Average revenue per record (Rs thousand)"

trend["Period"] = trend["Month"].map(lambda month: MONTHS[month - 1])
fig_month = px.line(
    trend,
    x="Period",
    y="Revenue",
    color="Outlet",
    markers=True,
    color_discrete_map=OUTLET_COLORS,
    category_orders={"Outlet": OUTLET_ORDER, "Period": MONTHS},
    title=trend_title,
    labels={"Period": "Month", "Revenue": y_axis_label},
)
fig_month.update_traces(
    line=dict(width=3),
    marker=dict(size=9, line=dict(width=2, color="#fffaf3")),
)
polish(fig_month, legend_title="Outlet")
fig_month.update_xaxes(showgrid=False, tickangle=0)

by_item = (
    view.groupby("Item", as_index=False)["Revenue"]
    .sum()
    .sort_values("Revenue")
)
by_item["pct"] = by_item["Revenue"] / by_item["Revenue"].sum()
fig_item = px.bar(
    by_item,
    x="Revenue",
    y="Item",
    orientation="h",
    text=by_item["pct"].map(lambda p: f"{p:.0%}"),
    color="Item",
    color_discrete_map={
        "Beverages": "#C45C26",
        "Bakery": "#2C6E63",
        "Merchandise": "#C4A035",
    },
    category_orders={"Item": ITEM_ORDER},
    title="🏆  Which items brought the money in",
    labels={"Revenue": "Revenue (Rs thousand)", "Item": ""},
)
fig_item.update_traces(
    textposition="outside",
    cliponaxis=False,
    showlegend=False,
    marker_line_width=0,
    opacity=0.92,
)
polish(fig_item)

grid = (
    view.pivot_table(index="Outlet", columns="Item", values="Revenue", aggfunc="mean")
    .reindex(index=[o for o in OUTLET_ORDER if o in picked_outlets])
    .reindex(columns=[i for i in ITEM_ORDER if i in picked_items])
)
fig_heat = px.imshow(
    grid,
    text_auto=".0f",
    color_continuous_scale=["#f9f3ec", "#ecc9a0", "#d9884a", "#c45c26"],
    title="🔥  Avg sale by shop × item",
    labels={"x": "", "y": "", "color": "Rs thousand"},
    aspect="auto",
)
fig_heat.update_traces(
    textfont=dict(size=14, family="Inter, sans-serif", color="#2a2118"),
)
polish(fig_heat, height=440, y_grid=False)
fig_heat.update_layout(margin=dict(l=70, r=16, t=72, b=36))

offer_view = view if offer_item == "All selected items" else view[view["Item"] == offer_item]
by_offer = offer_view.groupby("Offer", as_index=False)["Revenue"].mean()
fig_offer = px.bar(
    by_offer,
    x="Offer",
    y="Revenue",
    title="🏷️  Avg row at each offer level",
    labels={"Offer": "Offer %", "Revenue": "Avg revenue (Rs thousand)"},
    color_discrete_sequence=["#2C6E63"],
)
fig_offer.update_traces(marker_line_width=0, opacity=0.88)
fig_offer.update_xaxes(dtick=5)
polish(fig_offer)

by_day = view.groupby("Weekday", as_index=False)["Revenue"].mean()
by_day["DayName"] = by_day["Weekday"].map(lambda d: WEEKDAYS[int(d)])
fig_day = px.bar(
    by_day,
    x="DayName",
    y="Revenue",
    title="📅  Weekdays vs weekends",
    labels={"DayName": "", "Revenue": "Avg revenue (Rs thousand)"},
    color="DayName",
    color_discrete_map={
        "Mon": "#d8c4a8",
        "Tue": "#d8c4a8",
        "Wed": "#d8c4a8",
        "Thu": "#d8c4a8",
        "Fri": "#d8c4a8",
        "Sat": "#C45C26",
        "Sun": "#C45C26",
    },
    category_orders={"DayName": WEEKDAYS},
)
fig_day.update_traces(showlegend=False, marker_line_width=0, opacity=0.9)
polish(fig_day)

# Hover labels and legend clicks stay active without a crowded toolbar.
chart_cfg = {"displaylogo": False, "displayModeBar": False}

left, right = st.columns((1.35, 1), gap="medium")
left.plotly_chart(fig_month, use_container_width=True, config=chart_cfg)
left.caption("One point per month. Hover for exact values — click an outlet in the legend to hide/show its line.")
right.plotly_chart(fig_item, use_container_width=True, config=chart_cfg)
right.caption("The percentage at each bar's end is that category's share of selected revenue.")

st.markdown('<div class="section-label">Deeper Cuts</div>', unsafe_allow_html=True)

a, b, c = st.columns(3, gap="medium")
a.plotly_chart(fig_heat, use_container_width=True, config=chart_cfg)
a.caption("Each cell is an average. Darker = larger average sale row.")
b.plotly_chart(fig_offer, use_container_width=True, config=chart_cfg)
b.caption("Compare offers for one category at a time with the sidebar selector.")
c.plotly_chart(fig_day, use_container_width=True, config=chart_cfg)
c.caption("Bars show average revenue per row; weekends are highlighted in orange.")

# ── Insights ───────────────────────────────────────────
st.markdown('<div class="section-label">What the Data Says</div>', unsafe_allow_html=True)

peak = view.groupby("Month")["Revenue"].sum().idxmax()
top_item = view.groupby("Item")["Revenue"].sum().idxmax()
weekdays_total = view.loc[view["Weekday"] < 5, "Revenue"].mean()
weekend_total = view.loc[view["Weekday"] >= 5, "Revenue"].mean()
weekend_lift = (weekend_total / weekdays_total - 1) if weekdays_total else 0

lift_words = "higher" if weekend_lift >= 0 else "lower"
lift_icon = "📈" if weekend_lift >= 0 else "📉"

st.markdown(
    f"""
    <div class="insights-card">
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
        <div class="insight-item">
          <div class="insight-label">🗓️ Strongest Month</div>
          <div class="insight-text"><strong>{MONTHS[peak - 1]}</strong> has the highest total in the selected period.</div>
        </div>
        <div class="insight-item">
          <div class="insight-label">{ITEM_EMOJI.get(top_item, '📦')} Largest Category</div>
          <div class="insight-text"><strong>{top_item}</strong> contributes the most revenue in this view.</div>
        </div>
        <div class="insight-item">
          <div class="insight-label">{lift_icon} Weekend Pattern</div>
          <div class="insight-text">Average weekend rows are <strong>{abs(weekend_lift):.0%} {lift_words}</strong> than weekday rows.</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Read the offer chart as a comparison, not proof that a discount caused higher sales. "
    "Three deliberately extreme practice rows were removed from the cleaned file. "
    "Hover over charts for exact values. Click a legend label to focus on selected outlets."
)

# ── Data Table ─────────────────────────────────────────
st.markdown('<div class="section-label">Raw Data</div>', unsafe_allow_html=True)

with st.expander("🔍  Peek at the rows"):
    show = view[["Date", "Outlet", "Item", "Offer", "Revenue", "Month"]].sort_values("Date")
    st.download_button(
        "⬇️  Download this slice as CSV",
        data=show.to_csv(index=False).encode("utf-8"),
        file_name="cafe_sales_filtered.csv",
        mime="text/csv",
    )
    st.dataframe(
        show,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "Revenue": st.column_config.NumberColumn("Revenue (Rs thousand)", format="%.1f"),
            "Offer": st.column_config.NumberColumn("Offer %"),
        },
    )

# ── Footer ─────────────────────────────────────────────
st.markdown(
    """
    <div class="footer">
      Made with ☕ and Streamlit · Café Sales Dashboard 2025
    </div>
    """,
    unsafe_allow_html=True,
)
