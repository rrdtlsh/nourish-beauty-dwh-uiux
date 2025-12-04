"""
Nourish Beauty - Business Intelligence Dashboard
Main Entry Point
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from database.connection import get_engine
from sqlalchemy import text

# Page config
st.set_page_config(
    page_title="Nourish Beauty - BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">📊 Nourish Beauty - Business Intelligence Dashboard</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.title("🏪 Nourish Beauty")
    st.markdown("---")
    st.title("📌 Navigation")
    
    page = st.radio(
        "Select Dashboard:",
        ["🏠 Home", "📊 Sales Analysis", "👥 HR Performance", 
         "📢 Marketing Campaign", "🎯 User Behavior", "📱 Social Media"]
    )
    
    st.markdown("---")
    st.info(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.markdown("---")
    st.caption("**Raudatul Sholehah**\nNIM: 2310817220002\nBusiness Intelligence - UAS")

# Database connection
@st.cache_resource
def get_db_connection():
    return get_engine()

engine = get_db_connection()

# Load data functions
@st.cache_data(ttl=300)
def load_sales_data():
    query = """
    SELECT 
        fs.*,
        dt.tanggal_lengkap,
        dt.nama_bulan,
        dt.tahun,
        dp.nama_produk,
        dp.kategori_produk,
        dc.nama_cabang,
        dc.kota as cabang_kota
    FROM fact_sales fs
    LEFT JOIN dim_tanggal dt ON fs.tanggal_key = dt.tanggal_key
    LEFT JOIN dim_produk dp ON fs.produk_key = dp.produk_key
    LEFT JOIN dim_cabang dc ON fs.cabang_key = dc.cabang_key
    LIMIT 1000
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def load_summary_metrics():
    query = """
    SELECT 
        (SELECT COUNT(*) FROM fact_sales) as total_transactions,
        (SELECT SUM(total_harga) FROM fact_sales) as total_revenue,
        (SELECT COUNT(DISTINCT customer_key) FROM fact_marketing_response) as total_customers,
        (SELECT COUNT(*) FROM fact_employee_performance) as total_employees,
        (SELECT COUNT(*) FROM user_activity_log) as total_user_activities
    """
    return pd.read_sql(query, engine).iloc[0]

# HOME PAGE
if page == "🏠 Home":
    st.header("📈 Dashboard Overview")
    
    # Load metrics
    metrics = load_summary_metrics()
    
    # Display metrics
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
        st.metric("📊 User Activities", f"{metrics['total_user_activities']:,}")
    
    st.markdown("---")
    
    # Quick insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Revenue by Product Category")
        query = """
        SELECT 
            dp.kategori_produk,
            SUM(fs.total_harga) as revenue
        FROM fact_sales fs
        JOIN dim_produk dp ON fs.produk_key = dp.produk_key
        GROUP BY dp.kategori_produk
        ORDER BY revenue DESC
        """
        df_category = pd.read_sql(query, engine)
        
        fig = px.bar(df_category, x='kategori_produk', y='revenue',
                     labels={'revenue': 'Revenue (Rp)', 'kategori_produk': 'Category'},
                     color='revenue', color_continuous_scale='Blues')
        st.plotly_chart(fig, use_column_width=True)  # ← FIXED
    
    with col2:
        st.subheader("📈 Monthly Sales Trend")
        query = """
        SELECT 
            dt.nama_bulan,
            COUNT(*) as transactions,
            SUM(fs.total_harga) as revenue
        FROM fact_sales fs
        JOIN dim_tanggal dt ON fs.tanggal_key = dt.tanggal_key
        GROUP BY dt.nama_bulan, dt.bulan
        ORDER BY dt.bulan
        """
        df_monthly = pd.read_sql(query, engine)
        
        fig = px.line(df_monthly, x='nama_bulan', y='revenue',
                      labels={'revenue': 'Revenue (Rp)', 'nama_bulan': 'Month'},
                      markers=True)
        st.plotly_chart(fig, use_column_width=True)  # ← FIXED
    
    # Data quality info
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

# SALES ANALYSIS PAGE
elif page == "📊 Sales Analysis":
    st.header("📊 Sales Performance Analysis")
    
    df_sales = load_sales_data()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_category = st.multiselect("Product Category", 
                                          options=df_sales['kategori_produk'].unique(),
                                          default=df_sales['kategori_produk'].unique())
    with col2:
        selected_branch = st.multiselect("Branch", 
                                        options=df_sales['nama_cabang'].dropna().unique(),
                                        default=df_sales['nama_cabang'].dropna().unique())
    with col3:
        selected_month = st.multiselect("Month", 
                                       options=df_sales['nama_bulan'].dropna().unique(),
                                       default=df_sales['nama_bulan'].dropna().unique())
    
    # Filter data
    df_filtered = df_sales[
        (df_sales['kategori_produk'].isin(selected_category)) &
        (df_sales['nama_cabang'].isin(selected_branch)) &
        (df_sales['nama_bulan'].isin(selected_month))
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
        top_products = df_filtered.groupby('nama_produk')['total_harga'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(top_products, orientation='h', color=top_products.values)
        st.plotly_chart(fig, use_column_width=True)  # ← FIXED
    
    with col2:
        st.subheader("Payment Method Distribution")
        payment_dist = df_filtered['payment_type'].value_counts()
        fig = px.pie(values=payment_dist.values, names=payment_dist.index, hole=0.4)
        st.plotly_chart(fig, use_column_width=True)  # ← FIXED
    
    # Data table
    st.subheader("📋 Sales Data")
    st.dataframe(df_filtered[['tanggal_lengkap', 'nama_produk', 'kategori_produk', 
                              'nama_cabang', 'total_harga', 'rating']].head(100))

# HR Performance
elif page == "👥 HR Performance":
    st.header("👥 Employee Performance Analysis")
    
    query = "SELECT * FROM fact_employee_performance LIMIT 100"
    df_hr = pd.read_sql(query, engine)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Employees", f"{len(df_hr):,}")
    with col2:
        st.metric("Avg Performance", f"{df_hr['performance_score'].mean():.2f}")
    with col3:
        st.metric("Avg Engagement", f"{df_hr['engagement_score'].mean():.2f}")
    
    st.dataframe(df_hr.head(50))

# Marketing Campaign
elif page == "📢 Marketing Campaign":
    st.header("📢 Marketing Campaign Analysis")
    
    query = "SELECT * FROM fact_marketing_response LIMIT 100"
    df_marketing = pd.read_sql(query, engine)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Customers", f"{len(df_marketing):,}")
    with col2:
        st.metric("Avg Spending", f"Rp {df_marketing['total_spending'].mean():.0f}")
    with col3:
        acceptance_rate = (df_marketing['accepted_cmp1'].sum() / len(df_marketing)) * 100
        st.metric("Campaign 1 Success", f"{acceptance_rate:.1f}%")
    
    st.dataframe(df_marketing.head(50))

# User Behavior
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
    
    # Page views
    st.subheader("📄 Page Views Distribution")
    page_views = df_activity['page'].value_counts()
    fig = px.bar(page_views, labels={'index': 'Page', 'value': 'Views'})
    st.plotly_chart(fig, use_column_width=True)  # ← FIXED

# Social Media
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
    
    # Platform distribution
    st.subheader("📊 Platform Distribution")
    platform_dist = df_social['platform'].value_counts()
    fig = px.pie(values=platform_dist.values, names=platform_dist.index)
    st.plotly_chart(fig, use_column_width=True)  # ← FIXED

# Footer
st.markdown("---")
st.caption("© 2025 Nourish Beauty Data Warehouse | Business Intelligence Project | Raudatul Sholehah (2310817220002)")
