import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import plotly.graph_objects as go

st.markdown("""
    <style>
    .main {
        max-width: 1150px;
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
df = pd.read_csv("Auto Sales data Cleaned.csv", parse_dates=["ORDERDATE"])
df.columns = df.columns.str.strip()
df["ORDERDATE"] = pd.to_datetime(df["ORDERDATE"])
df["EST_PROFIT"] = (df["MSRP"] - df["PRICEEACH"]) * df["QUANTITYORDERED"]
df["MONTH"] = df["ORDERDATE"].dt.to_period("M")

# === KPI Calculations ===
total_revenue = df["SALES"].sum()
latest_month = df["ORDERDATE"].max().to_period("M")
latest_month_revenue = df[df["ORDERDATE"].dt.to_period("M") == latest_month]["SALES"].sum()

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
    pdf.cell(200, 10, txt=f"Orders Shipped: {shipped:,}", ln=True)
    pdf.cell(200, 10, txt=f"Orders Not Shipped: {not_shipped:,}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

pdf_bytes = generate_pdf()

# === Header ===
st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>
        <div style='font-size: 22px; font-weight: 600;'>🏢 Companies Dashboard Pvt.</div>
        <div style='font-size: 16px; text-align: right;'>
            <a href="#" target="_blank" title="Share Dashboard" style="text-decoration: none; margin-right: 15px;">🔗</a>
            <a href="#" download="KPI_Summary_Report.pdf" style="text-decoration: none; margin-right: 15px;">🗕️</a>
            🗓️ {datetime.today().strftime('%Y-%m-%d')}
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

left_col_1, right_col_1 = st.columns(2)
left_col_1, right_col_1 = st.columns(2)

with right_col_1:
    st.markdown("#### 🏆 Top 3 Product Lines (Last 3 Months)")
    recent_3_months = df[df["MONTH"].isin(last_3_months)]
    top_3_productlines = recent_3_months.groupby("PRODUCTLINE")["SALES"].sum().sort_values(ascending=False).head(3).reset_index()
    top_3_productlines["Total Sales"] = top_3_productlines["SALES"].apply(lambda x: f"£{x:,.0f}")
    st.dataframe(top_3_productlines[["PRODUCTLINE", "Total Sales"]].rename(columns={"PRODUCTLINE": "Product Line"}), use_container_width=True)

   
with left_col_1:
    st.markdown("#### 💵 Gross & Net Profit Analysis (Last 3 Months)")

    profit_df = df[df["MONTH"].isin(last_3_months)].copy()
    profit_df["GROSS_PROFIT"] = (profit_df["MSRP"] - profit_df["PRICEEACH"]) * profit_df["QUANTITYORDERED"]
    profit_df["NET_PROFIT"] = profit_df["SALES"] - profit_df["RAW_MATERIAL_COST"] - profit_df["OPERATING_EXPENSES"]

    monthly_profit = profit_df.groupby("MONTH").agg({
        "GROSS_PROFIT": "sum",
        "NET_PROFIT": "sum"
    }).reset_index()

    monthly_profit["MONTH"] = monthly_profit["MONTH"].astype(str)
    monthly_profit["Gross Profit (£)"] = monthly_profit["GROSS_PROFIT"].apply(lambda x: f"£{x:,.0f}")
    monthly_profit["Net Profit (£)"] = monthly_profit["NET_PROFIT"].apply(lambda x: f"£{x:,.0f}")
    display_profit = monthly_profit[["MONTH", "Gross Profit (£)", "Net Profit (£)"]].rename(columns={"MONTH": "Month"})

    st.dataframe(display_profit, use_container_width=True)
    total_net_profit = monthly_profit["NET_PROFIT"].sum()
    st.markdown(f"### 🧾 Total Net Profit (Last 3 Months): **£{total_net_profit:,.0f}**")

    # Waterfall Chart for Net Profit over 3 months

# Prepare values for Waterfall chart
x_vals = monthly_profit["MONTH"].astype(str).tolist()
y_vals = monthly_profit["NET_PROFIT"].tolist()

# Create Waterfall chart using go
waterfall_fig = go.Figure(go.Waterfall(
    name="Net Profit",
    orientation="v",
    x=x_vals,
    y=y_vals,
    text=[f"£{val:,.0f}" for val in y_vals],
    textposition="outside",
    connector={"line": {"color": "gray"}},
))

waterfall_fig.update_layout(
    title="📉 Net Profit Walk (Last 3 Months)",
    yaxis_title="Net Profit (£)",
    waterfallgap=0.3,
    margin=dict(t=50, b=30)
)

st.plotly_chart(waterfall_fig, use_container_width=True)

# 🔍 Insights Section
st.markdown("### 🔍 Insights on Net Profit Walk")
insights = [
    "📈 Strong profit recovery in the final month suggests improved cost control or revenue boost.",
    "💸 Mid-period dip likely due to elevated operating expenses or lower sales.",
    "🧮 Consistent cash flow with actionable patterns for forecasting future months."
]
for point in insights:
    st.markdown(f"- {point}")

left_col_2, right_col_2 = st.columns(2)

with right_col_2:
    st.markdown("#### 💸 Cash Burn Analysis (Last 3 Months)")
    if "PURCHASE_CATEGORY" in df.columns and "OPERATING_EXPENSES" in df.columns:
        recent_purchases = df[df["MONTH"].isin(last_3_months) & df["PURCHASE_CATEGORY"].notnull()]
        recent_purchases = recent_purchases.rename(columns={"OPERATING_EXPENSES": "CASH_BURN"})

        top_3_categories = (
            recent_purchases.groupby("PURCHASE_CATEGORY")["CASH_BURN"]
            .sum()
            .sort_values(ascending=False)
            .head(3)
            .reset_index()
        )
        top_3_categories["Total (£)"] = top_3_categories["CASH_BURN"].apply(lambda x: f"£{x:,.0f}")
        st.dataframe(
            top_3_categories[["PURCHASE_CATEGORY", "Total (£)"]].rename(columns={"PURCHASE_CATEGORY": "Category"}),
            use_container_width=True
        )

        burn_trend = (
            recent_purchases.groupby(["MONTH", "PURCHASE_CATEGORY"])["CASH_BURN"]
            .sum()
            .reset_index()
        )
        burn_trend["MONTH"] = burn_trend["MONTH"].astype(str)

        fig = px.bar(
            burn_trend[burn_trend["PURCHASE_CATEGORY"].isin(top_3_categories["PURCHASE_CATEGORY"])],
            x="MONTH",
            y="CASH_BURN",
            color="PURCHASE_CATEGORY",
            barmode="group",
            title="📊 Monthly Cash Burn by Category (Top 3)",
            labels={"CASH_BURN": "Expense (£)", "MONTH": "Month"},
            text_auto=".2s"
        )
        fig.update_layout(yaxis_title="Expense (£)", xaxis_title="Month")
        fig.update_traces(
            texttemplate='£%{y:,.0f}',
            hovertemplate='Month: %{x}<br>Category: %{legendgroup}<br>Expense: £%{y:,.0f}'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("PURCHASE_CATEGORY or OPERATING_EXPENSES column not found in data.")

with left_col_2:
    st.markdown("#### 🧑‍💼 Top 5 Clients (By Sales)")
    top_clients = (
        df.groupby(["CUSTOMERNAME", "COUNTRY"])["SALES"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )
    top_clients["Total Sales (£)"] = top_clients["SALES"].apply(lambda x: f"£{x:,.0f}")
    st.dataframe(
        top_clients[["CUSTOMERNAME", "COUNTRY", "Total Sales (£)"]]
        .rename(columns={"CUSTOMERNAME": "Client", "COUNTRY": "Country"}),
        use_container_width=True
    )

    st.markdown("#### 📊 Top 5 Clients: Sales Performance")
    fig = px.bar(
        top_clients,
        x="CUSTOMERNAME",
        y="SALES",
        color="COUNTRY",
        title="Sales Performance of Top 5 Clients",
        text="SALES"
    )
    fig.update_traces(
        hovertemplate='Client: %{x}<br>Sales: £%{y:,.0f}',
        texttemplate='£%{y:,.0f}'
    )
    fig.update_layout(xaxis_title="Client", yaxis_title="Sales (£)")
    st.plotly_chart(fig, use_container_width=True)

# === Export Option ===
st.markdown("### 📁 Export Raw Data")
with st.expander("⬇️ Download Raw Data"):
    st.download_button("Download CSV", data=df.to_csv(index=False), file_name="Auto_Sales_Data.csv", mime="text/csv")
