import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import calendar

st.set_page_config(layout="wide", page_title="Sales Dashboard", page_icon="📊")

st.title("Interactive Sales Dashboard")

uploaded_file = st.file_uploader("Upload your cleaned sales CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Clean column names
    df.columns = df.columns.str.strip().str.upper()

    # Check for required columns
    required_cols = ['ORDERDATE', 'SALES', 'ORDERNUMBER', 'STATUS', 'PRODUCTLINE', 'CUSTOMERNAME']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"Missing required columns: {', '.join(missing_cols)}. Please check your CSV and try again.")
        st.stop()

    # Convert ORDERDATE
    df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'], errors='coerce')

    # Drop rows with invalid dates
    df = df.dropna(subset=['ORDERDATE'])

    # Add month-year column for grouping
    df['MONTH_YEAR'] = df['ORDERDATE'].dt.to_period('M')


# Ensure ORDERDATE is in datetime
df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'])

# Create MONTH_YEAR column
df['MONTH_YEAR'] = df['ORDERDATE'].dt.to_period('M')

# Overall Revenue
overall_revenue = df['SALES'].sum()
formatted_overall_revenue = f"£{overall_revenue:,.2f}"

# Last Month
last_month = df['MONTH_YEAR'].max()
df_last_month = df[df['MONTH_YEAR'] == last_month]

# Revenue Last Month
last_month_revenue = df_last_month['SALES'].sum()
formatted_last_month_revenue = f"£{last_month_revenue:,.2f}"

# Total Orders Last Month
total_orders_last_month = df_last_month['ORDERNUMBER'].nunique()

# Shipped Orders
shipped_orders = df[df['STATUS'].str.lower() == 'shipped']['ORDERNUMBER'].nunique()

# On Hold Orders
on_hold_orders = df[df['STATUS'].str.lower() == 'on hold']['ORDERNUMBER'].nunique()

# --- Display in KPI boxes ---
st.markdown("## Executive Summary")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("💰 Overall Revenue", formatted_overall_revenue)
col2.metric("📅 Revenue Last Month", formatted_last_month_revenue)
col3.metric("🧾 Orders Last Month", total_orders_last_month)
col4.metric("✅ Shipped Orders", shipped_orders)
col5.metric("⏸️ On Hold Orders", on_hold_orders)
    # Top 5 products by revenue
    top_products = df.groupby('PRODUCTLINE')['SALES'].sum().sort_values(ascending=False).head(5).reset_index()

    # Pie chart for sales distribution by product line
    pie_data = df.groupby('PRODUCTLINE')['SALES'].sum()
    fig1, ax1 = plt.subplots()
    ax1.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=140)
    ax1.axis('equal')  # Equal aspect ratio ensures pie is drawn as a circle.

    # Country wise performance (revenue and orders)
    country_perf = df.groupby('COUNTRY').agg({'SALES': 'sum', 'ORDERNUMBER': 'nunique'}).reset_index()
    best_country = country_perf.loc[country_perf['SALES'].idxmax()]
    worst_country = country_perf.loc[country_perf['SALES'].idxmin()]

    # Customer behavior
    total_customers = df['CUSTOMERNAME'].nunique()
    top_customers = df.groupby('CUSTOMERNAME')['SALES'].sum().sort_values(ascending=False).head(5).reset_index()

    # Risk customers: top customers with no orders in last 3 months
    three_months_ago = df['ORDERDATE'].max() - pd.DateOffset(months=3)
    recent_customers = df[df['ORDERDATE'] >= three_months_ago]['CUSTOMERNAME'].unique()
    risk_customers = top_customers[~top_customers['CUSTOMERNAME'].isin(recent_customers)]

    # Forecast next month revenue (simple MoM growth average)
    monthly_totals = df.groupby('MONTH_YEAR')['SALES'].sum().reset_index()
    monthly_totals['MONTH_YEAR'] = monthly_totals['MONTH_YEAR'].dt.to_timestamp()
    monthly_totals = monthly_totals.sort_values('MONTH_YEAR')
    monthly_totals['PCT_CHANGE'] = monthly_totals['SALES'].pct_change()
    avg_growth = monthly_totals['PCT_CHANGE'].mean()

    last_month_revenue = monthly_totals.iloc[-1]['SALES']
    forecast_next_month_revenue = last_month_revenue * (1 + avg_growth)
    forecast_next_month_revenue = max(forecast_next_month_revenue, 0)  # avoid negative forecasts
    formatted_forecast = f"£{forecast_next_month_revenue:,.2f}"

    # Top 3 growth products next month forecast
    product_monthly = df.groupby(['PRODUCTLINE', 'MONTH_YEAR'])['SALES'].sum().reset_index()
    product_monthly['MONTH_YEAR'] = product_monthly['MONTH_YEAR'].dt.to_timestamp()

    growth_data = []
    products = product_monthly['PRODUCTLINE'].unique()
    for product in products:
        data = product_monthly[product_monthly['PRODUCTLINE'] == product].sort_values('MONTH_YEAR')
        if len(data) < 2:
            continue
        pct_change = (data.iloc[-1]['SALES'] - data.iloc[-2]['SALES']) / data.iloc[-2]['SALES']
        forecast = data.iloc[-1]['SALES'] * (1 + pct_change)
        growth_data.append({
            'PRODUCTLINE': product,
            'LAST_MONTH_SALES': data.iloc[-1]['SALES'],
            'PCT_GROWTH': pct_change,
            'FORECAST_NEXT_MONTH': max(forecast, 0)
        })
    growth_df = pd.DataFrame(growth_data)
    top_growth = growth_df.sort_values('PCT_GROWTH', ascending=False).head(3)

    # Display section
    st.markdown("## Executive Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Overall Revenue", formatted_overall_revenue)
    col2.metric(f"Total Orders Last Month ({last_month.strftime('%B %Y')})", total_orders_last_month)
    col3.metric("Shipped Orders", shipped_orders)
    st.metric("On Hold Orders", on_hold_orders)

    st.markdown("## Top 5 Products by Revenue")
    st.dataframe(top_products)

    st.markdown("## Sales Distribution by Product Line")
    st.pyplot(fig1)

    st.markdown("## Country Performance")
    st.write(f"Best Performing Country: **{best_country['COUNTRY']}** with £{best_country['SALES']:,.2f} revenue and {best_country['ORDERNUMBER']} orders.")
    st.write(f"Worst Performing Country: **{worst_country['COUNTRY']}** with £{worst_country['SALES']:,.2f} revenue and {worst_country['ORDERNUMBER']} orders.")
    st.dataframe(country_perf)

    st.markdown("## Customer Behavior")
    st.write(f"Total Unique Customers: {total_customers}")
    st.write("Top 5 Customers by Purchase Value:")
    st.dataframe(top_customers)
    st.write("Risk Customers (Top 5 customers with no orders in last 3 months):")
    st.dataframe(risk_customers)

    st.markdown("## Next Month Revenue Forecast")
    st.write(f"Forecasted Revenue for next month: **{formatted_forecast}** (based on average month-over-month growth of {avg_growth:.2%})")

    st.markdown("## Top 3 Growth Products and Forecast")
    st.dataframe(top_growth[['PRODUCTLINE', 'PCT_GROWTH', 'FORECAST_NEXT_MONTH']].style.format({
        'PCT_GROWTH': '{:.2%}',
        'FORECAST_NEXT_MONTH': '£{:,.2f}'
    }))

    st.markdown("### Forecast Logic Insights")
    st.write("""
    The forecast is calculated based on the average month-over-month growth rate observed historically in the sales data.
    For each product, the recent percentage change in sales is used to estimate next month's sales.
    Negative growth is capped at zero to avoid unrealistic negative sales predictions.
    """)

else:
    st.info("Please upload a CSV file to begin analysis.")
