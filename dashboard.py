
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

st.set_page_config(page_title="Sales Dashboard", layout="wide")

st.sidebar.header("📤 Upload CSV File")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Convert dates and create Month
    df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'])
    df['Month'] = df['ORDERDATE'].dt.to_period('M')
    latest_month = df['Month'].max()
    previous_month = df['Month'].sort_values().unique()[-2]

    # Currency formatting helper
    def format_currency(x): return f"£{x:,.2f}"

    # Overall Revenue
    total_revenue = df['SALES'].sum()
    total_orders = df['ORDERNUMBER'].nunique()
    avg_order_value = total_revenue / total_orders

    # Shipment Status
    shipped = df[df['STATUS'] == 'Shipped']['ORDERNUMBER'].nunique()
    on_hold = df[df['STATUS'] == 'On Hold']['ORDERNUMBER'].nunique()
    cancelled = df[df['STATUS'] == 'Cancelled']['ORDERNUMBER'].nunique()

    # Last Month Orders
    last_month_orders = df[df['Month'] == latest_month]['ORDERNUMBER'].nunique()

    # KPIs
    st.title("📊 1080p Sales Dashboard Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Revenue", format_currency(total_revenue))
    col2.metric("📦 Total Orders", total_orders)
    col3.metric("💳 Avg. Order Value", format_currency(avg_order_value))
    col4.metric(f"🗓 Orders in {latest_month}", last_month_orders)

    st.markdown("### 🚚 Shipment Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("✅ Shipped", shipped)
    col2.metric("⏳ On Hold", on_hold)
    col3.metric("❌ Cancelled", cancelled)

    # Monthly Revenue Chart
    st.markdown("### 📅 Monthly Revenue")
    monthly_revenue = df.groupby('Month')['SALES'].sum()
    st.line_chart(monthly_revenue)

    # Top 5 Products
    st.markdown("### 🏆 Top 5 Products by Revenue")
    top_products = df.groupby('PRODUCTLINE')['SALES'].sum().sort_values(ascending=False).head(5)
    st.bar_chart(top_products)

    # Pie Chart: Sales Distribution
    st.markdown("### 🥧 Sales by Product Line")
    fig1, ax1 = plt.subplots()
    df.groupby('PRODUCTLINE')['SALES'].sum().plot(kind='pie', ax=ax1, autopct='%1.1f%%', ylabel='')
    st.pyplot(fig1)

    # Country Performance
    st.markdown("### 🌍 Country-wise Revenue Performance")
    country_revenue = df.groupby('COUNTRY')['SALES'].sum().sort_values(ascending=False)
    best_country = country_revenue.idxmax()
    worst_country = country_revenue.idxmin()
    st.write(f"📈 Best Performing: {best_country} ({format_currency(country_revenue.max())})")
    st.write(f"📉 Least Performing: {worst_country} ({format_currency(country_revenue.min())})")
    st.dataframe(country_revenue)

    # Customer Behaviour
    st.markdown("### 👥 Customer Behavior Analysis")
    total_customers = df['CUSTOMERNAME'].nunique()
    top_customers = df.groupby('CUSTOMERNAME')['SALES'].sum().sort_values(ascending=False).head(5)
    last_order = df.groupby('CUSTOMERNAME')['ORDERDATE'].max()
    latest_date = df['ORDERDATE'].max()
    risk_customers = last_order[(latest_date - last_order) > pd.Timedelta(days=90)].loc[top_customers.index]

    st.write(f"Total Customers: {total_customers}")
    st.write("Top 5 Customers by Value")
    st.dataframe(top_customers)
    st.write("⚠️ Risk Customers (Top customers with no order in last 3 months):")
    st.dataframe(risk_customers)

    # Forecasting
    st.markdown("### 🔮 Next Month Forecast")
    growth_rate = monthly_revenue.pct_change().mean()
    next_month_prediction = monthly_revenue.iloc[-1] * (1 + growth_rate)
    predicted_orders = last_month_orders * (1 + growth_rate)

    st.write(f"Expected Revenue Next Month: **{format_currency(next_month_prediction)}**")
    st.write(f"Expected Orders Next Month: **{int(predicted_orders)}**")
    st.write(f"Confidence based on Avg. MoM Growth: **{growth_rate:.2%}**")

    # Top 3 Growth Products
    st.markdown("### 📈 Top 3 Growth Products")
    monthly_product_sales = df.groupby(['Month', 'PRODUCTLINE'])['SALES'].sum().reset_index()
    last_month_sales = monthly_product_sales[monthly_product_sales['Month'] == latest_month]
    prev_month_sales = monthly_product_sales[monthly_product_sales['Month'] == previous_month]

    merged = pd.merge(last_month_sales, prev_month_sales, on='PRODUCTLINE', suffixes=('_latest', '_prev'))
    merged['Growth'] = (merged['SALES_latest'] - merged['SALES_prev']) / merged['SALES_prev']
    top_growth = merged.sort_values(by='Growth', ascending=False).head(3)

    st.dataframe(top_growth[['PRODUCTLINE', 'Growth']])
    st.markdown("Growth is calculated as percentage increase in sales from previous month to latest.")
else:
    st.info("Please upload a CSV file from the sidebar to begin.")
