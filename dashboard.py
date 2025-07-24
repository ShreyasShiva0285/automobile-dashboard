
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

st.set_page_config(page_title="Sales Dashboard", layout="wide")

# Upload CSV
st.sidebar.header("📤 Upload CSV File")
uploaded_file = st.sidebar.file_uploader("Choose a file", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Data Preprocessing
    df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'])
    df['Month'] = df['ORDERDATE'].dt.to_period('M')
    latest_month = df['Month'].max()

    # KPIs
    total_revenue = df['SALES'].sum()
    total_orders = df['ORDERNUMBER'].nunique()
    avg_order_value = total_revenue / total_orders

    shipped_orders = df[df['STATUS'] == 'Shipped'].shape[0]
    on_hold_orders = df[df['STATUS'] == 'On Hold'].shape[0]

    last_month_orders = df[df['Month'] == latest_month].shape[0]

    # Display KPIs
    st.title("📊 1080p Financial Sales Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Revenue", f"£{total_revenue:,.2f}")
    col2.metric("📦 Total Orders", total_orders)
    col3.metric("💳 Avg. Order Value", f"£{avg_order_value:,.2f}")
    col4.metric(f"📅 Orders Last Month ({latest_month})", last_month_orders)

    # Order Status
    st.markdown("### 🚚 Order Status")
    st.write(f"✅ Shipped Orders: {shipped_orders}")
    st.write(f"⏳ On Hold Orders: {on_hold_orders}")

    # Monthly Revenue
    st.markdown("### 📅 Monthly Revenue")
    monthly_revenue = df.groupby('Month')['SALES'].sum()
    st.line_chart(monthly_revenue)

    # Top 5 Products
    st.markdown("### 🏆 Top 5 Products by Revenue")
    top_products = df.groupby('PRODUCTLINE')['SALES'].sum().sort_values(ascending=False).head(5)
    st.bar_chart(top_products)

    # Pie Chart: Sales by Product Line
    st.markdown("### 🥧 Sales by Product Line")
    fig, ax = plt.subplots()
    df.groupby('PRODUCTLINE')['SALES'].sum().plot(kind='pie', ax=ax, autopct='%1.1f%%', ylabel='')
    st.pyplot(fig)

    # Country Performance
    st.markdown("### 🌍 Country-wise Revenue")
    country_rev = df.groupby('COUNTRY')['SALES'].sum().sort_values(ascending=False)
    st.dataframe(country_rev)

    # Customer Behavior
    st.markdown("### 👥 Customer Behavior")
    total_customers = df['CUSTOMERNAME'].nunique()
    st.write(f"Total Customers: {total_customers}")

    top_customers = df.groupby('CUSTOMERNAME')['SALES'].sum().sort_values(ascending=False).head(5)
    st.write("Top 5 Customers by Value")
    st.dataframe(top_customers)

    recent_orders = df.groupby('CUSTOMERNAME')['ORDERDATE'].max()
    risk_customers = recent_orders[recent_orders < (df['ORDERDATE'].max() - pd.DateOffset(months=3))]
    st.write("⚠️ Risk Customers (No Orders in Last 3 Months)")
    st.dataframe(risk_customers)

    # Forecasting
    st.markdown("### 🔮 Forecasted Revenue for Next Month")
    monthly_rev = df.groupby('Month')['SALES'].sum().sort_index()
    growth_rate = monthly_rev.pct_change().mean()
    predicted_next = monthly_rev.iloc[-1] * (1 + growth_rate)
    st.write(f"📈 Predicted Revenue: **£{predicted_next:,.2f}** (based on average MoM growth rate of {growth_rate:.2%})")

else:
    st.info("Please upload a CSV file from the sidebar to begin.")
