import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(layout='wide')

st.header('Dashboard Analisis E - Commerce Public')

customers = pd.read_csv('./Data/customers_dataset.csv', encoding='latin1')
sellers = pd.read_csv('./Data/sellers_dataset.csv',
                      encoding='latin1', encoding_errors='replace')
products = pd.read_csv('./Data/products_dataset.csv',
                       encoding='latin1', encoding_errors='replace')
translation = pd.read_csv('./Data/product_category_name_translation.csv',
                          encoding='latin1', encoding_errors='replace')
orders = pd.read_csv('./Data/orders_dataset.csv',
                     encoding='latin1', encoding_errors='replace')
orderReviews = pd.read_csv(
    './Data/order_reviews_dataset.csv', encoding='latin1')
orderPayments = pd.read_csv(
    './Data/order_payments_dataset.csv', encoding='latin1', encoding_errors='replace')
orderItems = pd.read_csv('./Data/order_items_dataset.csv',
                         encoding='latin1', encoding_errors='replace')

mapping = dict(zip(translation.product_category_name,
               translation.product_category_name_english))
products.product_category_name = products.product_category_name.map(
    mapping).fillna(products.product_category_name)

columns = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date',
           'order_delivered_customer_date', 'order_estimated_delivery_date']
for column in columns:
    orders[column] = pd.to_datetime(orders[column], format='%d/%m/%Y %H:%M', errors='coerce')

ordersCustomers = pd.merge(left=orders, right=customers, how='left', left_on='customer_id', right_on='customer_id')

ordersProducts = pd.merge(left=orderItems, right=products, how='left', left_on='product_id', right_on='product_id')

orderCustomerProduct = pd.merge(left=ordersCustomers, right=ordersProducts, how='left', left_on='order_id', right_on='order_id')

orderReviewPayment = pd.merge(left=orderReviews, right=orderPayments, how='left', left_on='order_id', right_on='order_id')

ordersAll = pd.merge(left=orderCustomerProduct, right=orderReviewPayment, how='left', left_on='order_id', right_on='order_id')

col1, col2 = st.columns(2)
with col1:
    st.subheader('Jumlah Pesanan berdasarkan Kota Pelanggan')
    orderCustomerCity = ordersCustomers.groupby(by='customer_city').order_id.nunique().sort_values(ascending=False).head(10).reset_index()

    plt.figure(figsize=(12, 7))
    sns.barplot(x='customer_city', y='order_id', data=orderCustomerCity)
    plt.xlabel('Customer City')
    plt.ylabel('Total Orders')
    plt.xticks(rotation=30)
    st.pyplot(plt)

with col2:
    st.subheader('Jumlah Keterlambatan Pesanan')
    shipmentTime = orders.order_estimated_delivery_date - orders.order_delivered_customer_date
    shipmentTime = shipmentTime.apply(lambda x: x.total_seconds())
    orders['shipmentTime'] = round(shipmentTime / 86400)

    orders['lateShipment'] = orders.shipmentTime.apply(
        lambda x: 'Late' if x < 0 else 'On Time')

    plt.figure(figsize=(12, 7.8))
    sns.countplot(x='lateShipment', data=orders)
    plt.xlabel('Category')
    plt.ylabel('Total Orders')
    st.pyplot(plt)

cityFilter = st.selectbox('Pilih Kota', ['None'] + list(orderCustomerCity.customer_city.unique()))

if cityFilter == 'None':
    filterOrders = ordersAll
else:
    filterOrders = ordersAll.loc[ordersAll.customer_city == cityFilter]

st.subheader('Kategori Produk yang Laris')
orderCategory = filterOrders.groupby(by='product_category_name').order_id.nunique(
).sort_values(ascending=False).head(10).reset_index()
plt.figure(figsize=(8, 4))
sns.barplot(x='product_category_name', y='order_id', data=orderCategory)
plt.xlabel('Kategori')
plt.ylabel('Total Orders')
plt.xticks(rotation=45)
st.pyplot(plt)

st.subheader('Jumlah Pesanan berdasarkan Status Pesanan')
orderStatus = filterOrders.groupby(by='order_status').order_id.nunique(
).sort_values(ascending=False).reset_index()

plt.figure(figsize=(12, 8))
sns.barplot(x='order_status', y='order_id', data=orderStatus)
plt.xlabel('Order Status')
plt.ylabel('Total Orders')
st.pyplot(plt)

st.subheader('Distribusi Score Review')
orderReview = filterOrders.groupby(by='review_score').order_id.nunique(
).sort_values(ascending=False).reset_index()

plt.figure(figsize=(12, 8))
sns.barplot(x='review_score', y='order_id', data=orderReview)
plt.xlabel('Score Review')
plt.ylabel('Total Orders')
st.pyplot(plt)

st.subheader('Distribusi Jumlah Pesanan berdasarkan Metode Pembayaran')
orderPayment = filterOrders.groupby(by='payment_type').agg({
    'order_id': 'nunique',
    'payment_value': 'mean'
}).sort_values(by='order_id', ascending=False).reset_index()

plt.figure(figsize=(12, 8))
sns.barplot(x='payment_type', y='order_id', data=orderPayment)
plt.xlabel('Payment Type')
plt.ylabel('Total Orders')
st.pyplot(plt)