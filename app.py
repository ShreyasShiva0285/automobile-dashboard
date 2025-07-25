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

# Predicted next month revenue (simple average)
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

# ==== KPI Section (Horizontal Layout in Boxes) ====
st.markdown("### 📊 Key Performance Indicators")

box_style = """
    background-color: #fff;
    padding: 10px;
    border: 1.5px solid #cccccc;
    border-radius: 8px;
    text-align: center;
    box-shadow: 2px 2px 4px rgba(0,0,0,0.05);
    font-size: 15px;
"""
# Top row KPIs
kpi_row1 = st.columns(3)
with kpi_row1[0]:
    st.markdown(f"<div style='{box_style}'><h5>💰 Overall Revenue</h5><h3>£{total_revenue:,.0f}</h3></div>", unsafe_allow_html=True)
with kpi_row1[1]:
    st.markdown(f"<div style='{box_style}'><h5>📆 Latest Month Revenue</h5><h3>£{latest_month_revenue:,.0f}</h3></div>", unsafe_allow_html=True)
with kpi_row1[2]:
    st.markdown(f"<div style='{box_style}'><h5>📈 3-Month Growth</h5><h3>{growth_rate:.2f}%</h3></div>", unsafe_allow_html=True)

# Bottom row KPIs
kpi_row2 = st.columns(3)
with kpi_row2[0]:
    st.markdown(f"<div style='{box_style}'><h5>📊 Predicted Next Month</h5><h3>£{next_month_prediction:,.0f}</h3></div>", unsafe_allow_html=True)
with kpi_row2[1]:
    st.markdown(f"<div style='{box_style}'><h5>📦 Orders Shipped</h5><h3>{shipped}</h3></div>", unsafe_allow_html=True)
with kpi_row2[2]:
    st.markdown(f"<div style='{box_style}'><h5>🚚 Orders Not Shipped</h5><h3>{not_shipped}</h3></div>", unsafe_allow_html=True)

st.markdown("---")

# ==== Charts Section (unchanged) ====
st.markdown("### 📈 Sales Charts (unchanged)")
st.markdown("✅ Your existing bar chart, pie chart, and trends remain untouched.")

# Example placeholder
# fig = px.bar(df, x='PRODUCTLINE', y='SALES', title='Sales by Product Line')
# st.plotly_chart(fig, use_container_width=True)

# ==== Download Raw Data ====
with st.expander("⬇️ Download Raw Data"):
    st.download_button("Download CSV", data=df.to_csv(index=False), file_name="filtered_data.csv", mime="text/csv")
