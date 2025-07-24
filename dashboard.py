import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

st.set_page_config(layout="wide", page_title="Sales Dashboard 1080p")

st.title("📊 Sales Performance Dashboard")

uploaded_file = st.file_uploader("Upload your cleaned sales CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Clean and prepare data
    df.columns = df.columns.str.upper()
    df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'])
    df['MONTH_YEAR'] = df['ORDERDATE'].dt.to_period('M')

    # --- Executive Summary Metrics ---
    st.markdown("## Executive Summary")

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

    # Display KPI metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("💰 Overall Revenue", formatted_overall_revenue)
    col2.metric("🗕️ Revenue Last Month", formatted_last_month_revenue)
    col3.metric("🧾 Orders Last Month", total_orders_last_month)
    col4.metric("✅ Shipped Orders", shipped_orders)
    col5.metric("⏸️ On Hold Orders", on_hold_orders)

    # --- Top Products by Revenue ---
    st.markdown("## Top 5 Products by Revenue")
    top_products = df.groupby('PRODUCTLINE')['SALES'].sum().sort_values(ascending=False).head(5).reset_index()
    st.dataframe(top_products)

    # --- Pie Chart: Sales by Product Line ---
    st.markdown("## Sales Distribution by Product Line")
    pie_data = df.groupby('PRODUCTLINE')['SALES'].sum().sort_values(ascending=False)
    fig1, ax1 = plt.subplots()
    ax1.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    st.pyplot(fig1)

    # --- Country Performance ---
    st.markdown("## Country-wise Performance")
    country_sales = df.groupby('COUNTRY')['SALES'].sum().sort_values(ascending=False).reset_index()
    st.dataframe(country_sales)

    best_country = country_sales.iloc[0]
    worst_country = country_sales.iloc[-1]
    st.success(f"Best Performing Country: {best_country['COUNTRY']} (£{best_country['SALES']:,.2f})")
    st.error(f"Lowest Performing Country: {worst_country['COUNTRY']} (£{worst_country['SALES']:,.2f})")

    # --- Customer Insights ---
    st.markdown("## Customer Insights")
    total_customers = df['CUSTOMERNAME'].nunique()
    top_customers = df.groupby('CUSTOMERNAME')['SALES'].sum().sort_values(ascending=False).head(5).reset_index()
    recent_orders = df.groupby('CUSTOMERNAME')['ORDERDATE'].max().reset_index()
    risk_customers = recent_orders[recent_orders['ORDERDATE'] < (df['ORDERDATE'].max() - pd.DateOffset(months=3))]
    risk_customers = risk_customers[risk_customers['CUSTOMERNAME'].isin(top_customers['CUSTOMERNAME'])]

    st.write(f"Total Unique Customers: {total_customers}")
    st.write("Top 5 Customers by Purchase Value:")
    st.dataframe(top_customers)

    if not risk_customers.empty:
        st.warning("Risk Customers (Top buyers with no orders in last 3 months):")
        st.dataframe(risk_customers)

    # --- Forecasting Next Month Revenue ---
    st.markdown("## Forecast: Next Month Revenue")
    monthly_sales = df.groupby('MONTH_YEAR')['SALES'].sum().sort_index()
    monthly_growth = monthly_sales.pct_change().dropna()
    avg_growth = monthly_growth.mean()
    predicted_revenue = monthly_sales.iloc[-1] * (1 + avg_growth)

    st.write(f"Predicted Revenue for Next Month: £{predicted_revenue:,.2f}")
    st.write(f"Average Monthly Growth Rate: {avg_growth * 100:.2f}%")

    # --- Top 3 Growth Products ---
    st.markdown("## Top 3 Growth Products")
    df['MONTH'] = df['ORDERDATE'].dt.to_period('M')
    latest_month = df['MONTH'].max()
    previous_month = latest_month - 1

    current_sales = df[df['MONTH'] == latest_month].groupby('PRODUCTLINE')['SALES'].sum()
    past_sales = df[df['MONTH'] == previous_month].groupby('PRODUCTLINE')['SALES'].sum()
    growth = ((current_sales - past_sales) / past_sales).dropna().sort_values(ascending=False).head(3)
    growth_df = growth.reset_index().rename(columns={'SALES': 'GrowthRate'})
    growth_df['GrowthRate'] = growth_df[0] * 100
    st.dataframe(growth_df[['PRODUCTLINE', 'GrowthRate']])

else:
    st.info("👆 Upload your cleaned CSV file to begin dashboard analysis.")
