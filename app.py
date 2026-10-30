"""Explore the café's 2025 sales with clear filters and one chart at a time."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Café sales | 2025", page_icon="☕", layout="wide")

# A light, quiet palette keeps the charts and labels easy to read.
COLORS = {
    "Pune": "#397D9B",       # blue
    "Jaipur": "#A84F75",     # pink
    "Kochi": "#916B08",      # golden yellow
}
ITEM_COLORS = {
    "Beverages": "#397D9B",
    "Bakery": "#A84F75",
    "Merchandise": "#916B08",
}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
OUTLETS = ["Pune", "Jaipur", "Kochi"]
ITEMS = ["Beverages", "Bakery", "Merchandise"]

st.markdown(
    """
    <style>
    .stApp { background: #F6F9FC; color: #243746; }
    [data-testid="stHeader"] { background: transparent; }
    h1, h2, h3 { color: #243746; letter-spacing: -0.02em; }
    h1 { font-size: 2.25rem; }
    [data-testid="stSidebar"] { background: #EDF3F9; }
    [data-testid="stCaptionContainer"] { color: #5D7180; }
    [data-testid="stTabs"] button { font-weight: 600; }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #275F78; border-bottom-color: #397D9B;
    }
    [data-testid="stMetric"] {
        background: #FFFFFF; border: 1px solid #DCE6EF;
        border-radius: 12px; padding: 15px 17px;
    }
    [data-testid="stPlotlyChart"] {
        background: #FFFFFF; border: 1px solid #E1E9F0;
        border-radius: 12px; padding: 6px;
    }
    [data-testid="stImage"] img { border-radius: 12px; }
    .hero-card {
        background: linear-gradient(110deg, #FFFFFF 0%, #F3F8FC 62%, #FFF7FA 100%);
        border: 1px solid #DCE6EF; border-radius: 16px;
        padding: 22px 26px; margin: 4px 0 18px 0;
    }
    .hero-kicker { color: #397D9B; font-size: .76rem; font-weight: 700;
        letter-spacing: .12em; text-transform: uppercase; }
    .hero-copy { color: #526777; font-size: 1rem; line-height: 1.55; }
    .hero-card h1 { margin: 5px 0 8px 0; font-size: 2.15rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_sales() -> pd.DataFrame:
    """Load the cleaned CSV and fill date helper columns if needed."""
    file_path = Path(__file__).with_name("cafe_clean.csv")
    data = pd.read_csv(file_path, parse_dates=["Date"])
    if "Month" not in data:
        data["Month"] = data["Date"].dt.month
    if "Weekday" not in data:
        data["Weekday"] = data["Date"].dt.dayofweek
    return data


def style_chart(figure, *, height=390):
    """Use consistent spacing, colors, and grid lines across charts."""
    figure.update_layout(
        template="plotly_white",
        font=dict(family="Arial, sans-serif", color="#243746", size=13),
        title=dict(font=dict(size=18), x=0.02, xanchor="left"),
        margin=dict(l=18, r=18, t=60, b=20),
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend_title_text="",
    )
    figure.update_xaxes(showgrid=False, zeroline=False)
    figure.update_yaxes(showgrid=True, gridcolor="#E8EEF3", zeroline=False)
    return figure


def money_in_millions(amount_in_thousands):
    """The source data stores revenue in thousands of rupees."""
    return f"₹{amount_in_thousands / 1000:,.1f} million"


sales = load_sales()

heading, hero_image = st.columns([3.7, 2], gap="large")
with heading:
    st.caption("CAFÉ SALES · 2025 · PUNE · JAIPUR · KOCHI")
    st.title("Café sales & performance")
    st.markdown(
        "A quick look at **what changed**, **which products led**, and **how the outlets compare**. "
        "Your filters update every number and chart."
    )
    st.caption("*Charts use Rs thousand; headline totals use Rs million.*")
with hero_image:
    st.image(
        Path(__file__).parent / "assets" / "cafe_interior.jpg",
        use_container_width=True,
    )
    st.caption("A café setting · photo by [Micheile Henderson](https://unsplash.com/@micheile)")

# Sidebar filters
st.sidebar.title("Build your view")
st.sidebar.caption("Everything starts selected. Adjust one filter to see how the story changes.")

if st.sidebar.button("Reset all filters", use_container_width=True):
    for key in ("filter_outlets", "filter_items", "filter_months", "filter_offers"):
        st.session_state.pop(key, None)
    st.rerun()

selected_outlets = st.sidebar.multiselect(
    "Outlets", OUTLETS, default=OUTLETS, key="filter_outlets",
    help="Choose which café locations to include.",
)
selected_items = st.sidebar.multiselect(
    "Product categories", ITEMS, default=ITEMS, key="filter_items",
    help="Choose one or more types of products.",
)
month_range = st.sidebar.select_slider(
    "Months", options=list(range(1, 13)), value=(1, 12), key="filter_months",
    format_func=lambda month: MONTHS[month - 1],
)
offer_range = st.sidebar.slider(
    "Offer range", min_value=0, max_value=25, value=(0, 25), step=5,
    key="filter_offers", help="Keep records whose offer is within this range.",
)

if not selected_outlets or not selected_items:
    st.info("Select at least one outlet and one product category to see the charts.")
    st.stop()

first_month, last_month = month_range
first_offer, last_offer = offer_range
view = sales[
    sales["Outlet"].isin(selected_outlets)
    & sales["Item"].isin(selected_items)
    & sales["Month"].between(first_month, last_month)
    & sales["Offer"].between(first_offer, last_offer)
].copy()

if view.empty:
    st.info("No records match these filters. Widen a range or add an outlet/category.")
    st.stop()

# Five headline numbers answer the basic questions before readers open a chart.
outlet_totals = view.groupby("Outlet")["Revenue"].sum()
top_outlet = outlet_totals.idxmax()
item_totals = view.groupby("Item")["Revenue"].sum()
top_item = item_totals.idxmax()
row_share = len(view) / len(sales)
metrics = st.columns(5)
metrics[0].metric("Total revenue", f"₹{view['Revenue'].sum() / 1000:,.1f}M", help="Sum of revenue in the current filters.")
metrics[1].metric("Average per record", f"₹{view['Revenue'].mean():,.0f}k", help="One record is one item at one outlet on one date.")
metrics[2].metric("Records shown", f"{len(view):,}", delta=f"{row_share:.0%} of all records", delta_color="off")
metrics[3].metric("Leading outlet", top_outlet, delta=f"₹{outlet_totals[top_outlet] / 1000:,.1f}M revenue", delta_color="off")
metrics[4].metric("Top product line", top_item, delta=f"₹{item_totals[top_item] / 1000:,.1f}M revenue", delta_color="off")

st.caption(
    f"Current view: {MONTHS[first_month - 1]}–{MONTHS[last_month - 1]}, "
    f"{len(selected_outlets)} outlet(s), {len(selected_items)} category/categories, "
    f"offers {first_offer}%–{last_offer}%."
)

# Plain-language observations based on the active filters
peak_month = int(view.groupby("Month")["Revenue"].sum().idxmax())
weekday_average = view.loc[view["Weekday"] < 5, "Revenue"].mean()
weekend_average = view.loc[view["Weekday"] >= 5, "Revenue"].mean()
weekend_change = (weekend_average / weekday_average - 1) if weekday_average else 0
change_word = "higher" if weekend_change >= 0 else "lower"

with st.container(border=True):
    st.subheader("The short version")
    st.markdown("*These notes update with your filters.*")
    insight1, insight2, insight3 = st.columns(3)
    insight1.markdown(f"**Strongest month**  \n{MONTHS[peak_month - 1]} had the highest total revenue.")
    insight2.markdown(f"**Leading category**  \n{top_item} contributed the most revenue.")
    insight3.markdown(f"**Weekend pattern**  \nWeekend records averaged {abs(weekend_change):.0%} {change_word} revenue than weekday records.")

# One tab per question keeps the page calm while making every analysis easy to find.
overview_tab, product_tab, outlet_tab, offer_tab, data_tab = st.tabs(
    ["Overview", "Products", "Outlets", "Offers", "Data"]
)
chart_config = {"displaylogo": False, "displayModeBar": "hover"}

with overview_tab:
    st.subheader("How did sales change through the year?")
    st.markdown("**Choose a measure.** Total revenue shows the whole month’s sales; average sale compares a typical record.")
    trend_measure = st.radio(
        "Show", ["Total revenue", "Average sale"], horizontal=True,
        help="Total revenue adds records together. Average sale compares the typical record value.",
        key="trend_measure",
    )
    monthly = view.groupby(["Month", "Outlet"])["Revenue"]
    if trend_measure == "Total revenue":
        trend = monthly.sum().rename("Revenue").reset_index()
        y_label = "Revenue (Rs thousand)"
    else:
        trend = monthly.mean().rename("Revenue").reset_index()
        y_label = "Average revenue per record (Rs thousand)"
    trend["Month name"] = trend["Month"].map(lambda month: MONTHS[month - 1])
    line = px.line(
        trend, x="Month name", y="Revenue", color="Outlet", markers=True,
        color_discrete_map=COLORS,
        category_orders={"Month name": MONTHS, "Outlet": OUTLETS},
        labels={"Month name": "Month", "Revenue": y_label},
        title="One point per month for each outlet",
    )
    line.update_traces(
        line=dict(width=3), marker=dict(size=8),
        hovertemplate="<b>%{fullData.name}</b><br>%{x}<br>Revenue: ₹%{y:,.1f} thousand<extra></extra>",
    )
    peak_point = trend.loc[trend["Revenue"].idxmax()]
    line.add_scatter(
        x=[peak_point["Month name"]], y=[peak_point["Revenue"]],
        mode="markers+text", text=["Peak"], textposition="top center",
        marker=dict(size=15, color="#E2B541", symbol="star", line=dict(color="white", width=2)),
        name="Highest month", hovertemplate="Highest monthly value<extra></extra>",
        showlegend=False,
    )
    category_totals = view.groupby("Item", as_index=False)["Revenue"].sum().sort_values("Revenue")
    category_chart = px.bar(
        category_totals, x="Revenue", y="Item", orientation="h", color="Item",
        color_discrete_map=ITEM_COLORS, text=category_totals["Revenue"].map(lambda value: f"₹{value / 1000:.1f}M"),
        labels={"Revenue": "Revenue (Rs thousand)", "Item": "Product category"},
        title="Total revenue by product category",
    )
    category_chart.update_traces(textposition="outside", cliponaxis=False, showlegend=False)
    chart_left, chart_right = st.columns(2, gap="medium")
    chart_left.plotly_chart(style_chart(line), use_container_width=True, config=chart_config)
    chart_left.caption("*One point per month.* Hover for a value or click an outlet in the legend to focus the chart.")
    chart_right.plotly_chart(style_chart(category_chart), use_container_width=True, config=chart_config)
    chart_right.caption("Labels show each category’s total for the selected period.")

    st.subheader("Which days are busiest?")
    weekday = view.groupby("Weekday", as_index=False)["Revenue"].mean()
    weekday["Day"] = weekday["Weekday"].map(lambda day: WEEKDAYS[int(day)])
    weekday["Day type"] = weekday["Day"].map(lambda day: "Weekend" if day in ["Sat", "Sun"] else "Weekday")
    weekday["Records"] = view.groupby("Weekday")["Revenue"].size().values
    day_chart = px.bar(
        weekday, x="Day", y="Revenue", color="Day type",
        color_discrete_map={"Weekday": "#397D9B", "Weekend": "#916B08"},
        category_orders={"Day": WEEKDAYS},
        labels={"Day": "Day of week", "Revenue": "Average revenue (Rs thousand)"},
        title="Which days tend to be busier?",
    )
    day_chart.update_traces(
        text=weekday["Revenue"].map(lambda value: f"₹{value:,.0f}k"),
        textposition="outside",
        customdata=weekday[["Records"]],
        hovertemplate="<b>%{x}</b><br>Average: ₹%{y:,.1f} thousand<br>Records: %{customdata[0]}<extra></extra>",
    )
    st.plotly_chart(style_chart(day_chart, height=360), use_container_width=True, config=chart_config)
    st.caption("Weekend bars use a gold accent. Hover for the average and number of records.")

with product_tab:
    st.subheader("Which categories contribute most?")
    st.markdown("**Use total revenue** to compare contribution, or **average record** to compare typical sales size.")
    product_measure = st.radio(
        "Compare categories by", ["Total revenue", "Average record"], horizontal=True,
        key="product_measure",
    )
    product_groups = view.groupby("Item")["Revenue"]
    product_values = product_groups.sum() if product_measure == "Total revenue" else product_groups.mean()
    products = product_values.rename("Revenue").sort_values().reset_index()
    products["Share"] = products["Revenue"] / products["Revenue"].sum()
    product_chart = px.bar(
        products, x="Revenue", y="Item", orientation="h", color="Item",
        color_discrete_map=ITEM_COLORS,
        text=products["Share"].map(lambda share: f"{share:.0%}"),
        labels={"Revenue": "Revenue (Rs thousand)", "Item": "Category"},
        title=f"{product_measure} by category",
    )
    product_chart.update_traces(
        text=products.apply(lambda row: f"₹{row['Revenue']:,.0f}k  ·  {row['Share']:.0%}", axis=1),
        textposition="outside", cliponaxis=False, showlegend=False,
        hovertemplate="<b>%{y}</b><br>Revenue: ₹%{x:,.1f} thousand<extra></extra>",
    )
    st.plotly_chart(style_chart(product_chart), use_container_width=True, config=chart_config)
    st.caption("*The percentage at each bar end is the category’s share of the values shown.*")

    st.subheader("How do categories compare across outlets?")
    item_grid = view.pivot_table(index="Outlet", columns="Item", values="Revenue", aggfunc="mean")
    item_grid = item_grid.reindex(index=[outlet for outlet in OUTLETS if outlet in selected_outlets])
    item_grid = item_grid.reindex(columns=[item for item in ITEMS if item in selected_items])
    heatmap = px.imshow(
        item_grid, text_auto=".0f", aspect="auto",
        color_continuous_scale=["#F7FAFD", "#BBD8E8", "#397D9B"],
        labels={"x": "Category", "y": "Outlet", "color": "Rs thousand"},
        title="Average record revenue by outlet and category",
    )
    st.plotly_chart(style_chart(heatmap, height=340), use_container_width=True, config=chart_config)
    st.caption("*Each cell is an average. Darker blue means a higher average record value.*")

    st.subheader("A few familiar café details")
    photo_drink, photo_beans = st.columns(2, gap="large")
    with photo_drink:
        st.image(
            Path(__file__).parent / "assets" / "coffee_and_pastry.jpg",
            use_container_width=True,
        )
        st.caption("Coffee and pastry · photo by [Esra Afşar](https://unsplash.com/@esraafsar)")
    with photo_beans:
        st.image(
            Path(__file__).parent / "assets" / "coffee_beans.jpg",
            use_container_width=True,
        )
        st.caption("Roasted coffee beans · photo by [Tatiana Fernández R](https://unsplash.com/@tatianafernandez)")
    st.caption("*These are reference photos for context; they are not images of the practice dataset's actual products or outlets.*")

with outlet_tab:
    st.subheader("Compare outlet performance")
    st.markdown("**Total revenue** reflects outlet size; **average record** compares the typical sale value.")
    outlet_measure = st.radio(
        "Rank outlets by", ["Total revenue", "Average record"], horizontal=True,
        key="outlet_measure",
    )
    outlet_groups = view.groupby("Outlet")["Revenue"]
    outlet_values = outlet_groups.sum() if outlet_measure == "Total revenue" else outlet_groups.mean()
    ranking = outlet_values.rename("Revenue").sort_values().reset_index()
    outlet_chart = px.bar(
        ranking, x="Revenue", y="Outlet", orientation="h", color="Outlet",
        color_discrete_map=COLORS,
        category_orders={"Outlet": OUTLETS},
        labels={"Revenue": "Revenue (Rs thousand)", "Outlet": "Outlet"},
        title=f"{outlet_measure} by outlet",
    )
    outlet_chart.update_traces(showlegend=False)
    st.plotly_chart(style_chart(outlet_chart, height=330), use_container_width=True, config=chart_config)
    st.caption("Switch between total sales and the average value of one record to compare outlets fairly.")

    outlet_item = view.pivot_table(index="Item", columns="Outlet", values="Revenue", aggfunc="mean")
    outlet_item = outlet_item.reindex(index=[item for item in ITEMS if item in selected_items])
    outlet_item = outlet_item.reindex(columns=[outlet for outlet in OUTLETS if outlet in selected_outlets])
    outlet_heatmap = px.imshow(
        outlet_item, text_auto=".0f", aspect="auto",
        color_continuous_scale=["#FFF8FB", "#E8C4D2", "#A84F75"],
        labels={"x": "Outlet", "y": "Category", "color": "Rs thousand"},
        title="Average record by category and outlet",
    )
    st.plotly_chart(style_chart(outlet_heatmap, height=330), use_container_width=True, config=chart_config)

with offer_tab:
    st.subheader("What do sales look like at different offer levels?")
    st.markdown("Choose one product category to make the comparison easier to interpret.")
    offer_item = st.selectbox(
        "Product category", ["All selected categories"] + [item for item in ITEMS if item in selected_items],
        key="offer_item",
    )
    offer_view = view if offer_item == "All selected categories" else view[view["Item"] == offer_item]
    offer_summary = offer_view.groupby(["Offer", "Item"], as_index=False).agg(
        Revenue=("Revenue", "mean"), Records=("Revenue", "size")
    )
    offer_chart = px.line(
        offer_summary, x="Offer", y="Revenue", color="Item", markers=True,
        color_discrete_map=ITEM_COLORS,
        labels={"Offer": "Offer (%)", "Revenue": "Average revenue (Rs thousand)"},
        title="Average record revenue by offer",
        custom_data=["Records"],
    )
    offer_chart.update_traces(
        line=dict(width=3), marker=dict(size=9),
        hovertemplate="<b>%{fullData.name}</b><br>Offer: %{x}%<br>Average: ₹%{y:,.1f} thousand<br>Records: %{customdata[0]}<extra></extra>",
    )
    offer_chart.update_xaxes(dtick=5)
    st.plotly_chart(style_chart(offer_chart, height=400), use_container_width=True, config=chart_config)
    st.info("**A useful caution:** this compares groups in the practice data. It does not prove that an offer caused revenue to change.")

with data_tab:
    st.subheader("Inspect and download the selected records")
    st.markdown("Use the distribution to spot the shape of the data, then download the filtered rows if you want to explore them yourself.")
    distribution = px.histogram(
        view, x="Revenue", color="Item", color_discrete_map=ITEM_COLORS,
        marginal="box", nbins=35, barmode="overlay", opacity=0.72,
        labels={"Revenue": "Revenue (Rs thousand)", "count": "Number of records"},
        title="How revenue values are distributed",
    )
    st.plotly_chart(style_chart(distribution, height=420), use_container_width=True, config=chart_config)
    st.caption("The box above the histogram summarizes the middle of the data. Long tails show unusually large or small values.")

    display_data = view[["Date", "Outlet", "Item", "Offer", "Revenue"]].sort_values("Date")
    st.download_button(
        "Download selected records (CSV)",
        data=display_data.to_csv(index=False).encode("utf-8"),
        file_name="cafe_sales_selection.csv",
        mime="text/csv",
    )
    st.dataframe(
        display_data, use_container_width=True, hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "Revenue": st.column_config.NumberColumn("Revenue (Rs thousand)", format="%.1f"),
            "Offer": st.column_config.NumberColumn("Offer (%)"),
        },
    )

st.divider()
st.caption("Practice data for 2025. Revenue per row refers to one item, outlet, and date.")
