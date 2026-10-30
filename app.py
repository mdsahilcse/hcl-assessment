"""A small, readable Streamlit dashboard for exploring café sales."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# Keep page setup first so Streamlit can use the full browser width.
st.set_page_config(page_title="Café sales | 2025", page_icon="☕", layout="wide")

# A simple palette and light styling keep the charts easy to read.
COLORS = {"Pune": "#287D70", "Jaipur": "#D17A4A", "Kochi": "#5479A6"}
INK = "#263B36"

st.markdown(
    """
    <style>
    .stApp { background: #F6F7F4; color: #263B36; }
    h1, h2, h3 { color: #263B36; letter-spacing: -0.02em; }
    [data-testid="stMetric"] {
      background: white; border: 1px solid #E3E8E3; padding: 16px 18px;
      border-radius: 10px;
    }
    [data-testid="stSidebar"] { background: #EEF2EE; }
    [data-testid="stPlotlyChart"] {
      background: white; border: 1px solid #E3E8E3; border-radius: 10px;
      padding: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_sales_data() -> pd.DataFrame:
    """Read the cleaned sales file once and reuse it across filter changes."""
    csv_path = Path(__file__).with_name("cafe_clean.csv")
    return pd.read_csv(csv_path, parse_dates=["Date"])


def format_money_millions(amount_in_thousands: float) -> str:
    """Convert Rs thousand into a short Rs million label."""
    return f"₹{amount_in_thousands / 1000:,.1f} million"


def style_chart(fig, *, height: int = 360):
    """Apply the same clean typography and spacing to every Plotly chart."""
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Arial, sans-serif", color=INK, size=13),
        title=dict(font=dict(size=18), x=0.02, xanchor="left"),
        margin=dict(l=16, r=16, t=58, b=22),
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend_title_text="Outlet",
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    return fig


def make_sales_charts(sales: pd.DataFrame):
    """Build the four charts from the currently selected rows."""
    monthly = sales.groupby(["Month", "Outlet"], as_index=False)["Revenue"].sum()
    by_item = sales.groupby("Item", as_index=False)["Revenue"].sum().sort_values("Revenue")
    by_item["Share"] = by_item["Revenue"] / by_item["Revenue"].sum()
    outlet_item = sales.pivot_table(
        index="Outlet", columns="Item", values="Revenue", aggfunc="mean"
    )
    by_offer = sales.groupby("Offer", as_index=False)["Revenue"].mean()

    monthly_chart = px.line(
        monthly,
        x="Month",
        y="Revenue",
        color="Outlet",
        markers=True,
        color_discrete_map=COLORS,
        title="Monthly revenue by outlet",
        labels={"Month": "Month number", "Revenue": "Revenue (Rs thousand)"},
    )
    monthly_chart.update_xaxes(dtick=1)

    item_chart = px.bar(
        by_item,
        x="Revenue",
        y="Item",
        orientation="h",
        text=by_item["Share"].map(lambda share: f"{share:.0%}"),
        title="Revenue by product category",
        labels={"Revenue": "Revenue (Rs thousand)", "Item": "Product category"},
        color_discrete_sequence=["#287D70"],
    )
    item_chart.update_traces(textposition="outside", cliponaxis=False)

    heatmap = px.imshow(
        outlet_item,
        text_auto=".0f",
        color_continuous_scale="Teal",
        title="Average sale by outlet and category",
        labels={"x": "Product category", "y": "Outlet", "color": "Rs thousand"},
        aspect="auto",
    )

    offer_chart = px.bar(
        by_offer,
        x="Offer",
        y="Revenue",
        title="Average sale at each offer level",
        labels={"Offer": "Offer (%)", "Revenue": "Average revenue (Rs thousand)"},
        color_discrete_sequence=["#D17A4A"],
    )
    offer_chart.update_xaxes(dtick=5)

    return tuple(style_chart(chart) for chart in (monthly_chart, item_chart, heatmap, offer_chart))


sales = load_sales_data()
sales["Date"] = pd.to_datetime(sales["Date"])
if "Month" not in sales.columns:
    sales["Month"] = sales["Date"].dt.month

# Page introduction
st.title("Café sales, made clear")
st.write(
    "Explore how sales changed during 2025, which categories contributed most, "
    "and how results differ by outlet. Use the filters to focus the whole page."
)
st.caption("All revenue is in Indian rupees. Charts and totals update together when you change a filter.")

# Sidebar filters
st.sidebar.title("Choose what to see")
st.sidebar.caption("Start with everything selected, then narrow the view.")
selected_outlets = st.sidebar.multiselect(
    "Outlets", options=sorted(sales["Outlet"].unique()),
    default=sorted(sales["Outlet"].unique()),
    help="Select one or more café locations.",
)
selected_items = st.sidebar.multiselect(
    "Product categories", options=sorted(sales["Item"].unique()),
    default=sorted(sales["Item"].unique()),
    help="Choose Beverages, Bakery, Merchandise, or any combination.",
)
first_month, last_month = st.sidebar.slider(
    "Months to include", min_value=1, max_value=12, value=(1, 12),
    help="1 is January and 12 is December.",
)
first_offer, last_offer = st.sidebar.slider(
    "Offer range (%)", min_value=0, max_value=25, value=(0, 25), step=5,
)

# Each condition below is one filter. A row must match all four to remain visible.
visible_sales = sales[
    sales["Outlet"].isin(selected_outlets)
    & sales["Item"].isin(selected_items)
    & sales["Month"].between(first_month, last_month)
    & sales["Offer"].between(first_offer, last_offer)
].copy()

if visible_sales.empty:
    st.info("There are no sales for this selection. Try adding an outlet or widening a range.")
    st.stop()

# Headline numbers give readers the scale before they interpret the charts.
best_outlet = visible_sales.groupby("Outlet")["Revenue"].sum().idxmax()
kpis = st.columns(4)
kpis[0].metric("Total revenue", format_money_millions(visible_sales["Revenue"].sum()))
kpis[1].metric("Average per record", f"₹{visible_sales['Revenue'].mean():,.0f} thousand")
kpis[2].metric("Sales records", f"{len(visible_sales):,}")
kpis[3].metric("Top outlet", best_outlet)

# Explain the scope in ordinary language so filtered charts are not misread.
st.caption(
    f"Showing {len(visible_sales):,} records from {len(selected_outlets)} selected outlet(s), "
    f"{len(selected_items)} selected category/categories, months {first_month}–{last_month}, "
    f"and offers from {first_offer}% to {last_offer}%."
)

monthly_chart, item_chart, heatmap, offer_chart = make_sales_charts(visible_sales)
trend_tab, mix_tab, offer_tab, data_tab = st.tabs(
    ["Sales over time", "Products and outlets", "Offers", "Data"]
)

with trend_tab:
    st.subheader("How sales changed")
    st.write("Each line follows one outlet through the months. Hover over a point to see its total.")
    st.plotly_chart(monthly_chart, use_container_width=True)

with mix_tab:
    st.subheader("Where sales came from")
    st.write("The labels on the bars show each category’s share of the selected revenue.")
    st.plotly_chart(item_chart, use_container_width=True)
    st.write("The table of colors compares average record revenue. Darker cells indicate higher averages.")
    st.plotly_chart(heatmap, use_container_width=True)

with offer_tab:
    st.subheader("Offers and average sales")
    st.write(
        "This chart compares records with different offer levels. It can show a relationship, "
        "but it cannot tell us that the offer caused the sales change."
    )
    st.plotly_chart(offer_chart, use_container_width=True)

with data_tab:
    st.subheader("The records behind the charts")
    st.write("Use this table to check dates, outlets, categories, offers, and revenue values.")
    st.download_button(
        "Download these rows as CSV",
        data=visible_sales.to_csv(index=False).encode("utf-8"),
        file_name="cafe_sales_selection.csv",
        mime="text/csv",
    )
    st.dataframe(visible_sales, use_container_width=True, hide_index=True)

st.divider()
st.caption(
    "Data note: this practice dataset contains three deliberately inserted extreme values, "
    "which were excluded in the cleaned file. Offer comparisons are descriptive, not causal."
)
