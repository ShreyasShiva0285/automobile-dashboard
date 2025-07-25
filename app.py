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

    return pdf.output(dest='S').encode('latin-1')


# === Header (Left: Title | Right: Share, Download, Date) ===
pdf_bytes = generate_pdf()
st.markdown("""
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <div style='font-size: 22px; font-weight: 600;'>🏢 Companies Dashboard Pvt.</div>
        <div style='font-size: 16px; text-align: right;'>
            <a href="https://your-streamlit-app-url" target="_blank" title="Share Dashboard" style="text-decoration: none; margin-right: 15px;">🔗</a>
            <a href="#" download="KPI_Summary_Report.pdf" style="text-decoration: none; margin-right: 15px;">📥</a>
            📅 {date}
        </div>
    </div>
""".format(date=datetime.today().strftime('%Y-%m-%d')), unsafe_allow_html=True)

# Trigger download button below the link (functional)
st.download_button(
    label="Download KPI Summary PDF",
    data=pdf_bytes,
    file_name="KPI_Summary_Report.pdf",
    mime="application/pdf"
)
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

# === TOP ROW KPIs ===
top_spacer1, top_col1, top_spacer2, top_col2, top_spacer3, top_col3, top_spacer4 = st.columns([0.2, 1, 0.2, 1, 0.2, 1, 0.2])
with top_col1:
    st.markdown(f"<div style='{box_style}'><h5>💰 Overall Revenue</h5><h3>£{total_revenue:,.0f}</h3></div>", unsafe_allow_html=True)
with top_col2:
    st.markdown(f"<div style='{box_style}'><h5>📆 Latest Month Revenue ({latest_month.strftime('%B')})</h5><h3>£{latest_month_revenue:,.0f}</h3></div>", unsafe_allow_html=True)
with top_col3:
    st.markdown(f"<div style='{box_style}'><h5>📈 3-Month Growth</h5><h3>{growth_rate:.2f}%</h3></div>", unsafe_allow_html=True)

# === BOTTOM ROW KPIs ===
bottom_spacer1, bottom_col1, bottom_spacer2, bottom_col2, bottom_spacer3, bottom_col3, bottom_spacer4 = st.columns([0.2, 1, 0.2, 1, 0.2, 1, 0.2])
with bottom_col1:
    st.markdown(f"<div style='{box_style}'><h5>🔮 Predicted Revenue (Month {predicted_month_num})</h5><h3>£{next_month_prediction:,.0f}</h3></div>", unsafe_allow_html=True)
with bottom_col2:
    st.markdown(f"<div style='{box_style}'><h5>📦 Orders Shipped</h5><h3>{shipped}</h3></div>", unsafe_allow_html=True)
with bottom_col3:
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
