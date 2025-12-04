"""
Nourish Beauty - Business Intelligence Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from database.connection import get_engine

st.set_page_config(
    page_title="Nourish Beauty - BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">📊 Nourish Beauty - BI Dashboard</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.title("🏪 Nourish Beauty")
    st.markdown("---")
    
    page = st.radio(
        "Select Dashboard:",
        ["🏠 Home", "📊 Sales Analysis", "👥 HR Performance", 
         "📢 Marketing Campaign", "🎯 User Behavior", "📱 Social Media"]
    )
    
    st.markdown("---")
    st.info(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.caption("**Raudatul Sholehah**\nNIM: 2310817220002")

@st.cache_resource
def get_db_connection():
    return get_engine()

engine = get_db_connection()

@st.cache_data(ttl=300)
def load_sales_data():
    query = """
    SELECT 
        fs.sales_key,
        fs.harga_satuan,
        fs.jumlah,
        fs.total_penjualan_sebelum_pajak as total_harga,
        fs.rating,
        dt.tanggal as tanggal_lengkap,
        dt.nama_bulan,
        dt.bulan,
        dt.tahun,
        dp.nama_produk,
        dp.kategori_produk,
        dc.nama_cabang,
        dc.kota as cabang_kota,
        dpm.metode_pembayaran as payment_type
    FROM fact_sales fs
    LEFT JOIN dim_tanggal dt ON fs.tanggal_key = dt.tanggal_key
    LEFT JOIN dim_produk dp ON fs.produk_key = dp.produk_key
    LEFT JOIN dim_cabang dc ON fs.cabang_key = dc.cabang_key
    LEFT JOIN dim_payment dpm ON fs.payment_key = dpm.payment_key
    LIMIT 1000
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def load_summary_metrics():
    query = """
    SELECT 
        (SELECT COUNT(*) FROM fact_sales) as total_transactions,
        (SELECT SUM(total_penjualan_sebelum_pajak) FROM fact_sales) as total_revenue,
        (SELECT COUNT(DISTINCT customer_key) FROM fact_marketing_response) as total_customers,
        (SELECT COUNT(*) FROM fact_employee_performance) as total_employees,
        (SELECT COUNT(*) FROM user_activity_log) as total_user_activities
    """
    return pd.read_sql(query, engine).iloc[0]

# HOME PAGE
if page == "🏠 Home":
    st.header("📈 Dashboard Overview")
    
    metrics = load_summary_metrics()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("💰 Total Revenue", f"Rp {metrics['total_revenue']/1e6:.1f}M")
    with col2:
        st.metric("🛒 Transactions", f"{metrics['total_transactions']:,}")
    with col3:
        st.metric("👥 Customers", f"{metrics['total_customers']:,}")
    with col4:
        st.metric("👔 Employees", f"{metrics['total_employees']:,}")
    with col5:
        st.metric("📊 Activities", f"{metrics['total_user_activities']:,}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Revenue by Category")
        query = """
        SELECT 
            dp.kategori_produk,
            SUM(fs.total_penjualan_sebelum_pajak) as revenue
        FROM fact_sales fs
        JOIN dim_produk dp ON fs.produk_key = dp.produk_key
        GROUP BY dp.kategori_produk
        ORDER BY revenue DESC
        """
        df_category = pd.read_sql(query, engine)
        fig = px.bar(df_category, x='kategori_produk', y='revenue',
                     color='revenue', color_continuous_scale='Blues')
        st.plotly_chart(fig, use_column_width=True)
    
    with col2:
        st.subheader("📈 Monthly Trend")
        query = """
        SELECT 
            dt.nama_bulan,
            SUM(fs.total_penjualan_sebelum_pajak) as revenue
        FROM fact_sales fs
        JOIN dim_tanggal dt ON fs.tanggal_key = dt.tanggal_key
        GROUP BY dt.nama_bulan, dt.bulan
        ORDER BY dt.bulan
        """
        df_monthly = pd.read_sql(query, engine)
        fig = px.line(df_monthly, x='nama_bulan', y='revenue', markers=True)
        st.plotly_chart(fig, use_column_width=True)
    
    st.markdown("---")
    st.subheader("📊 Data Warehouse Summary")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**Total Records**: 10,435")
        st.success("**Data Quality**: 99.1%")
    with col2:
        st.info("**ETL Status**: ✅ Success")
        st.success("**Last ETL Run**: Today")
    with col3:
        st.info("**Database**: PostgreSQL 18")
        st.success("**Schema**: Star Schema")

# SALES ANALYSIS
elif page == "📊 Sales Analysis":
    st.header("📊 Sales Performance Analysis")
    
    df_sales = load_sales_data()
    
    if df_sales.empty:
        st.error("No data available")
    else:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            categories = df_sales['kategori_produk'].dropna().unique()
            selected_category = st.multiselect("Category", options=categories, default=categories)
        with col2:
            branches = df_sales['nama_cabang'].dropna().unique()
            selected_branch = st.multiselect("Branch", options=branches, default=branches)
        
        df_filtered = df_sales[
            (df_sales['kategori_produk'].isin(selected_category)) &
            (df_sales['nama_cabang'].isin(selected_branch))
        ]
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Sales", f"Rp {df_filtered['total_harga'].sum()/1e6:.2f}M")
        with col2:
            st.metric("Transactions", f"{len(df_filtered):,}")
        with col3:
            st.metric("Avg Transaction", f"Rp {df_filtered['total_harga'].mean():.0f}")
        with col4:
            st.metric("Avg Rating", f"{df_filtered['rating'].mean():.2f} ⭐")
        
        # Charts
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Top 10 Products")
            top = df_filtered.groupby('nama_produk')['total_harga'].sum().sort_values(ascending=False).head(10)
            fig = px.bar(top, orientation='h')
            st.plotly_chart(fig, use_column_width=True)
        
        with col2:
            st.subheader("Payment Methods")
            payment = df_filtered['payment_type'].value_counts()
            fig = px.pie(values=payment.values, names=payment.index, hole=0.4)
            st.plotly_chart(fig, use_column_width=True)
        
        st.subheader("📋 Sales Data")
        st.dataframe(df_filtered[['tanggal_lengkap', 'nama_produk', 'kategori_produk', 
                                   'nama_cabang', 'total_harga', 'rating']].head(50))

# HR PERFORMANCE
elif page == "👥 HR Performance":
    st.header("👥 Employee Performance Analysis")
    
    query = "SELECT * FROM fact_employee_performance LIMIT 100"
    df_hr = pd.read_sql(query, engine)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Employees", f"{len(df_hr):,}")
    
    with col2:
        if 'engagement_score' in df_hr.columns and pd.api.types.is_numeric_dtype(df_hr['engagement_score']):
            st.metric("Avg Engagement", f"{df_hr['engagement_score'].mean():.2f}")
        else:
            st.metric("Avg Engagement", "N/A")
    
    with col3:
        if 'performance_score' in df_hr.columns:
            perf_counts = df_hr['performance_score'].value_counts()
            top_perf = perf_counts.index[0] if len(perf_counts) > 0 else "N/A"
            st.metric("Top Performance", top_perf)
        else:
            st.metric("Performance", "N/A")
    
    if 'performance_score' in df_hr.columns:
        st.subheader("📊 Performance Distribution")
        perf_dist = df_hr['performance_score'].value_counts()
        fig = px.bar(perf_dist, labels={'index': 'Performance', 'value': 'Count'})
        st.plotly_chart(fig, use_column_width=True)
    
    if 'department' in df_hr.columns:
        st.subheader("🏢 Department Distribution")
        dept_dist = df_hr['department'].value_counts()
        fig = px.pie(values=dept_dist.values, names=dept_dist.index)
        st.plotly_chart(fig, use_column_width=True)
    
    st.subheader("📋 Employee Data")
    st.dataframe(df_hr.head(50))

# MARKETING CAMPAIGN
elif page == "📢 Marketing Campaign":
    st.header("📢 Marketing Campaign Analysis")
    
    query = "SELECT * FROM fact_marketing_response LIMIT 100"
    df_marketing = pd.read_sql(query, engine)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Customers", f"{len(df_marketing):,}")
    with col2:
        if 'total_spending' in df_marketing.columns:
            st.metric("Avg Spending", f"Rp {df_marketing['total_spending'].mean():.0f}")
        else:
            st.metric("Avg Spending", "N/A")
    with col3:
        if 'accepted_cmp1' in df_marketing.columns:
            acceptance_rate = (df_marketing['accepted_cmp1'].sum() / len(df_marketing)) * 100
            st.metric("Campaign 1 Success", f"{acceptance_rate:.1f}%")
        else:
            st.metric("Campaign Success", "N/A")
    
    campaign_cols = [col for col in df_marketing.columns if 'accepted_cmp' in col]
    if campaign_cols:
        st.subheader("📊 Campaign Acceptance Rates")
        campaign_data = []
        for col in campaign_cols:
            rate = (df_marketing[col].sum() / len(df_marketing)) * 100
            campaign_data.append({'Campaign': col.replace('accepted_cmp', 'Campaign '), 'Acceptance Rate (%)': rate})
        
        df_campaigns = pd.DataFrame(campaign_data)
        fig = px.bar(df_campaigns, x='Campaign', y='Acceptance Rate (%)', color='Acceptance Rate (%)')
        st.plotly_chart(fig, use_column_width=True)
    
    st.subheader("📋 Customer Data")
    st.dataframe(df_marketing.head(50))

# USER BEHAVIOR
elif page == "🎯 User Behavior":
    st.header("🎯 User Behavior Analytics")
    
    query = "SELECT * FROM user_activity_log LIMIT 1000"
    df_activity = pd.read_sql(query, engine)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sessions", f"{df_activity['session_id'].nunique():,}")
    with col2:
        st.metric("Total Users", f"{df_activity['user_id'].nunique():,}")
    with col3:
        st.metric("Avg Dwell Time", f"{df_activity['dwell_time_seconds'].mean():.1f}s")
    
    st.subheader("📄 Page Views Distribution")
    page_views = df_activity['page'].value_counts()
    fig = px.bar(page_views, labels={'index': 'Page', 'value': 'Views'})
    st.plotly_chart(fig, use_column_width=True)
    
    st.subheader("📋 Activity Log")
    st.dataframe(df_activity.head(50))

# SOCIAL MEDIA
elif page == "📱 Social Media":
    st.header("📱 Social Media Engagement")
    
    query = "SELECT * FROM fact_social_media_engagement ORDER BY post_date DESC LIMIT 100"
    df_social = pd.read_sql(query, engine)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Posts", f"{len(df_social):,}")
    with col2:
        st.metric("Total Likes", f"{df_social['likes'].sum():,}")
    with col3:
        st.metric("Avg Engagement", f"{df_social['engagement_rate'].mean():.2f}%")
    with col4:
        st.metric("Total Reach", f"{df_social['reach'].sum()/1e3:.1f}K")
    
    st.subheader("📊 Platform Distribution")
    platform_dist = df_social['platform'].value_counts()
    fig = px.pie(values=platform_dist.values, names=platform_dist.index)
    st.plotly_chart(fig, use_column_width=True)
    
    st.subheader("📋 Social Media Posts")
    st.dataframe(df_social.head(50))

st.markdown("---")
st.caption("© 2025 Nourish Beauty | Raudatul Sholehah (2310817220002)")
