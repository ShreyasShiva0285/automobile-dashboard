import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Load data
df = pd.read_csv("Auto Sales data.csv", parse_dates=["ORDERDATE"])
df["ORDERDATE"] = pd.to_datetime(df["ORDERDATE"])
df["EST_PROFIT"] = (df["MSRP"] - df["PRICEEACH"]) * df["QUANTITYORDERED"]

# KPI Section - Horizontal Layout
st.markdown("### 📊 Key Performance Indicators")

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
with kpi_col1:
    st.metric("💰 Overall Revenue", f"£{total_revenue:,.0f}")
with kpi_col2:
    st.metric("📆 Latest Month Revenue", f"£{latest_month_revenue:,.0f}")
with kpi_col3:
    st.metric("📈 3-Month Growth", f"{growth_rate:.2f}%")
with kpi_col4:
    st.metric("📊 Predicted Next Month", f"£{next_month_prediction:,.0f}")

status_col1, status_col2 = st.columns(2)
with status_col1:
    st.metric("📦 Orders Shipped", shipped)
with status_col2:
    st.metric("🚚 Orders Not Shipped", not_shipped)

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
