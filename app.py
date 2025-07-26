import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

# === Layout Styling ===
box_wrapper = "padding: 8px;"  # Space around each card
box_style = """
    background-color: #fff;
    padding: 16px;
    border: 1.5px solid #cccccc;
    border-radius: 8px;
    text-align: center;
    box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
    font-size: 14px;
    height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
"""
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
predicted_month_name = (latest_month.to_timestamp() + pd.DateOffset(months=1)).strftime('%B')

status_counts = df["STATUS"].value_counts()
shipped = status_counts.get("Shipped", 0)
not_shipped = status_counts.sum() - shipped

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

pdf_bytes = generate_pdf()

# === Header Row ===
st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>
        <div style='font-size: 22px; font-weight: 600;'>🏢 Companies Dashboard Pvt.</div>
        <div style='font-size: 16px; text-align: right;'>
            <a href="https://your-streamlit-app-url" target="_blank" title="Share Dashboard" style="text-decoration: none; margin-right: 15px;">🔗</a>
            <a href="#" download="KPI_Summary_Report.pdf" style="text-decoration: none; margin-right: 15px;">📥</a>
            📅 {datetime.today().strftime('%Y-%m-%d')}
        </div>
    </div>
""", unsafe_allow_html=True)

# === Functional PDF download ===
st.download_button(
    label="Download KPI Summary PDF",
    data=pdf_bytes,
    file_name="KPI_Summary_Report.pdf",
    mime="application/pdf"
)
st.markdown("### 📊 Key Performance Indicators")

# === Updated Box Style with Margin ===
box_wrapper = "padding: 8px;"  # Adds space around each KPI card
box_style = """
    background-color: #fff;
    padding: 16px;
    border: 1.5px solid #cccccc;
    border-radius: 8px;
    text-align: center;
    box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
    font-size: 14px;
    height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
"""

# === Top 3 KPIs ===
top_cols = st.columns(3)
with top_cols[0]:
    st.markdown(f"<div style='{box_wrapper}'><div style='{box_style}'><h5>💰 Overall Revenue</h5><h3>£{total_revenue:,.0f}</h3></div></div>", unsafe_allow_html=True)
with top_cols[1]:
    st.markdown(f"<div style='{box_wrapper}'><div style='{box_style}'><h5>📆 Latest Month Revenue ({latest_month.strftime('%B')})</h5><h3>£{latest_month_revenue:,.0f}</h3></div></div>", unsafe_allow_html=True)
with top_cols[2]:
    st.markdown(f"<div style='{box_wrapper}'><div style='{box_style}'><h5>📈 3-Month Growth</h5><h3>{growth_rate:.2f}%</h3></div></div>", unsafe_allow_html=True)

# === Bottom 3 KPIs ===
bottom_cols = st.columns(3)
with bottom_cols[0]:
    st.markdown(f"<div style='{box_wrapper}'><div style='{box_style}'><h5>🔮 Predicted Revenue ({predicted_month_name})</h5><h3>£{next_month_prediction:,.0f}</h3></div></div>", unsafe_allow_html=True)
with bottom_cols[1]:
    st.markdown(f"<div style='{box_wrapper}'><div style='{box_style}'><h5>📦 Orders Shipped</h5><h3>{shipped}</h3></div></div>", unsafe_allow_html=True)
with bottom_cols[2]:
    st.markdown(f"<div style='{box_wrapper}'><div style='{box_style}'><h5>🚚 Orders Not Shipped</h5><h3>{not_shipped}</h3></div></div>", unsafe_allow_html=True)

st.markdown("---")

# === Client Insights Section ===
st.markdown("### 👥 Top 5 Clients")

# Split screen: Left empty, right contains table and chart
left_col, right_col = st.columns([1, 2])  # 1/3rd left, 2/3rd right

# --- Right Side: Table & Chart ---
with right_col:
    # Get top 5 clients by sales
    top_clients = (
        df.groupby(["CUSTOMERNAME", "COUNTRY"])["SALES"]
        .sum()
        .reset_index()
        .sort_values(by="SALES", ascending=False)
        .head(5)
    )

    # Rename columns for display and chart usage
    top_clients.rename(columns={
        "CUSTOMERNAME": "Customer Name",
        "SALES": "Sales",
        "COUNTRY": "Country"
    }, inplace=True)

    # Show the table
    st.markdown("#### 📋 Top 5 Clients by Sales")
    st.dataframe(top_clients, use_container_width=True)

    # Bar chart to show client performance
    st.markdown("#### 📊 Performance of Top Clients")
    fig = px.bar(
        top_clients,
        x="Customer Name",
        y="Sales",
        color="Country",
        text_auto='.2s',
        title="Sales Performance of Top 5 Clients"
    )
    st.plotly_chart(fig, use_container_width=True)

# === Sales Charts Placeholder ===
st.markdown("### 📈 Sales Charts (unchanged)")
# Example:
# fig = px.bar(df, x='PRODUCTLINE', y='SALES', title='Sales by Product Line')
# st.plotly_chart(fig, use_container_width=True)

# === Raw Data Export ===
with st.expander("⬇️ Download Raw Data"):
    st.download_button("Download CSV", data=df.to_csv(index=False), file_name="Auto_Sales_Data.csv", mime="text/csv")
