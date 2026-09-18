import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page Configuration
st.set_page_config(
    page_title="Sales Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load Sales data
df = pd.read_csv("sales_data.csv")

# Convert Order_Date to datetime to make date filtering work
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
min_date = df["Order_Date"].min()
max_date = df["Order_Date"].max()

# Dashboard Title
st.title("📊 Sales Analysis Dashboard")
st.write("Interactive dashboard for analyzing sales performance.")

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")

# 1. Date Filter (The missing piece!)
selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date.date(), max_date.date()),  # Default: Selects entire range
    min_value=min_date.date(),
    max_value=max_date.date()
)

# 2. Region Filter
region_filter = st.sidebar.multiselect(
    "Select Region",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

# 3. Category Filter
category_filter = st.sidebar.multiselect(
    "Select Category",
    options=df["Category of all applications"].unique(),
    default=df["Category"].unique()
)

# --- APPLY ALL FILTERS ---
# Check if the user completed the date range selection (start & end date selected)
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
    filtered_df = df[
        (df["Order_Date"] >= pd.to_datetime(start_date)) &
        (df["Order_Date"] <= pd.to_datetime(end_date)) &
        (df["Region"].isin(region_filter)) &
        (df["Category"].isin(category_filter))
    ]
else:
    # Fallback in case user is in the middle of picking a date range
    filtered_df = df[
        (df["Region"].isin(region_filter)) &
        (df["Category"].isin(category_filter))
    ]

# --- KPI METRICS ---
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_orders = len(filtered_df)
total_quantity = filtered_df["Quantity"].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Sales", f"₹{total_sales:,.0f}")
col2.metric("Total Profit", f"₹{total_profit:,.0f}")
col3.metric("Total Orders", total_orders)
col4.metric("Units Sold", total_quantity)

st.divider()

# --- CHARTS ---

# 1. Monthly Sales Trend
monthly_sales = (
    filtered_df
    .groupby(filtered_df["Order_Date"].dt.to_period("M"))["Sales"]
    .sum()
    .reset_index()
)
monthly_sales["Order_Date"] = monthly_sales["Order_Date"].astype(str)

fig1 = px.line(
    monthly_sales,
    x="Order_Date",
    y="Sales",
    title="Monthly Sales Trend",
    markers=True
)
st.plotly_chart(fig1, use_container_width=True)

# 2. Region Wise Sales
region_sales = (
    filtered_df
    .groupby("Region")["Sales"]
    .sum()
    .reset_index()
)
fig2 = px.bar(
    region_sales,
    x="Region",
    y="Sales",
    title="Region Wise Sales"
)
st.plotly_chart(fig2, use_container_width=True)

# 3. Product Performance
product_sales = (
    filtered_df
    .groupby("Product")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
fig3 = px.bar(
    product_sales,
    x="Product",
    y="Sales",
    title="Top Products By Sales"
)
st.plotly_chart(fig3, use_container_width=True)

# 4. Profit Analysis
profit_data = (
    filtered_df
    .groupby("Product")["Profit"]
    .sum()
    .reset_index()
)
fig4 = px.pie(
    profit_data,
    values="Profit",
    names="Product",
    title="Profit Distribution"
)
st.plotly_chart(fig4, use_container_width=True)

# --- DISPLAY DATA & DOWNLOAD ---
st.subheader("Sales Data")
st.dataframe(filtered_df, use_container_width=True)

csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Sales Report",
    data=csv,
    file_name="sales_report.csv",
    mime="text/csv"
)

st.markdown("---")
st.write("Built using Python, Pandas, Plotly and Streamlit")