import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Big Data Sales Analysis", page_icon="📊", layout="wide")

st.title("📊 Big Data Sales Analysis Dashboard")
st.caption("Developed by Payal Amale | Mini Project")
st.markdown("Explore a sample sales dataset using data processing, filtering, summary statistics, and interactive charts.")

@st.cache_data
def load_default_data():
    return pd.read_csv("sales_dataset.csv", parse_dates=["Date"])

uploaded = st.sidebar.file_uploader("Upload your own CSV (optional)", type=["csv"])
try:
    if uploaded is not None:
        data = pd.read_csv(uploaded)
    else:
        data = load_default_data()
except Exception as e:
    st.error(f"Could not read the CSV file: {e}")
    st.stop()

required = {"Sales", "Category", "Region"}
missing = required - set(data.columns)
if missing:
    st.error("CSV must contain these columns: " + ", ".join(sorted(required)))
    st.stop()

if "Date" in data.columns:
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")

st.sidebar.header("Filters")
if "Region" in data.columns:
    regions = sorted(data["Region"].dropna().astype(str).unique().tolist())
    selected_regions = st.sidebar.multiselect("Select region", regions, default=regions)
else:
    selected_regions = []
if "Category" in data.columns:
    categories = sorted(data["Category"].dropna().astype(str).unique().tolist())
    selected_categories = st.sidebar.multiselect("Select category", categories, default=categories)
else:
    selected_categories = []

filtered = data.copy()
if "Region" in filtered.columns and selected_regions:
    filtered = filtered[filtered["Region"].astype(str).isin(selected_regions)]
elif "Region" in filtered.columns and not selected_regions:
    filtered = filtered.iloc[0:0]
if "Category" in filtered.columns and selected_categories:
    filtered = filtered[filtered["Category"].astype(str).isin(selected_categories)]
elif "Category" in filtered.columns and not selected_categories:
    filtered = filtered.iloc[0:0]

sales_total = pd.to_numeric(filtered["Sales"], errors="coerce").fillna(0).sum()
order_count = filtered["Order_ID"].nunique() if "Order_ID" in filtered.columns else len(filtered)
avg_sale = sales_total / order_count if order_count else 0
units = pd.to_numeric(filtered["Quantity"], errors="coerce").fillna(0).sum() if "Quantity" in filtered.columns else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Sales", f"₹{sales_total:,.0f}")
m2.metric("Orders / Records", f"{order_count:,}")
m3.metric("Average Sale per Order", f"₹{avg_sale:,.0f}")
m4.metric("Units Sold", f"{units:,.0f}" if "Quantity" in filtered.columns else "N/A")

st.divider()
left, right = st.columns(2)
with left:
    st.subheader("Sales by Category")
    category_sales = filtered.groupby("Category", dropna=False)["Sales"].sum().reset_index().sort_values("Sales", ascending=False)
    fig = px.bar(category_sales, x="Category", y="Sales", color="Category", title="Total sales in each category")
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Sales Share by Region")
    region_sales = filtered.groupby("Region", dropna=False)["Sales"].sum().reset_index()
    fig2 = px.pie(region_sales, names="Region", values="Sales", hole=.35, title="Regional sales distribution")
    st.plotly_chart(fig2, use_container_width=True)

if "Date" in filtered.columns and filtered["Date"].notna().any():
    st.subheader("Sales Trend Over Time")
    trend = filtered.dropna(subset=["Date"]).copy()
    trend["Month"] = trend["Date"].dt.to_period("M").astype(str)
    monthly = trend.groupby("Month", as_index=False)["Sales"].sum()
    fig3 = px.line(monthly, x="Month", y="Sales", markers=True, title="Monthly sales trend")
    st.plotly_chart(fig3, use_container_width=True)

st.subheader("Dataset Preview")
st.write(f"Showing {len(filtered):,} records after filters.")
st.dataframe(filtered, use_container_width=True, hide_index=True)

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download filtered data as CSV", data=csv, file_name="filtered_sales_data.csv", mime="text/csv")

with st.expander("Project explanation"):
    st.write("""
    **Aim:** To analyze sales data using Python and Streamlit.

    **Big Data concepts demonstrated:** data ingestion from CSV, data cleaning/conversion,
    filtering, aggregation, summary metrics, visualization, and exporting processed data.

    **Note:** This mini project uses a generated sample dataset to demonstrate the workflow.
    It is a dashboard prototype, not a distributed Hadoop/Spark cluster.
    """)
