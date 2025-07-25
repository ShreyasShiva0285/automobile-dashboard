# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# === Load data ===
df = pd.read_csv("Auto Sales data.csv", parse_dates=['ORDERDATE'])

# === Preprocess ===
df['EST_PROFIT'] = (df['MSRP'] - df['PRICEEACH']) * df['QUANTITYORDERED']
df['Month'] = df['ORDERDATE'].dt.to_period('M').astype(str)

# === Sidebar Filters ===
st.sidebar.title("🔍 Filters")
date_range = st.sidebar.date_input("Select Order Date Range", [df['ORDERDATE'].min(), df['ORDERDATE'].max()])
productline_filter = st.sidebar.multiselect("Product Line", df['PRODUCTLINE'].unique(), default=df['PRODUCTLINE'].unique())
deal_filter = st.sidebar.multiselect("Deal Size", df['DEALSIZE'].unique(), default=df['DEALSIZE'].unique())

df_filtered = df[
    (df['ORDERDATE'] >= pd.to_datetime(date_range[0])) &
    (df['ORDERDATE'] <= pd.to_datetime(date_range[1])) &
    (df['PRODUCTLINE'].isin(productline_filter)) &
    (df['DEALSIZE'].isin(deal_filter))
]

# === KPIs ===
total_revenue = df_filtered['SALES'].sum()
order_count = df_filtered['ORDERNUMBER'].nunique()
avg_order_value = total_revenue / order_count if order_count else 0
estimated_profit = df_filtered['EST_PROFIT'].sum()
unique_customers = df_filtered['CUSTOMERNAME'].nunique()
repeat_customers = df_filtered['CUSTOMERNAME'].value_counts().gt(1).sum()

st.set_page_config(layout="wide")
st.title("🚗 Automobile Sales Dashboard")
st.markdown(f"📅 **Today**: `{datetime.now().strftime('%Y-%m-%d %H:%M')}`")

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("💰 Total Revenue", f"£{total_revenue:,.0f}")
kpi2.metric("📦 Total Orders", f"{order_count}")
kpi3.metric("📊 Avg Order Value", f"£{avg_order_value:,.2f}")

kpi4, kpi5, kpi6 = st.columns(3)
kpi4.metric("💹 Estimated Profit", f"£{estimated_profit:,.0f}")
kpi5.metric("👥 Unique Customers", f"{unique_customers}")
kpi6.metric("🔁 Repeat Customers", f"{repeat_customers}")

# === Charts ===

st.subheader("📊 Sales by Product Line")
sales_by_line = df_filtered.groupby("PRODUCTLINE")["SALES"].sum().reset_index()
fig1 = px.bar(sales_by_line, x="SALES", y="PRODUCTLINE", orientation="h", color="SALES", color_continuous_scale="Blues")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("📈 Monthly Revenue Trend")
monthly_rev = df_filtered.groupby("Month")["SALES"].sum().reset_index()
monthly_rev['Growth'] = monthly_rev['SALES'].diff()
fig2 = px.bar(
    monthly_rev, x="Month", y="SALES", color="Growth",
    color_continuous_scale=["red", "green"], title="Monthly Revenue Trend"
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("🍰 Deal Size Distribution")
fig3 = px.pie(df_filtered, names='DEALSIZE', hole=0.5, title="Deal Size Share")
st.plotly_chart(fig3, use_container_width=True)

# === Business Insights ===
st.subheader("🧠 Business Insights")
insights = []
if monthly_rev['Growth'].iloc[-1] < 0:
    insights.append("⚠️ Revenue declined this month. Investigate underperforming products.")
else:
    insights.append("✅ Revenue increased this month. Keep up the momentum!")

if repeat_customers / unique_customers < 0.3:
    insights.append("⚠️ Low repeat customers. Consider retention strategies.")

if estimated_profit < (0.1 * total_revenue):
    insights.append("⚠️ Profit margin below 10%. Check pricing and costs.")

for insight in insights:
    st.markdown(insight)

# === Export Button ===
st.subheader("⬇️ Download Filtered Data")
st.download_button("Download CSV", df_filtered.to_csv(index=False), file_name="filtered_auto_sales.csv")
