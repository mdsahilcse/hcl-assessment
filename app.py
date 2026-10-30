from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# page config has to come first
st.set_page_config(page_title="Café sales | 2025", page_icon="☕", layout="wide")

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
OUTLET_ORDER = ["Pune", "Jaipur", "Kochi"]
ITEM_ORDER = ["Beverages", "Bakery", "Merchandise"]
OUTLET_COLORS = {"Pune": "#C45C26", "Jaipur": "#2C6E63", "Kochi": "#C4A035"}

st.markdown(
    """
    <style>
      .stApp { background: #f4efe6; color: #2a2118; }
      [data-testid="stHeader"] { background: transparent; }
      h1 { font-family: Georgia, "Times New Roman", serif; color: #2a2118; }
      [data-testid="stSidebar"] { background: #2c2118; }
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
      [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
      [data-testid="stSidebar"] h2,
      [data-testid="stSidebar"] small,
      [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #e8dccb !important;
      }
      [data-testid="stMetric"] {
        background: #fffaf3;
        border: 1px solid #e4d7c3;
        border-radius: 12px;
        padding: 12px 16px;
      }
      [data-testid="stMetricLabel"] p { color: #6d5c4d !important; }
      [data-testid="stMetricValue"] { color: #2a2118 !important; }
      [data-testid="stMetricDelta"] { color: #6d5c4d !important; }
      .hero {
        background: #fffaf3;
        border: 1px solid #e4d7c3;
        border-radius: 14px;
        padding: 18px 22px 14px 22px;
        margin-bottom: 12px;
      }
      .hero .kicker { color: #8a5a32; font-size: 0.85rem; margin: 0; }
      .hero h1 { margin: 4px 0 6px 0; font-size: 2.1rem; }
      .hero p { margin: 0; color: #5c4e40; }
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
        font=dict(family="Segoe UI, Helvetica, sans-serif", color="#2a2118", size=13),
        title=dict(font=dict(size=16), x=0.01, xanchor="left"),
        margin=dict(l=8, r=12, t=52, b=8),
        height=height,
        paper_bgcolor="#fffaf3",
        plot_bgcolor="#fffaf3",
        legend_title_text=legend_title or "",
        coloraxis_showscale=False,
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(
        showgrid=y_grid,
        gridcolor="#eadfce",
        zeroline=False,
    )
    return fig


df = load_data()

st.markdown(
    """
    <div class="hero">
      <p class="kicker">Daily café sales · Pune · Jaipur · Kochi</p>
      <h1>How the shops did in 2025</h1>
      <p>Revenue in the file is Rs thousand. Totals on this page are shown in millions of rupees.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.header("Make it your view")
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
trend_detail = st.sidebar.radio(
    "Trend detail",
    options=["Month", "Week", "Day"],
    horizontal=True,
    help="Choose how much detail to show in the sales trend.",
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

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total revenue", inr_millions(view["Revenue"].sum()))
c2.metric("Average sale row", f"₹{view['Revenue'].mean():,.0f}k", help="Each row is one item at one outlet on one date.")
c3.metric("Records in view", f"{len(view):,}")
c4.metric("Leading outlet", top_shop)

st.caption(
    f"Showing {MONTHS[start_m - 1]}–{MONTHS[end_m - 1]}  ·  "
    f"{len(picked_outlets)} outlet(s), {len(picked_items)} item(s)  ·  "
    f"offers {start_offer}–{end_offer}%  ·  "
    f"{share:.0%} of the full year  ·  "
    f"{top_shop} made ₹{outlet_totals[top_shop] / 1000:,.1f} million"
)

# --- charts ---
# Group dates at the level chosen in the sidebar. Month labels stay readable;
# weeks and days retain real dates so Plotly can format and zoom the axis.
if trend_detail == "Month":
    trend = view.groupby(["Month", "Outlet"], as_index=False)["Revenue"].sum()
    trend["Period"] = trend["Month"].map(lambda month: MONTHS[month - 1])
    period_order = {"Period": MONTHS}
    trend_title = "Revenue by month"
elif trend_detail == "Week":
    trend = view.assign(Period=view["Date"].dt.to_period("W").dt.start_time)
    trend = trend.groupby(["Period", "Outlet"], as_index=False)["Revenue"].sum()
    period_order = {}
    trend_title = "Revenue by week"
else:
    trend = view.groupby(["Date", "Outlet"], as_index=False)["Revenue"].sum()
    trend = trend.rename(columns={"Date": "Period"})
    period_order = {}
    trend_title = "Revenue by day"

fig_month = px.line(
    trend.sort_values("Period"),
    x="Period",
    y="Revenue",
    color="Outlet",
    markers=trend_detail == "Month",
    color_discrete_map=OUTLET_COLORS,
    category_orders={"Outlet": OUTLET_ORDER, **period_order},
    title=trend_title,
    labels={"Period": "", "Revenue": "Revenue (Rs thousand)"},
)
fig_month.update_traces(line=dict(width=2.5), marker=dict(size=7))
polish(fig_month, legend_title="Outlet")

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
    title="Which items brought the money in",
    labels={"Revenue": "Revenue (Rs thousand)", "Item": ""},
)
fig_item.update_traces(textposition="outside", cliponaxis=False, showlegend=False)
polish(fig_item)

grid = (
    view.pivot_table(index="Outlet", columns="Item", values="Revenue", aggfunc="mean")
    .reindex(index=[o for o in OUTLET_ORDER if o in picked_outlets])
    .reindex(columns=[i for i in ITEM_ORDER if i in picked_items])
)
fig_heat = px.imshow(
    grid,
    text_auto=".0f",
    color_continuous_scale=["#f3eadb", "#e7b07a", "#c45c26"],
    title="Average row (Rs thousand) by shop and item",
    labels={"x": "", "y": "", "color": "Rs thousand"},
    aspect="auto",
)
polish(fig_heat, height=440, y_grid=False)
fig_heat.update_layout(margin=dict(l=70, r=16, t=72, b=36))

offer_view = view if offer_item == "All selected items" else view[view["Item"] == offer_item]
by_offer = offer_view.groupby("Offer", as_index=False)["Revenue"].mean()
fig_offer = px.bar(
    by_offer,
    x="Offer",
    y="Revenue",
    title="Average row at each offer level",
    labels={"Offer": "Offer %", "Revenue": "Avg revenue (Rs thousand)"},
    color_discrete_sequence=["#2C6E63"],
)
fig_offer.update_xaxes(dtick=5)
polish(fig_offer)

by_day = view.groupby("Weekday", as_index=False)["Revenue"].mean()
by_day["DayName"] = by_day["Weekday"].map(lambda d: WEEKDAYS[int(d)])
fig_day = px.bar(
    by_day,
    x="DayName",
    y="Revenue",
    title="Weekdays vs weekends",
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
fig_day.update_traces(showlegend=False)
polish(fig_day)

# Keep the compact Plotly toolbar available for zoom, reset, and image download.
chart_cfg = {
    "displaylogo": False,
    "displayModeBar": "hover",
    "modeBarButtonsToAdd": ["select2d", "lasso2d"],
    "toImageButtonOptions": {"format": "png", "filename": "cafe_sales_chart", "scale": 2},
}

left, right = st.columns((1.35, 1), gap="medium")
left.plotly_chart(fig_month, use_container_width=True, config=chart_cfg)
left.caption("Follow the lines across months, weeks, or days. Hover for exact values; use the toolbar to zoom or save an image.")
right.plotly_chart(fig_item, use_container_width=True, config=chart_cfg)
right.caption("The percentage at the end of each bar is that category's share of the selected revenue.")

a, b, c = st.columns(3, gap="medium")
a.plotly_chart(fig_heat, use_container_width=True, config=chart_cfg)
a.caption("Each cell is an average. Darker cells mean a larger average sale row.")
b.plotly_chart(fig_offer, use_container_width=True, config=chart_cfg)
b.caption("Compare offers for one category at a time with the sidebar selector.")
c.plotly_chart(fig_day, use_container_width=True, config=chart_cfg)
c.caption("Bars show average revenue per row; weekends are highlighted in orange.")

# Turn the current selection into a short, plain-language reading guide.
peak = view.groupby("Month")["Revenue"].sum().idxmax()
top_item = view.groupby("Item")["Revenue"].sum().idxmax()
weekdays_total = view.loc[view["Weekday"] < 5, "Revenue"].mean()
weekend_total = view.loc[view["Weekday"] >= 5, "Revenue"].mean()
weekend_lift = (weekend_total / weekdays_total - 1) if weekdays_total else 0

with st.container(border=True):
    st.subheader("A quick read of this selection")
    notes = st.columns(3)
    notes[0].write(f"**Strongest month**\n\n{MONTHS[peak - 1]} has the highest total in the selected period.")
    notes[1].write(f"**Largest category**\n\n{top_item} contributes the most revenue in this view.")
    lift_words = "higher" if weekend_lift >= 0 else "lower"
    notes[2].write(f"**Weekend pattern**\n\nAverage weekend rows are {abs(weekend_lift):.0%} {lift_words} than weekday rows.")

st.caption(
    "Read the offer chart as a comparison, not proof that a discount caused higher sales. "
    "Three deliberately extreme practice rows were removed from the cleaned file. "
    "Use the chart toolbar to zoom, select points, reset, or save a PNG."
)

with st.expander("Peek at the rows"):
    show = view[["Date", "Outlet", "Item", "Offer", "Revenue", "Month"]].sort_values("Date")
    st.download_button(
        "Download this slice as CSV",
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
