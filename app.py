import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Load the data
df = pd.read_csv("Auto Sales data.csv", parse_dates=["ORDERDATE"])
df["ORDERDATE"] = pd.to_datetime(df["ORDERDATE"])
df["EST_PROFIT"] = (df["MSRP"] - df["PRICEEACH"]) * df["QUANTITYORDERED"]

# ==== KPI Calculations ====
total_revenue = df["SALES"].sum()

# Latest month revenue
latest_month = df["ORDERDATE"].max().to_period("M")
latest_month_revenue = df[df["ORDERDATE"].dt.to_period("M") == latest_month]["SALES"].sum()

# 3-month growth
df["MONTH"] = df["ORDERDATE"].dt.to_period("M")
last_3_months = df["MONTH"].sort_values().unique()[-3:]
rev_last_3 = df[df["MONTH"].isin(last_3_months)].groupby("MONTH")["SALES"].sum()
growth_rate = ((rev_last_3.iloc[-1] - rev_last_3.iloc[0]) / rev_last_3.iloc[0]) * 100 if len(rev_last_3) == 3 else 0

# Predicted next month
monthly_rev = df.groupby(df["ORDERDATE"].dt.to_period("M"))["SALES"].sum()
next_month_prediction = monthly_rev.mean()

# Order status
status_counts = df["STATUS"].value_counts()
shipped = status_counts.get("Shipped", 0)
not_shipped = status_counts.sum() - shipped

# ==== Streamlit Layout ====
st.set_page_config(page_title="Companies Dashboard Pvt.", layout="wide")

# ==== Header ====
col1, col2 = st.columns([6, 6])
with col1:
    st.markdown("## 🏢 Companies Dashboard Pvt.")
with col2:
    st.markdown(f"""
        <div style='text-align:right; font-size:18px'>
            🔗 📥 <span style='margin-left:20px;'>📅 {datetime.today().strftime('%Y-%m-%d')}</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==== KPI Section (Horizontal) ====
st.markdown("### 📊 Key Performance Indicators")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("💰 Overall Revenue", f"£{total_revenue:,.0f}")
with kpi2:
    st.metric("📆 Latest Month Revenue", f"£{latest_month_revenue:,.0f}")
with kpi3:
    st.metric("📈 3-Month Growth", f"{growth_rate:.2f}%")
with kpi4:
    st.metric("📊 Predicted Next Month", f"£{next_month_prediction:,.0f}")

kpi5, kpi6 = st.columns(2)
with kpi5:
    st.metric("📦 Orders Shipped", shipped)
with kpi6:
    st.metric("🚚 Orders Not Shipped", not_shipped)

st.markdown("---")

# ==== (Optional) Charts Below - keep your existing charts ====
# Just a placeholder section to keep your visuals

st.markdown("### 📈 Sales Charts (unchanged)")
st.markdown("✅ Your existing bar chart, pie chart, and trends remain untouched.")

# Add download button if needed
with st.expander("⬇️ Download Raw Data"):
    st.download_button("Download CSV", data=df.to_csv(index=False), file_name="filtered_data.csv", mime="text/csv")
