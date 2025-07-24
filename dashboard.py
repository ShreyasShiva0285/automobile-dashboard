import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set Seaborn style globally
sns.set_style("whitegrid")
palette = sns.color_palette("Set2")

st.set_page_config(layout="wide", page_title="Automobile Sales Dashboard", page_icon="🚗")
st.title("🚗 Automobile Sales Dashboard")

uploaded_file = st.file_uploader("Upload your cleaned sales CSV file", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    df.columns = df.columns.str.strip().str.upper().str.replace(' ', '')
    required_cols = ['SALES', 'ORDERNUMBER', 'PRODUCTLINE', 'STATUS', 'CUSTOMERNAME', 'COUNTRY', 'ORDERDATE']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"Missing required columns in the uploaded file: {', '.join(missing_cols)}")
    else:
        df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'])
        df['MONTH_YEAR'] = df['ORDERDATE'].dt.to_period('M')

        # Executive Summary KPIs with colors on deltas
        overall_revenue = df['SALES'].sum()
        last_month = df['MONTH_YEAR'].max()
        last_month_data = df[df['MONTH_YEAR'] == last_month]

        revenue_last_month = last_month_data['SALES'].sum()
        total_orders_last_month = last_month_data['ORDERNUMBER'].nunique()
        shipped_orders = df[df['STATUS'].str.lower() == 'shipped'].shape[0]
        on_hold_orders = df[df['STATUS'].str.lower() == 'on hold'].shape[0]

        # Calculate revenue growth (MoM)
        monthly_sales = df.groupby('MONTH_YEAR')['SALES'].sum().sort_index()
        sales_growth = monthly_sales.pct_change().iloc[-1] if len(monthly_sales) > 1 else 0

        st.header("Executive Summary")
        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
        kpi1.metric("Overall Revenue", f"£{overall_revenue:,.2f}")
        kpi2.metric("Revenue Last Month", f"£{revenue_last_month:,.2f}", delta=f"{sales_growth*100:.2f}%")
        kpi3.metric("Total Orders Last Month", f"{total_orders_last_month}")
        kpi4.metric("Orders Shipped", f"{shipped_orders}")
        kpi5.metric("Orders On Hold", f"{on_hold_orders}")

        # Top 5 Products by Revenue with bar chart
        st.subheader("Top 5 Products by Revenue")
        top_products = df.groupby('PRODUCTLINE')['SALES'].sum().sort_values(ascending=False).head(5).reset_index()
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        sns.barplot(data=top_products, x='SALES', y='PRODUCTLINE', palette="Set3", ax=ax2)
        ax2.set_xlabel("Sales (£)")
        ax2.set_ylabel("Product Line")
        ax2.set_title("Top 5 Products by Revenue")
        st.pyplot(fig2)
        st.dataframe(top_products.style.format({"SALES": "£{:,.2f}"}), use_container_width=True)

        # Smaller Pie Chart - Sales Distribution by Product Line
        st.subheader("Sales Distribution by Product Line")
        product_sales = df.groupby('PRODUCTLINE')['SALES'].sum()
        fig1, ax1 = plt.subplots(figsize=(5, 5))
        wedges, texts, autotexts = ax1.pie(
            product_sales, 
            labels=product_sales.index, 
            autopct='%1.1f%%', 
            startangle=140, 
            colors=palette,
            textprops={'fontsize': 10}
        )
        ax1.axis('equal')  # Equal aspect ratio ensures pie is drawn as a circle.
        plt.setp(autotexts, size=10, weight="bold", color="white")
        ax1.set_title("Sales Distribution")
        st.pyplot(fig1)

        # Country-wise performance with bar chart and table
        st.subheader("Country Performance")
        country_perf = df.groupby('COUNTRY')['SALES'].agg(['sum', 'count']).sort_values(by='sum', ascending=False).reset_index()

        fig3, ax3 = plt.subplots(figsize=(10, 4))
        sns.barplot(data=country_perf, x='COUNTRY', y='sum', palette="pastel", ax=ax3)
        ax3.set_xlabel("Country")
        ax3.set_ylabel("Total Sales (£)")
        ax3.set_title("Total Sales by Country")
        plt.xticks(rotation=45)
        st.pyplot(fig3)
        st.dataframe(country_perf.rename(columns={'sum': 'Total Sales (£)', 'count': 'Order Count'}), use_container_width=True)

        # Customer Behavior
        st.subheader("Customer Behavior")
        total_customers = df['CUSTOMERNAME'].nunique()
        top_customers = df.groupby('CUSTOMERNAME')['SALES'].sum().sort_values(ascending=False).head(5).reset_index()

        last_date = df['ORDERDATE'].max()
        three_months_ago = last_date - pd.DateOffset(months=3)
        risk_customers = []
        for customer in top_customers['CUSTOMERNAME']:
            last_order = df[df['CUSTOMERNAME'] == customer]['ORDERDATE'].max()
            if last_order < three_months_ago:
                risk_customers.append({"Customer": customer, "Last Order Date": last_order.date()})

        st.write(f"Total Customers: {total_customers}")
        st.write("Top 5 Customers by Purchase Value")
        st.dataframe(top_customers.style.format({"SALES": "£{:,.2f}"}), use_container_width=True)
        st.write("Risk Customers (No order in last 3 months)")
        st.dataframe(pd.DataFrame(risk_customers))

        # Forecast Next Month Revenue and Orders
        st.subheader("Forecast - Next Month Revenue and Orders")
        monthly_orders = df.groupby('MONTH_YEAR')['ORDERNUMBER'].nunique().sort_index()
        orders_growth = monthly_orders.pct_change().iloc[-1] if len(monthly_orders) > 1 else 0

        predicted_revenue = monthly_sales.iloc[-1] * (1 + sales_growth) if len(monthly_sales) > 0 else 0
        predicted_orders = monthly_orders.iloc[-1] * (1 + orders_growth) if len(monthly_orders) > 0 else 0

        col6, col7 = st.columns(2)
        col6.metric("Predicted Revenue Next Month", f"£{predicted_revenue:,.2f}", f"{sales_growth*100:.2f}%")
        col7.metric("Predicted Orders Next Month", f"{int(predicted_orders)}", f"{orders_growth*100:.2f}%")

        # Top 3 Growth Products (Month-over-Month %)
        st.subheader("Top 3 Growth Products (Month-over-Month %)")

        monthly_prod_sales = df.groupby(['PRODUCTLINE', 'MONTH_YEAR'])['SALES'].sum().reset_index()
        monthly_prod_sales = monthly_prod_sales.sort_values(['PRODUCTLINE', 'MONTH_YEAR'])
        monthly_prod_sales['Growth'] = monthly_prod_sales.groupby('PRODUCTLINE')['SALES'].pct_change()

        latest_month = monthly_prod_sales['MONTH_YEAR'].max()
        last_month_growth = monthly_prod_sales[monthly_prod_sales['MONTH_YEAR'] == latest_month]
        last_month_growth = last_month_growth.dropna(subset=['Growth'])
        last_month_growth['GrowthRate (%)'] = last_month_growth['Growth'] * 100
        top_growth_products = last_month_growth.sort_values('GrowthRate (%)', ascending=False).head(3)

        # Show as colored dataframe with bars
        st.dataframe(top_growth_products[['PRODUCTLINE', 'GrowthRate (%)']].style.bar(subset=['GrowthRate (%)'], color='#69b3a2'))

else:
    st.info("Please upload your cleaned sales CSV file to proceed.")
