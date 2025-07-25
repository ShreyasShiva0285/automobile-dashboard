import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import io

# === Load Data ===
df = pd.read_csv("Auto Sales data.csv", parse_dates=["ORDERDATE"])
df["ORDERDATE"] = pd.to_datetime(df["ORDERDATE"])
df["EST_PROFIT"] = (df["MSRP"] - df["PRICEEACH"]) * df["QUANTITYORDERED"]

# === KPI Calculations ===
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

predicted_month_num = (latest_month.to_timestamp().month % 12) + 1

# === PDF Generator ===
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="KPI Summary Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Overall Revenue: £{total_revenue:,.0f}", ln=True)
    pdf.cell(200, 10, txt=f"Latest Month Revenue ({latest_month.strftime('%B')}): £{latest_month_revenue:,.0f}", ln=True)
    pdf.cell(200, 10, txt=f"3-Month Growth Rate: {growth_rate:.2f}%", ln=True)
    pdf.cell(200, 10, txt=f"Predicted Revenue (Month {predicted_month_num}): £{next_month_prediction:,.0f}", ln=True)
    pdf.cell(200, 10, txt=f"Orders Shipped: {shipped}", ln=True)
    pdf.cell(200, 10, txt=f"Orders Not Shipped: {not_shipped}", ln=True)

    pdf_stream = io.BytesIO()
    pdf.output(pdf_stream)
    pdf_stream.seek(0)
    return pdf_stream



# === Page Config ===
st.set_page_config(page_title="Companies Dashboard Pvt.", layout="wide")

# === Header ===
col1, col2 = st.columns([6, 6])
with col1:
    st.markdown("## 🏢 Companies Dashboard Pvt.")
with col2:
    pdf_bytes = generate_pdf()
    st.markdown(f"""
        <div style='text-align:right; font-size:18px'>
            <a href="https://your-streamlit-app-url" target="_blank" title="Share Dashboard">🔗</a>
        </div>
    """, unsafe_allow_html=True)
    st.download_button(
        label="📥",
        data=pdf_bytes,
        file_name="KPI_Summary_Report.pdf",
        mime="application/pdf",
        help="Download KPI Summary as PDF"
    )
    st.markdown(f"<div style='text-align:right; font-size:16px'>📅 {datetime.today().strftime('%Y-%m-%d')}</div>", unsafe_allow_html=True)

st.markdown("---")

# === KPI Layout ===
st.markdown("### 📊 Key Performance Indicators")

box_style = """
    background-color: #fff;
    padding: 10px;
    border: 1.5px solid #cccccc;
    border-radius: 8px;
    text-align: center;
    box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
    font-size: 14px;
"""

kpi_top = st.columns(3)
with kpi_top[0]:
    st.markdown(f"<div style='{box_style}'><h5>💰 Overall Revenue</h5><h3>£{total_revenue:,.0f}</h3></div>", unsafe_allow_html=True)
with kpi_top[1]:
    st.markdown(f"<div style='{box_style}'><h5>📆 Latest Month Revenue ({latest_month.strftime('%B')})</h5><h3>£{latest_month_revenue:,.0f}</h3></div>", unsafe_allow_html=True)
with kpi_top[2]:
    st.markdown(f"<div style='{box_style}'><h5>📈 3-Month Growth</h5><h3>{growth_rate:.2f}%</h3></div>", unsafe_allow_html=True)

kpi_bottom = st.columns(3)
with kpi_bottom[0]:
    st.markdown(f"<div style='{box_style}'><h5>🔮 Predicted Revenue (Month {predicted_month_num})</h5><h3>£{next_month_prediction:,.0f}</h3></div>", unsafe_allow_html=True)
with kpi_bottom[1]:
    st.markdown(f"<div style='{box_style}'><h5>📦 Orders Shipped</h5><h3>{shipped}</h3></div>", unsafe_allow_html=True)
with kpi_bottom[2]:
    st.markdown(f"<div style='{box_style}'><h5>🚚 Orders Not Shipped</h5><h3>{not_shipped}</h3></div>", unsafe_allow_html=True)

st.markdown("---")

# === Charts Placeholder ===
st.markdown("### 📈 Sales Charts (unchanged)")
st.markdown("✅ Your existing bar chart, pie chart, and trends remain untouched.")
# Example:
# fig = px.bar(df, x='PRODUCTLINE', y='SALES', title='Sales by Product Line')
# st.plotly_chart(fig, use_container_width=True)

# === Data Export ===
with st.expander("⬇️ Download Raw Data"):
    st.download_button("Download CSV", data=df.to_csv(index=False), file_name="Auto_Sales_Data.csv", mime="text/csv")
