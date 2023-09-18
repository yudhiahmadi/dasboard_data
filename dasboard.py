import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')


def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return daily_orders_df


def create_count_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english").order_id.count().sort_values(ascending=False).reset_index()
    return sum_order_items_df


def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_unique_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_unique_id": "customer_count"
    }, inplace=True)
    
    return bystate_df

def review_scores_analysis_df(df):
    # Menghitung Bintang Review
    score_reviews_order = df.groupby(by=["product_category_name_english"]).agg({
        "review_score" : "mean"
    })
    # Mengurutkan hasil secara Descending berdasarkan kolom "review_score"
    score_reviews_order = score_reviews_order.sort_values(by="review_score", ascending=False)

    # Menampilkan hasil
    return score_reviews_order

def reviews_order_df(df):
    def classify_review_score(score):
        if score >= 4:
            return "Baik"
        elif 3 <= score <= 4:
            return "Cukup"
        elif score < 3:
            return "Buruk"
        else:
            return "Lainnya"

    score_reviews_order = df.groupby(by=["product_category_name_english"]).agg({
        "review_score": "mean"
    })

    score_reviews_order = score_reviews_order.sort_values(by="review_score", ascending=False)

    score_reviews_order["review_classification"] = score_reviews_order["review_score"].apply(classify_review_score)

    classification_counts = score_reviews_order["review_classification"].value_counts()
    buruk_reviews = score_reviews_order[score_reviews_order["review_classification"] == "Buruk"]


    return classification_counts

def pembayaran_df(df):
    payment = df.groupby(by="payment_type").order_id.count()

    return payment

def revenue_df(df):
    revenue_by_state = df.groupby('customer_state')['price'].sum().sort_values(ascending=False)
 
    return revenue_by_state

def revenue_freight_df(df):
    total_revenue = df['price'].sum()
    total_freight_cost = df['freight_value'].sum()
    data = {
    'Category': ['Total Revenue', 'Total Freight Cost'],
    'Amount (R$)': [total_revenue, total_freight_cost]
    }
    rev_freig = pd.DataFrame(data)

    return rev_freig

def perbulan_df(df):
    df['month_year'] = df['order_approved_at'].dt.to_period('M')
    analisis_bulan = df.groupby('month_year').agg({
        'order_id' :'count',
        'price': 'sum',
        'freight_value': 'sum'
    }).reset_index()

    return analisis_bulan

def waktu_df(df):
    def period_of_day(hour):
        if 0 <= hour < 6:
            return 'Dini Hari'
        elif 6 <= hour < 12:
            return 'Pagi Hari'
        elif 12 <= hour < 18:
            return 'Siang Hari'
        else:
            return 'Malam Hari'

    df['period'] = df['order_approved_at'].dt.hour.apply(period_of_day)

    # Mengganti nama
    period_data = df.groupby('period').agg({
        'order_id': 'count'
    }).reindex(['Dini Hari', 'Pagi Hari', 'Siang Hari', 'Malam Hari']).reset_index()

    return period_data

def penjualan_df(df):
    penjualan_produk = df.groupby(by="product_category_name_english").order_id.count().sort_values(ascending=False)
    return penjualan_produk

def order_state_df(df):
    order_state = df.groupby(by=["customer_state"]).agg({
    "delivery_duration": "mean",
    "review_score" : "mean"
    })
    order_state_sorted = order_state.sort_values(by='delivery_duration', ascending=False)
    return order_state_sorted


def create_rfm_df(df):
    last_date = df['order_approved_at'].max() 
    recency_df = df.groupby('customer_unique_id').agg(last_purchase=('order_approved_at', 'max'))
    recency_df['Recency'] = (last_date - recency_df['last_purchase']).dt.days
    frequency_df = df.groupby('customer_unique_id').agg(Frequency=('order_id', 'nunique'))
    monetary_df = df.groupby('customer_unique_id').agg(Monetary=('price', 'sum'))
    rfm_df = pd.concat([recency_df, frequency_df, monetary_df], axis=1)

    return rfm_df

def churn_rate_df(df):
    last_date = df['order_approved_at'].max() 
    recency_df = df.groupby('customer_unique_id').agg(last_purchase=('order_approved_at', 'max'))
    recency_df['Recency'] = (last_date - recency_df['last_purchase']).dt.days
    frequency_df = df.groupby('customer_unique_id').agg(Frequency=('order_id', 'nunique'))
    monetary_df = df.groupby('customer_unique_id').agg(Monetary=('price', 'sum'))
    rfm_df = pd.concat([recency_df, frequency_df, monetary_df], axis=1)

    one_time_buyers = rfm_df[rfm_df['Frequency'] == 1].shape[0]
    total_customers = rfm_df.shape[0]
    churn_rate = (one_time_buyers / total_customers) * 100
    return churn_rate


all_df = pd.read_csv("data_gabung_latihan.csv")

datetime_columns = ["order_approved_at", "order_delivered_customer_date"]
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()
 
st.set_page_config(page_title="Y.AH Dasboard")

with st.sidebar:
    st.subheader('PT Latihan Data Belajar Analisis')
    st.image("logo.png")
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                (all_df["order_approved_at"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_count_order_items_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)
churn_rate = churn_rate_df(main_df)
review_score_df = review_scores_analysis_df(main_df)
review_order_df = reviews_order_df(main_df)
payment_df = pembayaran_df(main_df)
revenue = revenue_df(main_df)
analisis_perbulan_df = perbulan_df(main_df)
jam_waktu_df = waktu_df(main_df)
revenue_freight = revenue_freight_df(main_df)
penjualan = penjualan_df(main_df)
order_state = order_state_df(main_df)

st.title('Dasboard Data Perusahaan PT. Latihan Data Belajar Analisis')
st.header('Laporan disusun oleh Yudhi Ahmadi')

listTabs = ["Revenue", "Payment", "Customer", "Delivery", "Digital Marketing", "RFM and Churn Rate"]

whitespace = 11

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([s.center(whitespace,"\u2001") for s in listTabs])
 
with tab1:
    st.header("Peforma Penjualan dan Revenue Perusahaan")

    st.subheader("Penjualan Perhari")
    col1, col2 = st.columns(2)
 
    with col1:
        total_orders = daily_orders_df.order_count.sum()
        st.metric("Total orders", value=total_orders)
    
    with col2:
        total_revenue = format_currency(daily_orders_df.revenue.sum(), "R$", locale='es_CO') 
        st.metric("Total Revenue", value=total_revenue)
    
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(
        daily_orders_df["order_approved_at"],
        daily_orders_df["order_count"],
        marker='o', 
        linewidth=2,
        color="#90CAF9",
    )
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
    st.pyplot(fig)
    

    st.subheader("Penjualan Perbulan")
    fig, ax = plt.subplots(3, 1, figsize=(12, 15))
    analisis_perbulan_df.plot(x='month_year', y='order_id', ax=ax[0], title='Sales Quantity Monthly Analysis')
    analisis_perbulan_df.plot(x='month_year', y='price', ax=ax[1], title='Revenue Monthly Analysis')
    analisis_perbulan_df.plot(x='month_year', y='freight_value', ax=ax[2], title='Freight Cost Monthly Analysis')
    ax[1].yaxis.set_major_formatter(lambda x, _: f'R$ {x*1e-3:.0f}k')
    ax[2].yaxis.set_major_formatter(lambda x, _: f'R$ {x*1e-3:.0f}k')
    ax[0].set_xlabel(None)
    ax[1].set_xlabel(None)
    ax[2].set_xlabel(None)
    st.pyplot(fig)

    st.subheader("Pendapatan dari Berbagai State")
    fig, ax = plt.subplots(figsize=(14, 6))
    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(x=revenue.index, y=revenue.values, palette=colors)
    ax.set_title('Revenue by State')
    ax.set_xlabel('State Locations')
    ax.set_ylabel('Total Revenue (in R$)')
    st.pyplot(fig)

    st.subheader("Perbandingan Revenue dan Freight Cost")
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(data=revenue_freight, x='Category', y='Amount (R$)', palette=colors)
    ax.set_ylabel('Amount (R$)', loc="center", fontsize=10)
    ax.set_title('Total Revenue and Total Freight Cost', loc="center", fontsize=10)
    st.pyplot(fig)

    st.subheader("Rekomendasi")
    st.write('Berdasarkan analisis data yang diperoleh, penjualan meningkat seiring bertambahnya waktu, State SP sangat suka dengan produk perusahaan, dan pendapatan lebih tinggi dari freight cost yang dikeluarkan. Saya merekomendasikan untuk:')
    st.write('1. Jika kita ingin membuka cabang maka kita perlu, Membuat Riset clusterisasi ke State yang mirip karakteristiknya dengan State SP. Harapannya dengan karakteristik State yang mirip maka kebutuhan penduduknya juga mirip sehingga jika disana tidak ada perusahaan kompetitor maka kita akan menjadi top of mind penyedia kebutuhan produk di State tersebut.')
    st.write('2. Memperbaiki produk yang buruk yang sudah dipasarkan di State target perusahaan kita. Untuk itu kita perlu melakukan pengolahan ke kategori apa produk yang buruk itu dengan melihat rating score kepuasan pelanggan, dan bagaimana pelanggan menyukai produk kita. (Jawabannya ada di penjelasan selanjutnya)')

    
with tab2:
    st.header("Metode Pembayaran Pelanggan")
    fig, ax = plt.subplots(figsize=(13, 8))
    colors = ["#D3D3D3", "#72BCD4", "#D3D3D3", "#D3D3D3"]
    sns.barplot(x=payment_df.index, y=payment_df.values, palette=colors)
    ax.set_title('Metode Pembayaran', loc="center", fontsize=10)
    st.pyplot(fig)
    
    st.subheader("Rekomendasi")
    st.write('Pelanggan Lebih menyukai melakukan pembayaran menggunakan kartu kredit. dengan meningkatnya penjualan dari bulan ke bulan, kita harus melihat apakah mesin pembayaran kartu kredit ini sudah terbatas atau tidak. Kita perlu mengecek maintanance alat atau menambah alat pembayaran kartu kredit guna persiapan lonjakan pembelian yang tajam. Rekomendasi saya terhadap hal ini adalah pengadaan/peningkatan sistem pembayaran kartu kredit untuk persiapan terhadap segala kondisi. Jangan sampai pelanggan batal membeli karena masalah di pembayaran')
  
with tab3:
    st.header("Kepuasan Pelanggan")
    
    st.subheader("Distribusi Kepuasan Pelanggan")
    colors = ["#D3D3D3", "#D3D3D3", "#72BCD4"]
    fig, ax = plt.subplots(figsize=(13, 8))
    sns.histplot(data=review_score_df, x="review_score", bins=10, kde=True)
    ax.set_title("Frekuensi Review")
    st.pyplot(fig)

    st.subheader("Produk yang Perlu ditingkatkan")
    colors = ["#D3D3D3", "#D3D3D3", "#72BCD4"]
    fig, ax = plt.subplots(figsize=(13, 8))
    sns.barplot(x=review_order_df.index, y=review_order_df.values, palette=colors)
    ax.set_title("Review Produk", loc="center", fontsize=10)
    st.pyplot(fig)

    st.subheader("Kategori Produk")
    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3"]
    fig, ax = plt.subplots(figsize=(13, 15))
    sns.barplot(y=penjualan.index, x=penjualan.values, palette=colors)
    ax.set_title('Revenue oleh Product Category')
    ax.set_xlabel('Total Revenue (in R$)')
    ax.set_ylabel('Kategori Produk')
    st.pyplot(fig)

    st.subheader("Rekomendasi")
    st.write('Setelah melakukan analisis terhadap kepuasan pelanggan rata-rata pelanggan kita tergolong puas dengan rating 4-5. Disamping itu, ternyata produk yang paling banyak terjual adalah kategori bed_bath_table, dan yang paling rendah adalah security_and_service. Saya merekomendasikan')
    st.write('Membuat perbaikan produk terhadap kategori security_and_service karena rating yang buruk (dibawah 3). Jika ingin meningkatkan penjualan kita perlu memperbaiki produk ini. Atau jika perusahaan dirasa tidak mampu memperbaikinya maka kita bisa hilangkan saja karena produk ini juga terjual hanya sedikit. Hal ini tentu dilema, Namun jika tujuan awal kita adalah memenuhi kepuasan pelanggan maka kita harus memperbaiki produk tersebut hingga produk tersebut sehingga membuat rating kita naik.')

with tab4:
    st.header("Pengiriman Produk")

    st.subheader("Pengiriman PerState")
    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    fig, ax = plt.subplots(figsize=(13, 8))
    sns.barplot(data=order_state, x=order_state.index, y='delivery_duration', palette=colors)
    st.pyplot(fig)

    st.subheader("Korelasi Pengiriman dan Kepuasan Pelanggan")
    fig, ax = plt.subplots(figsize=(13, 8))
    sns.scatterplot(data=order_state, x='review_score', y='delivery_duration')
    slope, intercept, r_value, p_value, std_err = stats.linregress(order_state['review_score'], order_state['delivery_duration'])
    sns.lineplot(x=order_state['review_score'], y=slope * order_state['review_score'] + intercept, color='blue', label='Regression Line')
    corr_eqn = f'Correlation (r) = {r_value:.2f}\nEquation: y = {slope:.2f}x + {intercept:.2f}'
    plt.annotate(corr_eqn, xy=(0.05, 0.8), xycoords='axes fraction', fontsize=12, color='blue')
    st.pyplot(fig)

    st.subheader("Rekomendasi")
    st.write('Hasil Analisis Menunjukkan Pengiriman paling cepat sampai yaitu ke state RR, Bagaimana Pengiriman ini bisa cepat sampai? Kita perlu mengadopsi pengiriman state RR ke state lainnya. Hal ini karena cepatnya pengiriman mempengaruhi kepuasan pelanggan dengan korelasi -0.3 yang artinya semakin cepat pengiriman produk maka semakin puas pelanggan. Kita perlu membuat divisi khusus yang menangani pengiriman jika ingin membuat puas pelanggan, bahkan bisa mengalahkan kompetitor-kompetitor lainnya dengan perbedaan ini.')

with tab5:
    st.header("Waktu yang Tepat untuk Melakukan Iklan Promosi")
    colors = ["#D3D3D3", "#D3D3D3", "#72BCD4", "#D3D3D3",]
    fig, ax = plt.subplots(figsize=(13, 8))
    sns.barplot(data=jam_waktu_df, x='period', y='order_id', palette=colors)
    ax.set_xlabel('Waktu Pesan')
    ax.set_ylabel('Orders')
    st.pyplot(fig)

    st.subheader("Rekomendasi")
    st.write('Berbicara dari segi hal digital marketing, Kita menemukan waktu yang tepat untuk mengiklankan produk kita. Kita dapat mengurangi iklan yang muncul di waktu dini hari dan pagi hari dan mengalokasikannya ke waktu siang dan malam hari. Hal ini karena riset yang saya temukan dengan pola pelanggan yang cenderung untuk melakukan order pada siang dan malam hari. maka dari itu lebih efektif untuk menempatkan iklan di waktu tersebut guna menyasar pelanggan yang lebih banyak.')

with tab6:
    st.header("Analisis Recency, Frequency, dan Monetary")
    col1, col2 = st.columns(2)
    fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(13, 15))
    sns.histplot(rfm_df['Recency'], bins=50, ax=ax[0], kde=True).set_title('Recency Distribution')
    sns.histplot(rfm_df['Frequency'], bins=50, ax=ax[1]).set_title('Frequency Distribution')
    sns.histplot(rfm_df['Monetary'], bins=50, ax=ax[2]).set_title('Monetary Distribution')
    st.pyplot(fig)

    with col1:
        total_orders = churn_rate
        st.metric("Churn Rate (%)", value=total_orders)

    st.subheader("Rekomendasi")
    st.write('Analisis RFM menunjukkan bahwa recency pelanggan terbanyak pada 280-300 hari, frekuensi pelanggan dominan 1, dan monetary pelanggan 0-250. Saya merekomendasikan')
    st.write('1. Soal Recency kita perlu melakukan riset kenapa banyak pelanggan yang tidak membeli lagi di hari tersebut, apakah karena kompetitor lebih menarik, teknologi kurang, terrdapat produk substitusi, atau terdapat bencana alam. Hal hal tersebut perlu kita perbaiki guna mengembalikan pelanggan kita kembali.')
    st.write('2. Sedangkan rekomendasi untuk Frekuensi, Kita perlu untuk membuat member card atau kita boleh meminta izin untuk promosi produk ke pelanggan guna menarik mereka untuk berbelanja lagi ke kita. Member card dapat berisi diskon, promo beli 2 dapat 1, dan promo menarik lainnya. Dengan begitu, pelanggan yang sudah membeli produk ke kita akan tertarik lagi dengan promo-promo yang sudah kita siapkan.')
    st.write('3. Pelanggan cenderung menghabiskan uangnya pada Rdollar 0-250. kita perlu melakukan clusterisasi terhadap produk-produk yang mendukung produk lain untuk kita letakkan di rekomendasi produk yang sering dibeli oleh pelanggan. Contoh produk yang sering dibeli pelanggan adalah sikat gigi maka kita perlu meletakkan pasta gigi direkomendasi produk tersebut guna meningkatkan monetary perusahaan.')







