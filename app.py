import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Load data
df = pd.read_csv("Auto Sales data.csv", parse_dates=["ORDERDATE"])
df["ORDERDATE"] = pd.to_datetime(df["ORDERDATE"])
df["EST_PROFIT"] = (df["MSRP"] - df["PRICEEACH"]) * df["QUANTITYORDERED"]

# KPI Calculations
total_revenue = df["SALES"].sum()
latest_month = df["ORDERDATE"].max().to_period("M")
latest_month_revenue = df[df["ORDERDATE"].dt.to_period("M") == latest_month]["SALES"].sum()

df["MONTH"] = df["ORDERDATE"].dt.to_period("M")
last_3_months = df["MONTH"].sort_values().unique()[-3:]
rev_last_3 = df[df["MONTH"].isin(last_3_months)].groupby("MONTH")["SALES"].sum()
growth_rate = ((rev_last_3.iloc[-1] - rev_last_3.iloc[0]) / rev_last_3.iloc[0]) * 100 if len(rev_last_3) == 3 else 0

monthly_rev = df.groupby(df["ORDERDATE"].dt.to_period("M"))["SALES"].sum()
next_month_prediction = monthly_rev.mean()

status_counts = df["STATUS"].value_counts()
shipped = status_counts.get("Shipped", 0)
not_shipped = status_counts.sum() - shipped
active_deals = df[df["STATUS"] == "In Process"]["CUSTOMERNAME"].nunique()

# Streamlit Layout
st.set_page_config(page_title="Companies Dashboard Pvt.", layout="wide")

# Header
col1, col2 = st.columns([6, 6])
with col1:
    st.markdown("## 🏢 Companies Dashboard Pvt.")

with col2:
    st.markdown(f"""
        <div style='text-align:right; font-size:18px'>
            🔗 📥 <span style='margin-left:20px;'>📅 {datetime.today().strftime('%Y-%m-%d')}</span>
        </div>
    """, unsafe_allow_html=True)

# KPI Section
col_left, col_right = st.columns([6, 6])
with col_left:
    st.metric("💰 Overall Revenue", f"£{total_revenue:,.0f}")
    st.metric("📆 Latest Month Revenue", f"£{latest_month_revenue:,.0f}")
    st.metric("📈 Last 3-Month Growth Rate", f"{growth_rate:.2f}%")
    st.metric("📊 Next Month Predicted Revenue", f"£{next_month_prediction:,.0f}")

with col_right:
    st.metric("📦 Orders Shipped", shipped)
    st.metric("🚚 Orders Not Shipped", not_shipped)
    st.metric("🧑‍💼 Active Deal Customers", active_deals)
