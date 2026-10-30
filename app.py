import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Cafe Sales | 2025", page_icon="☕", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
.stApp {background: linear-gradient(135deg,#f7f4ed 0%,#edf5f1 100%); color:#17332d}
h1,h2,h3 {font-family:'Playfair Display',serif!important;color:#17332d}
[data-testid="stMetric"] {background:#fff;border:1px solid #dce8df;padding:18px 20px;border-radius:18px;box-shadow:0 8px 24px #17332d0d}
[data-testid="stSidebar"] {background:#17332d}
[data-testid="stSidebar"] * {color:#f8f4eb!important}
[data-testid="stPlotlyChart"] {background:#fff;border-radius:18px;padding:10px;box-shadow:0 8px 24px #17332d0d}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv("cafe_clean.csv", parse_dates=["Date"])

clean = load_data()
st.markdown("# Café, at a glance")
st.caption("2025 performance • Three outlets • A fresh look at the daily sales story")
st.sidebar.markdown("## Tune your view")
st.sidebar.caption("Every metric and chart responds to these filters.")
outlets = st.sidebar.multiselect("Outlets", sorted(clean.Outlet.unique()), default=sorted(clean.Outlet.unique()))
items = st.sidebar.multiselect("Product categories", sorted(clean.Item.unique()), default=sorted(clean.Item.unique()))
first_month, last_month = st.sidebar.slider("Months", 1, 12, (1, 12))
low_offer, high_offer = st.sidebar.slider("Offer range", 0, 25, (0, 25), step=5)
view = clean[clean.Outlet.isin(outlets) & clean.Item.isin(items) & clean.Month.between(first_month,last_month) & clean.Offer.between(low_offer,high_offer)]
if view.empty:
    st.warning("No sales match these filters. Widen the selection to see results.")
    st.stop()

k1,k2,k3,k4 = st.columns(4)
k1.metric("Revenue", f"₹{view.Revenue.sum()/1000:,.1f}M")
k2.metric("Average sale", f"₹{view.Revenue.mean():,.0f}K")
k3.metric("Records", f"{len(view):,}")
k4.metric("Leading outlet", view.groupby('Outlet').Revenue.sum().idxmax())

palette={"Pune":"#e07a5f","Jaipur":"#3d8b78","Kochi":"#e0a83e"}
monthly=view.groupby(["Month","Outlet"],as_index=False).Revenue.sum()
fig_a=px.line(monthly,x="Month",y="Revenue",color="Outlet",markers=True,color_discrete_map=palette,title="The year, month by month")
by_item=view.groupby("Item",as_index=False).Revenue.sum().sort_values("Revenue")
fig_b=px.bar(by_item,x="Revenue",y="Item",orientation="h",color="Revenue",color_continuous_scale=["#b9d6c7","#286858"],title="Where revenue comes from")
grid=view.pivot_table(index="Outlet",columns="Item",values="Revenue",aggfunc="mean")
fig_c=px.imshow(grid,text_auto=".0f",color_continuous_scale="YlGnBu",title="Average sale • outlet × category")
by_offer=view.groupby("Offer",as_index=False).Revenue.mean()
fig_d=px.bar(by_offer,x="Offer",y="Revenue",color="Revenue",color_continuous_scale=["#f2c078","#d56f51"],title="Average sale by offer")
for fig in (fig_a,fig_b,fig_c,fig_d):
    fig.update_layout(template="plotly_white",font=dict(family="DM Sans, sans-serif",color="#29443c"),title_font=dict(size=19),margin=dict(l=18,r=18,t=55,b=18),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",coloraxis_showscale=False)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
left,right=st.columns(2)
left.plotly_chart(fig_a,use_container_width=True)
right.plotly_chart(fig_b,use_container_width=True)
left.plotly_chart(fig_c,use_container_width=True)
right.plotly_chart(fig_d,use_container_width=True)
st.caption("Revenue values are Rs thousand unless shown as millions. Offer comparisons are observational and do not establish cause.")
with st.expander("Explore the rows behind these charts"):
    st.dataframe(view,use_container_width=True,hide_index=True)
