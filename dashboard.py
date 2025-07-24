import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide", page_title="Automobile Sales Dashboard", page_icon="🚗")
st.title("🚗 Automobile Sales Dashboard")

uploaded_file = st.file_uploader("Upload your cleaned sales CSV file", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Normalize column names: strip spaces, uppercase, remove spaces inside
    df.columns = df.columns.str.strip().str.upper().str.replace(' ', '')

    # Show columns detected (debug)
    st.write("Columns in uploaded CSV:", df.columns.tolist())

    required_cols = ['SALES', 'ORDERNUMBER', 'PRODUCTLINE', 'STATUS', 'CUSTOMERNAME', 'COUNTRY', 'ORDERDATE']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"Missing required columns in the uploaded file: {', '.join(missing_cols)}")
    else:
        # Convert ORDERDATE to datetime
        df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'])
        df['MONTH_YEAR'] = df['ORDERDATE'].dt.to_period('M')

        st.header("Executive Summary")
        # KPIs
        overall_revenue = df['SALES'].sum()
        last_month = df['MONTH_YEAR'].max()
        last_month_data = df[df['MONTH_YEAR'] == last_month]

        revenue_last_month = last_month_data['SALES'].sum()
        total_orders_last_month = last_month_data['ORDERNUMBER'].nunique()
        shipped_orders = df[df['STATUS'] == 'Shipped'].shape[0]
        on_hold_orders = df[df['STATUS'] == 'On Hold'].shape[0]

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Overall Revenue", f"£{overall_revenue:,.2f}")
        col2.metric("Revenue Last Month", f"£{revenue_last_month:,.2f}")
        col3.metric("Total Orders Last Month", f"{total_orders_last_month}")
        col4.metric("Orders Shipped", f"{shipped_orders}")
        col5.metric("Orders On Hold", f"{on_hold_orders}")

        # Top 5 Products by Revenue
        st.subheader("Top 5 Products by Revenue")
        top_products = df.groupby('PRODUCTLINE')['SALES'].sum().sort_values(ascending=False).head(5).reset_index()
        st.dataframe(top_products)

        # Pie Chart - Sales by Product Line
        st.subheader("Sales Distribution by Product Line")
        product_sales = df.groupby('PRODUCTLINE')['SALES'].sum()
        fig1, ax1 = plt.subplots()
        ax1.pie(product_sales, labels=product_sales.index, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        st.pyplot(fig1)

        # Country-wise performance
        st.subheader("Country Performance")
        country_perf = df.groupby('COUNTRY')['SALES'].agg(['sum', 'count']).sort_values(by='sum', ascending=False)
        st.dataframe(country_perf)

        # Customer Behavior
        st.subheader("Customer Behavior")
        total_customers = df['CUSTOMERNAME'].nunique()
        top_customers = df.groupby('CUSTOMERNAME')['SALES'].sum().sort_values(ascending=False).head(5).reset_index()

        # Risk customers = no orders in last 3 months
        last_date = df['ORDERDATE'].max()
        three_months_ago = last_date - pd.DateOffset(months=3)
        risk_customers = []
        for customer in top_customers['CUSTOMERNAME']:
            last_order = df[df['CUSTOMERNAME'] == customer]['ORDERDATE'].max()
            if last_order < three_months_ago:
                risk_customers.append({"Customer": customer, "Last Order Date": last_order.date()})

        st.write(f"Total Customers: {total_customers}")
        st.write("Top 5 Customers by Purchase Value")
        st.dataframe(top_customers)
        st.write("Risk Customers (No order in last 3 months)")
        st.dataframe(pd.DataFrame(risk_customers))

        # Forecast Next Month Revenue and Orders
        st.subheader("Forecast - Next Month Revenue and Orders")
        monthly_sales = df.groupby('MONTH_YEAR')['SALES'].sum().sort_index()
        monthly_orders = df.groupby('MONTH_YEAR')['ORDERNUMBER'].nunique().sort_index()

        # Calculate MoM growth
        sales_growth = monthly_sales.pct_change().iloc[-1]
        orders_growth = monthly_orders.pct_change().iloc[-1]

        predicted_revenue = monthly_sales.iloc[-1] * (1 + sales_growth)
        predicted_orders = monthly_orders.iloc[-1] * (1 + orders_growth)

        col6, col7 = st.columns(2)
        col6.metric("Predicted Revenue Next Month", f"£{predicted_revenue:,.2f}", f"{sales_growth*100:.2f}%")
        col7.metric("Predicted Orders Next Month", f"{int(predicted_orders)}", f"{orders_growth*100:.2f}%")

        # Top 3 Growth Products
        st.subheader("Top 3 Growth Products (Month-over-Month %)")

        # Calculate product growth correctly
        monthly_prod_sales = df.groupby(['PRODUCTLINE', 'MONTH_YEAR'])['SALES'].sum().reset_index()
        monthly_prod_sales = monthly_prod_sales.sort_values(['PRODUCTLINE', 'MONTH_YEAR'])
        monthly_prod_sales['Growth'] = monthly_prod_sales.groupby('PRODUCTLINE')['SALES'].pct_change()

        # Get latest month data
        latest_month = monthly_prod_sales['MONTH_YEAR'].max()
        last_month_growth = monthly_prod_sales[monthly_prod_sales['MONTH_YEAR'] == latest_month]
        last_month_growth = last_month_growth.dropna(subset=['Growth'])
        last_month_growth['GrowthRate (%)'] = last_month_growth['Growth'] * 100
        top_growth_products = last_month_growth.sort_values('GrowthRate (%)', ascending=False).head(3)

        st.dataframe(top_growth_products[['PRODUCTLINE', 'GrowthRate (%)']])
else:
    st.info("Please upload your cleaned sales CSV file to proceed.")
