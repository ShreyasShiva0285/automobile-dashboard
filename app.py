import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import numpy as np

st.markdown("""
    <style>
    .main {
        max-width: 1250px;
        margin-left: auto;
        margin-right: auto;
        padding: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# === Layout Styling ===
box_wrapper = "padding: 8px;"
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

# === Dummy Data for PURCHASE_CATEGORY ===
purchase_categories = ["Raw Materials", "Utilities", "Logistics", "Packaging", "Software"]
np.random.seed(42)
df["PURCHASE_CATEGORY"] = np.random.choice(purchase_categories, size=len(df))
df["PURCHASE_COST"] = df["SALES"] * np.random.uniform(0.2, 0.6, size=len(df))

# === KPI Calculations ===
df["MONTH"] = df["ORDERDATE"].dt.to_period("M")
latest_month = df["ORDERDATE"].max().to_period("M")
last_3_months = df["MONTH"].sort_values().unique()[-3:]

monthly_rev = df.groupby("MONTH")["SALES"].sum()
total_revenue = df["SALES"].sum()
latest_month_revenue = df[df["MONTH"] == latest_month]["SALES"].sum()
rev_last_3 = df[df["MONTH"].isin(last_3_months)].groupby("MONTH")["SALES"].sum()
growth_rate = ((rev_last_3.iloc[-1] - rev_last_3.iloc[0]) / rev_last_3.iloc[0]) * 100 if len(rev_last_3) == 3 else 0
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
    pdf.cell(200, 10, txt=f"Orders Shipped: {shipped:,}", ln=True)
    pdf.cell(200, 10, txt=f"Orders Not Shipped: {not_shipped:,}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

pdf_bytes = generate_pdf()

# === Header ===
st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>
        <div style='font-size: 22px; font-weight: 600;'>🏢 Companies Dashboard Pvt.</div>
        <div style='font-size: 16px; text-align: right;'>
            <a href="#" download="KPI_Summary_Report.pdf" style="text-decoration: none; margin-right: 15px;">📅 {datetime.today().strftime('%Y-%m-%d')}</a>
        </div>
    </div>
""", unsafe_allow_html=True)

st.download_button("Download KPI Summary PDF", data=pdf_bytes, file_name="KPI_Summary_Report.pdf", mime="application/pdf")
st.markdown("### 📊 Key Performance Indicators")

# === KPI Cards ===
top_cols = st.columns(3)
with top_cols[0]:
    st.markdown(f"<div style='{box_wrapper}'><div style='{box_style}'><h5>💰 Overall Revenue</h5><h3>£{total_revenue:,.0f}</h3></div></div>", unsafe_allow_html=True)
with top_cols[1]:
    st.markdown(f"<div style='{box_wrapper}'><div style='{box_style}'><h5>📆 Latest Month Revenue ({latest_month.strftime('%B')})</h5><h3>£{latest_month_revenue:,.0f}</h3></div></div>", unsafe_allow_html=True)
with top_cols[2]:
    st.markdown(f"<div style='{box_wrapper}'><div style='{box_style}'><h5>📈 3-Month Growth</h5><h3>{growth_rate:.2f}%</h3></div></div>", unsafe_allow_html=True)

bottom_cols = st.columns(3)
with bottom_cols[0]:
    st.markdown(f"<div style='{box_wrapper}'><div style='{box_style}'><h5>🔮 Predicted Revenue ({predicted_month_name})</h5><h3>£{next_month_prediction:,.0f}</h3></div></div>", unsafe_allow_html=True)
with bottom_cols[1]:
    st.markdown(f"<div style='{box_wrapper}'><div style='{box_style}'><h5>📦 Orders Shipped</h5><h3>{shipped:,}</h3></div></div>", unsafe_allow_html=True)
with bottom_cols[2]:
    st.markdown(f"<div style='{box_wrapper}'><div style='{box_style}'><h5>🚚 Orders Not Shipped</h5><h3>{not_shipped:,}</h3></div></div>", unsafe_allow_html=True)

st.markdown("---")

# === Layout: Left and Right ===
left_col, right_col = st.columns([1, 1])

with left_col:
    st.markdown("#### 🏆 Top 3 Product Lines (Last 3 Months)")
    recent_3_months = df[df["MONTH"].isin(last_3_months)]
    top_3_productlines = recent_3_months.groupby("PRODUCTLINE")["SALES"].sum().sort_values(ascending=False).head(3).reset_index()
    top_3_productlines["Total Sales"] = top_3_productlines["SALES"].apply(lambda x: f"£{x:,.0f}")
    st.dataframe(top_3_productlines[["PRODUCTLINE", "Total Sales"]].rename(columns={"PRODUCTLINE": "Product Line"}), use_container_width=True)

    st.markdown("#### ❌ Lowest-Selling Product Line & Clients")
    lowest_line = recent_3_months.groupby("PRODUCTLINE")["SALES"].sum().sort_values().head(1).reset_index()
    low_product_line = lowest_line.iloc[0]["PRODUCTLINE"]
    low_customers = recent_3_months[recent_3_months["PRODUCTLINE"] == low_product_line].groupby("CUSTOMERNAME")["SALES"].sum().reset_index()
    low_customers["Sales (£)"] = low_customers["SALES"].apply(lambda x: f"£{x:,.0f}")
    st.write(f"📉 Lowest Product Line: **{low_product_line}**")
    st.dataframe(low_customers[["CUSTOMERNAME", "Sales (£)"]].rename(columns={"CUSTOMERNAME": "Customer"}), use_container_width=True)

    st.markdown("#### 🔮 Forecast: Next Month Sales (Top Product Lines)")
    forecasted_productline = df[df["PRODUCTLINE"].isin(top_3_productlines["PRODUCTLINE"])]
    productline_forecast = forecasted_productline.groupby("PRODUCTLINE")["SALES"].mean().reset_index()
    productline_forecast["Predicted Sales"] = productline_forecast["SALES"]
    fig_forecast_pie = px.pie(
        productline_forecast,
        values="Predicted Sales",
        names="PRODUCTLINE",
        title="Next Month Forecast (Top 3 Product Lines)",
        hole=0.3
    )
    fig_forecast_pie.update_traces(textinfo='percent+label', hovertemplate='Product Line: %{label}<br>£%{value:,.0f}')
    st.plotly_chart(fig_forecast_pie, use_container_width=True)

    st.markdown("#### 💧 Cash Burn Analysis")
    recent_purchases = df[df["MONTH"].isin(last_3_months) & df["PURCHASE_CATEGORY"].notnull()]
    cash_burn = recent_purchases.groupby("PURCHASE_CATEGORY")["PURCHASE_COST"].sum().sort_values(ascending=False).reset_index()
    cash_burn["Burn (£)"] = cash_burn["PURCHASE_COST"].apply(lambda x: f"£{x:,.0f}")
    st.dataframe(cash_burn[["PURCHASE_CATEGORY", "Burn (£)"]], use_container_width=True)

    fig_burn = px.area(
        recent_purchases.groupby(["MONTH", "PURCHASE_CATEGORY"])["PURCHASE_COST"].sum().reset_index(),
        x="MONTH",
        y="PURCHASE_COST",
        color="PURCHASE_CATEGORY",
        title="Cash Burn Trend by Category (Last 3 Months)"
    )
    fig_burn.update_traces(hovertemplate='%{x}<br>%{color}: £%{y:,.0f}')
    st.plotly_chart(fig_burn, use_container_width=True)

with right_col:
    st.markdown("#### 🧑‍💼 Top 5 Clients (By Sales)")
    top_clients = df.groupby(["CUSTOMERNAME", "COUNTRY"])["SALES"].sum().sort_values(ascending=False).head(5).reset_index()
    top_clients["Total Sales (£)"] = top_clients["SALES"].apply(lambda x: f"£{x:,.0f}")
    st.dataframe(top_clients[["CUSTOMERNAME", "COUNTRY", "Total Sales (£)"]].rename(columns={"CUSTOMERNAME": "Client", "COUNTRY": "Country"}), use_container_width=True)

    st.markdown("#### 📊 Top 5 Clients: Sales Performance")
    fig = px.bar(
        top_clients,
        x="CUSTOMERNAME",
        y="SALES",
        color="COUNTRY",
        title="Sales Performance of Top 5 Clients"
    )
    fig.update_traces(hovertemplate='Client: %{x}<br>Sales: £%{y:,.0f}')
    st.plotly_chart(fig, use_container_width=True)

# === Raw Export ===
st.markdown("### 📁 Export Raw Data")
with st.expander("⬇️ Download Raw Data"):
    st.download_button("Download CSV", data=df.to_csv(index=False), file_name="Auto_Sales_Data.csv", mime="text/csv")
