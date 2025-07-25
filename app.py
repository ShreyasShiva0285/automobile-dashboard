import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import io

# === Streamlit Fullscreen + No Scroll CSS ===
st.set_page_config(layout="wide")

st.markdown("""
    <style>
        html, body, [class*="css"]  {
            margin: 0;
            padding: 0;
            overflow-x: hidden;
        }
        .block-container {
            padding: 1rem 2rem 1rem 2rem;
            max-width: 90% !important;
            margin: auto;
        }
    </style>
""", unsafe_allow_html=True)

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

predicted_month_name = (latest_month.to_timestamp() + pd.DateOffset(months=1)).strftime('%B')

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
    pdf.cell(200, 10, txt=f"Predicted Revenue ({predicted_month_name}): £{next_month_prediction:,.0f}", ln=True)
    pdf.cell(200, 10, txt=f"Orders Shipped: {shipped}", ln=True)
    pdf.cell(200, 10, txt=f"Orders Not Shipped: {not_shipped}", ln=True)

    return pdf.output(dest='S').encode('latin-1')

# === Header with Title and Download/Date on same line ===
pdf_bytes = generate_pdf()
st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <div style='font-size: 22px; font-weight: 600;'>🏢 Companies Dashboard Pvt.</div>
        <div style='font-size: 16px; text-align: right;'>
            <a href="https://your-streamlit-app-url" target="_blank" title="Share Dashboard" style="text-decoration: none; margin-right: 15px;">🔗</a>
            <a href="#" download="KPI_Summary_Report.pdf" style="text-decoration: none; margin-right: 15px;">📥</a>
            📅 {datetime.today().strftime('%Y-%m-%d')}
        </div>
    </div>
""", unsafe_allow_html=True)

st.download_button(
    label="Download KPI Summary PDF",
    data=pdf_bytes,
    file_name="KPI_Summary_Report.pdf",
    mime="application/pdf"
)

# === KPI Boxes ===
st.markdown("### 📊 Key Performance Indicators")

box_style = """
    background-color: #fff;
    padding: 12px;
    border: 1.5px solid #cccccc;
    border-radius: 8px;
    text-align: center;
    box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
    font-size: 14px;
    height: 100px;
    display: flex;
    flex-direction: column;
    justify-content: center;
"""

# Top KPI row
top_cols = st.columns(3)
with top_cols[0]:
    st.markdown(f"<div style='{box_style}'><h5>💰 Overall Revenue</h5><h3>£{total_revenue:,.0f}</h3></div>", unsafe_allow_html=True)
with top_cols[1]:
    st.markdown(f"<div style='{box_style}'><h5>📆 Latest Month Revenue ({latest_month.strftime('%B')})</h5><h3>£{latest_month_revenue:,.0f}</h3></div>", unsafe_allow_html=True)
with top_cols[2]:
    st.markdown(f"<div style='{box_style}'><h5>📈 3-Month Growth</h5><h3>{growth_rate:.2f}%</h3></div>", unsafe_allow_html=True)

# Bottom KPI row
bottom_cols = st.columns(3)
with bottom_cols[0]:
    st.markdown(f"<div style='{box_style}'><h5>🔮 Predicted Revenue ({predicted_month_name})</h5><h3>£{next_month_prediction:,.0f}</h3></div>", unsafe_allow_html=True)
with bottom_cols[1]:
    st.markdown(f"<div style='{box_style}'><h5>📦 Orders Shipped</h5><h3>{shipped}</h3></div>", unsafe_allow_html=True)
with bottom_cols[2]:
    st.markdown(f"<div style='{box_style}'><h5>🚚 Orders Not Shipped</h5><h3>{not_shipped}</h3></div>", unsafe_allow_html=True)

st.markdown("---")

# === Placeholder for charts ===
st.markdown("### 📈 Sales Charts (unchanged)")
st.markdown("✅ Your existing bar chart, pie chart, and trends remain untouched.")
# Example:
# fig = px.bar(df, x='PRODUCTLINE', y='SALES', title='Sales by Product Line')
# st.plotly_chart(fig, use_container_width=True)

# === Data Export ===
with st.expander("⬇️ Download Raw Data"):
    st.download_button("Download CSV", data=df.to_csv(index=False), file_name="Auto_Sales_Data.csv", mime="text/csv")
