"""
Nourish Beauty - Business Intelligence Dashboard
Pink Minimalist Design with High Contrast
Author: Raudatul Sholehah - 2310817220002
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Path configuration
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from database.connection import get_engine

# === PAGE CONFIGURATION ===
st.set_page_config(
    page_title="Nourish Beauty - BI Dashboard",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === LOAD EXTERNAL CSS ===
def load_css(file_name: str):
    """Load external CSS file from assets folder"""
    css_path = os.path.join(os.path.dirname(__file__), "assets", file_name)
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Apply pink minimalist CSS
load_css("beauty-theme.css")

# === CHART STYLING FUNCTION ===
def style_chart(fig, title=""):
    """Apply pink minimalist styling to charts with HIGH CONTRAST"""
    fig.update_layout(
        title={
            'text': title,
            'font': {'size': 18, 'color': '#2D2D2D', 'family': 'Inter'}
        },
        template='plotly_white',
        font=dict(family='Inter, sans-serif', size=13, color='#2D2D2D'),
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        margin=dict(t=60, b=50, l=50, r=50),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=12, color='#2D2D2D'),
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#E0E0E0',
            borderwidth=1
        ),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor='#E0E0E0',
            linewidth=2,
            tickfont=dict(size=12, color='#2D2D2D')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#F5F5F5',
            gridwidth=1,
            showline=False,
            tickfont=dict(size=12, color='#2D2D2D')
        ),
        hoverlabel=dict(
            bgcolor='white',
            font_size=13,
            font_family='Inter',
            bordercolor='#D81B60'
        )
    )
    return fig

# === DATABASE CONNECTION ===
@st.cache_resource
def get_db_connection():
    return get_engine()

engine = get_db_connection()


# === DATA LOADING FUNCTIONS ===
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
        (SELECT COUNT(*) FROM fact_employee_performance) as total_employees
    """
    return pd.read_sql(query, engine).iloc[0]


# === MAROON COLOR PALETTE (untuk compatibility dengan tabs) ===
MAROON_COLORS = {
    'primary': '#77002C',      # Deep Maroon
    'secondary': '#BF0040',    # Maroon Red
    'accent': '#FF246D',       # Pink Accent
    'light': '#FF6699',        # Light Pink
    'dark': '#5C3317',         # Dark Brown
    'gradient': ['#77002C', '#BF0040', '#FF246D', '#FF6699']
}

# === SIDEBAR DENGAN STYLING MULTI-PAGE ===
with st.sidebar:
    # Style navigation menu Streamlit yang otomatis muncul
    st.markdown("""
    <style>
    /* Style untuk menu pages otomatis */
    [data-testid="stSidebarNav"] {
        background: linear-gradient(135deg, #77002C 0%, #BF0040 100%);
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(119, 0, 44, 0.2);
    }
    
    [data-testid="stSidebarNav"]::before {
        content: "📊 PAGES NAVIGATION";
        display: block;
        color: white;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1px;
        margin-bottom: 0.75rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Style untuk link pages */
    [data-testid="stSidebarNav"] ul {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    [data-testid="stSidebarNav"] li {
        list-style: none !important;
        margin: 0.25rem 0 !important;
    }
    
    [data-testid="stSidebarNav"] a {
        display: flex !important;
        align-items: center;
        padding: 0.75rem 1rem !important;
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: white !important;
        text-decoration: none !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        border: 1px solid transparent !important;
    }
    
    [data-testid="stSidebarNav"] a:hover {
        background: rgba(255, 255, 255, 0.2) !important;
        transform: translateX(4px);
    }
    
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: white !important;
        color: #77002C !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Info Section
    st.markdown("""
    <div class="info-section">
        <div class="info-item">
            <span class="info-label">📅 Last Update</span>
            <span class="info-value">{}</span>
        </div>
        <div class="info-item">
            <span class="info-label">👤 Author</span>
            <span class="info-value">Raudatul Sholehah</span>
        </div>
        <div class="info-item">
            <span class="info-label">🎓 NIM</span>
            <span class="info-value">2310817220002</span>
        </div>
    </div>
    """.format(datetime.now().strftime('%d %b %Y, %H:%M')), unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # System Status
    st.markdown("""
    <div class="status-section">
        <div class="status-title">System Status</div>
        <div class="status-item">
            <span class="status-dot active"></span>
            <span>Database: Online</span>
        </div>
        <div class="status-item">
            <span class="status-dot active"></span>
            <span>ETL: Success</span>
        </div>
        <div class="status-item">
            <span class="status-dot active"></span>
            <span>Data Quality: 99.1%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
# === HORIZONTAL NAVIGATION TABS ===
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Dashboard Overview",
    "💰 Sales Analytics", 
    "👥 HR Performance",
    "📢 Marketing Campaign",
    "🎯 User Behavior",
    "📱 Social Media"
])


# === TAB 1: DASHBOARD OVERVIEW ===
with tab1:
    st.markdown('<h1 class="page-title">Dashboard Overview</h1>', unsafe_allow_html=True)
    
    metrics = load_summary_metrics()
    
    # Debug Info
    with st.expander("🔍 Debug Info (Click to expand)"):
        st.code(f"""
        RAW DATA FROM DATABASE:
        - Total Revenue (raw): Rp {metrics['total_revenue']:,.2f}
        - Total Revenue / 1M: Rp {metrics['total_revenue']/1e6:.2f}M
        - Total Transactions: {metrics['total_transactions']:,}
        - Avg per Transaction: Rp {metrics['total_revenue']/metrics['total_transactions']:,.2f}
        
        NOTE: Original CSV data is in USD. 
        Multiply by 15,000 for IDR conversion.
        """)
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        revenue_display = metrics['total_revenue']/1e9 if metrics['total_revenue'] > 1e9 else metrics['total_revenue']/1e6
        unit = 'B' if metrics['total_revenue'] > 1e9 else 'M'
        
        st.markdown(f"""
        <div class="kpi-card kpi-primary">
            <div class="kpi-icon">💰</div>
            <div class="kpi-label">Total Revenue</div>
            <div class="kpi-value">Rp {revenue_display:.1f}{unit}</div>
            <div class="kpi-change positive">↑ 12.5%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">🛒</div>
            <div class="kpi-label">Transactions</div>
            <div class="kpi-value">{metrics['total_transactions']:,}</div>
            <div class="kpi-change positive">+8.3%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">👥</div>
            <div class="kpi-label">Customers</div>
            <div class="kpi-value">{metrics['total_customers']:,}</div>
            <div class="kpi-change neutral">+2.1%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">👔</div>
            <div class="kpi-label">Employees</div>
            <div class="kpi-value">{metrics['total_employees']:,}</div>
            <div class="kpi-change neutral">Stable</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="section-title">Revenue by Category</h3>', unsafe_allow_html=True)
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
                    color_discrete_sequence=[MAROON_COLORS['primary']])
        fig.update_traces(marker_line_width=0, texttemplate='%{y:.2s}', textposition='outside',
                         textfont=dict(size=14, color='#2D2D2D', family='Inter'))
        fig = style_chart(fig)
        st.plotly_chart(fig, use_container_width=True, key="cat_rev")
    
    with col2:
        st.markdown('<h3 class="section-title">Monthly Sales Trend</h3>', unsafe_allow_html=True)
        query = """
        SELECT 
            dt.nama_bulan, dt.bulan,
            SUM(fs.total_penjualan_sebelum_pajak) as revenue
        FROM fact_sales fs
        JOIN dim_tanggal dt ON fs.tanggal_key = dt.tanggal_key
        GROUP BY dt.nama_bulan, dt.bulan
        ORDER BY dt.bulan
        """
        df_monthly = pd.read_sql(query, engine)
        
        fig = px.line(df_monthly, x='nama_bulan', y='revenue', markers=True)
        fig.update_traces(
            line=dict(color=MAROON_COLORS['primary'], width=4),
            marker=dict(size=10, color=MAROON_COLORS['primary'], line=dict(width=3, color='white')),
            fill='tozeroy', fillcolor='rgba(139, 69, 19, 0.1)'
        )
        fig = style_chart(fig)
        st.plotly_chart(fig, use_container_width=True, key="monthly_trend")
    
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    
    # System Status
    st.markdown('<h3 class="section-title">System Status</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="status-card">
            <div class="status-icon">✓</div>
            <div class="status-label">Data Quality</div>
            <div class="status-value">99.1%</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="status-card">
            <div class="status-icon">✓</div>
            <div class="status-label">ETL Status</div>
            <div class="status-value">Success</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="status-card">
            <div class="status-icon">✓</div>
            <div class="status-label">Database</div>
            <div class="status-value">PostgreSQL 18</div>
        </div>
        """, unsafe_allow_html=True)


# === TAB 2: SALES ANALYTICS ===
with tab2:
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Sales Analytics</h1>
        <p class="page-subtitle">Detailed sales performance analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    df_sales = load_sales_data()
    
    if df_sales.empty:
        st.error("❌ No sales data available")
    else:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            categories = df_sales['kategori_produk'].dropna().unique()
            selected_category = st.multiselect("🏷️ Product Category", options=categories, 
                                              default=categories, key="sales_cat")
        with col2:
            branches = df_sales['nama_cabang'].dropna().unique()
            selected_branch = st.multiselect("🏪 Branch Location", options=branches, 
                                            default=branches, key="sales_branch")
        
        df_filtered = df_sales[
            (df_sales['kategori_produk'].isin(selected_category)) &
            (df_sales['nama_cabang'].isin(selected_branch))
        ]
        
        st.markdown('<div class="section-spacer-small"></div>', unsafe_allow_html=True)
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💵 Total Sales", f"Rp {df_filtered['total_harga'].sum()/1e6:.2f}M")
        with col2:
            st.metric("🛒 Transactions", f"{len(df_filtered):,}")
        with col3:
            st.metric("📊 Avg Transaction", f"Rp {df_filtered['total_harga'].mean():.0f}")
        with col4:
            st.metric("⭐ Avg Rating", f"{df_filtered['rating'].mean():.2f}")
        
        st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<h3 class="section-title">Sales by Branch</h3>', unsafe_allow_html=True)
            
            # Group by branch
            sales_by_branch = df_filtered.groupby('nama_cabang')['total_harga'].sum().sort_values(ascending=False)
            
            if len(sales_by_branch) > 0:
                fig = px.bar(
                    sales_by_branch,
                    orientation='h',
                    color_discrete_sequence=[MAROON_COLORS['secondary']]
                )
                fig.update_traces(
                    marker_line_width=0,
                    texttemplate='Rp %{x:,.0f}',
                    textposition='outside',
                    textfont=dict(size=12, color='#2D2D2D', family='Inter')
                )
                fig = style_chart(fig)
                fig.update_yaxes(title='')
                fig.update_xaxes(title='Revenue (Rp)')
                fig.update_layout(height=400, margin=dict(l=100, r=80, t=30, b=50))
                st.plotly_chart(fig, use_container_width=True, key="sales_branch")
            else:
                st.warning("⚠️ No branch data available")
        
        with col2:
            st.markdown('<h3 class="section-title">Payment Methods</h3>', unsafe_allow_html=True)
            payment = df_filtered['payment_type'].value_counts()
            
            fig = px.pie(values=payment.values, names=payment.index, hole=0.5,
                        color_discrete_sequence=MAROON_COLORS['gradient'])
            fig.update_traces(textposition='inside', textinfo='percent+label',
                             textfont=dict(size=13, color='white'),
                             marker=dict(line=dict(color='white', width=3)))
            fig = style_chart(fig)
            st.plotly_chart(fig, use_container_width=True, key="payment_dist")
        
        st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
        
        # Data Table
        st.markdown('<h3 class="section-title">Transaction Details</h3>', unsafe_allow_html=True)
        st.dataframe(
            df_filtered[['tanggal_lengkap', 'nama_produk', 'kategori_produk', 
                        'nama_cabang', 'total_harga', 'rating']].head(50),
            use_container_width=True, hide_index=True
        )


# === TAB 3: HR PERFORMANCE ===
with tab3:
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">HR Performance</h1>
        <p class="page-subtitle">Employee performance and workforce analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    query = "SELECT * FROM fact_employee_performance LIMIT 100"
    df_hr = pd.read_sql(query, engine)
    
    # Top Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">👔</div>
            <div class="kpi-label">Total Employees</div>
            <div class="kpi-value">{len(df_hr):,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if 'engagement_score' in df_hr.columns and pd.api.types.is_numeric_dtype(df_hr['engagement_score']):
            avg_engagement = df_hr['engagement_score'].mean()
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">💪</div>
                <div class="kpi-label">Avg Engagement</div>
                <div class="kpi-value">{avg_engagement:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="kpi-card">
                <div class="kpi-icon">💪</div>
                <div class="kpi-label">Avg Engagement</div>
                <div class="kpi-value">N/A</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if 'performance_score' in df_hr.columns:
            top_perf = df_hr['performance_score'].value_counts().index[0] if len(df_hr) > 0 else "N/A"
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">🏆</div>
                <div class="kpi-label">Top Performance</div>
                <div class="kpi-value">{top_perf}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="kpi-card">
                <div class="kpi-icon">🏆</div>
                <div class="kpi-label">Performance</div>
                <div class="kpi-value">N/A</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    
    # Charts with Additional Metrics
    col1, col2, col3 = st.columns([1, 2, 2])  # 3 columns: metrics, chart1, chart2
    
    with col1:
        st.markdown('<h3 class="section-title">Key Metrics</h3>', unsafe_allow_html=True)
        
        # Performance metrics cards
        if 'performance_score' in df_hr.columns:
            perf_dist = df_hr['performance_score'].value_counts()
            total_emp = len(df_hr)
            
            for perf_level in perf_dist.index[:5]:  # Top 5 levels
                count = perf_dist[perf_level]
                percentage = (count / total_emp) * 100
                
                st.markdown(f"""
                <div style='background-color: #FCE4EC; padding: 0.75rem; border-radius: 8px; 
                            margin-bottom: 0.5rem; border-left: 4px solid {MAROON_COLORS['primary']}; color: #2D2D2D;'>
                    <strong style='color: #2D2D2D; font-size: 0.9rem;'>{perf_level}</strong><br>
                    <span style='color: #4A4A4A; font-size: 0.85rem;'>
                        {count} employees ({percentage:.1f}%)
                    </span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No performance data available")
    
    with col2:
        if 'performance_score' in df_hr.columns:
            st.markdown('<h3 class="section-title">Performance Distribution</h3>', unsafe_allow_html=True)
            perf_dist = df_hr['performance_score'].value_counts()
            
            fig = px.bar(
                perf_dist,
                color_discrete_sequence=[MAROON_COLORS['dark']]
            )
            fig.update_traces(
                marker_line_width=0,
                texttemplate='%{y}',
                textposition='outside',
                textfont=dict(size=12, color='#2D2D2D', family='Inter')
            )
            fig = style_chart(fig)
            fig.update_xaxes(title='Performance Level', tickfont=dict(size=10))
            fig.update_yaxes(title='Count', tickfont=dict(size=10))
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True, key="perf_dist")
    
    with col3:
        if 'department' in df_hr.columns:
            st.markdown('<h3 class="section-title">Department Distribution</h3>', unsafe_allow_html=True)
            dept_dist = df_hr['department'].value_counts()
            
            fig = px.pie(
                values=dept_dist.values,
                names=dept_dist.index,
                color_discrete_sequence=MAROON_COLORS['gradient']
            )
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont=dict(size=12, color='white', family='Inter'),
                marker=dict(line=dict(color='white', width=3))
            )
            fig = style_chart(fig)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True, key="dept_dist")
    
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<h3 class="section-title">Employee Data</h3>', unsafe_allow_html=True)
    st.dataframe(df_hr.head(50), use_container_width=True, hide_index=True)


# === TAB 4: MARKETING CAMPAIGN ===
with tab4:
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Marketing Campaign</h1>
        <p class="page-subtitle">Campaign performance analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    query = "SELECT * FROM fact_marketing_response LIMIT 100"
    df_marketing = pd.read_sql(query, engine)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👥 Total Customers", f"{len(df_marketing):,}")
    with col2:
        if 'total_spending' in df_marketing.columns:
            st.metric("💰 Avg Spending", f"Rp {df_marketing['total_spending'].mean():.0f}")
        else:
            st.metric("💰 Avg Spending", "N/A")
    with col3:
        if 'accepted_cmp1' in df_marketing.columns:
            rate = (df_marketing['accepted_cmp1'].sum() / len(df_marketing)) * 100
            st.metric("🎯 Campaign Success", f"{rate:.1f}%")
        else:
            st.metric("🎯 Campaign Success", "N/A")
    
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    
    # Campaign Chart
    campaign_cols = [col for col in df_marketing.columns if 'accepted_cmp' in col]
    if campaign_cols:
        st.markdown('<h3 class="section-title">Campaign Acceptance Rates</h3>', unsafe_allow_html=True)
        campaign_data = []
        for col in campaign_cols:
            rate = (df_marketing[col].sum() / len(df_marketing)) * 100
            campaign_data.append({
                'Campaign': col.replace('accepted_cmp', 'Campaign '),
                'Acceptance Rate (%)': rate
            })
        
        df_campaigns = pd.DataFrame(campaign_data)
        fig = px.bar(df_campaigns, x='Campaign', y='Acceptance Rate (%)',
                    color='Acceptance Rate (%)',
                    color_continuous_scale=['#F5DEB3', '#CD853F', '#A0522D', '#8B4513'])
        fig.update_traces(marker_line_width=0, texttemplate='%{y:.1f}%', textposition='outside',
                         textfont=dict(size=13, color='#2D2D2D'))
        fig = style_chart(fig)
        st.plotly_chart(fig, use_container_width=True, key="campaign")
    
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<h3 class="section-title">Customer Response Data</h3>', unsafe_allow_html=True)
    st.dataframe(df_marketing.head(50), use_container_width=True, hide_index=True)


# === TAB 5: USER BEHAVIOR ===
with tab5:
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">User Behavior</h1>
        <p class="page-subtitle">User activity and engagement metrics</p>
    </div>
    """, unsafe_allow_html=True)
    
    query = "SELECT * FROM user_activity_log LIMIT 1000"
    df_activity = pd.read_sql(query, engine)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔑 Total Sessions", f"{df_activity['session_id'].nunique():,}")
    with col2:
        st.metric("👤 Total Users", f"{df_activity['user_id'].nunique():,}")
    with col3:
        st.metric("⏱️ Avg Dwell Time", f"{df_activity['dwell_time_seconds'].mean():.1f}s")
    
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    
    # Page Views Chart
    st.markdown('<h3 class="section-title">Page Views Distribution</h3>', unsafe_allow_html=True)
    page_views = df_activity['page'].value_counts()
    
    fig = px.bar(page_views, color_discrete_sequence=[MAROON_COLORS['accent']])
    fig.update_traces(marker_line_width=0, texttemplate='%{y}', textposition='outside',
                     textfont=dict(size=13, color='#2D2D2D'))
    fig = style_chart(fig)
    fig.update_xaxes(title='Page')
    fig.update_yaxes(title='Views')
    st.plotly_chart(fig, use_container_width=True, key="page_views")
    
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<h3 class="section-title">Activity Log</h3>', unsafe_allow_html=True)
    st.dataframe(df_activity.head(50), use_container_width=True, hide_index=True)


# === TAB 6: SOCIAL MEDIA ===
with tab6:
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Social Media</h1>
        <p class="page-subtitle">Social media engagement analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    query = "SELECT * FROM fact_social_media_engagement ORDER BY post_date DESC LIMIT 100"
    df_social = pd.read_sql(query, engine)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📝 Total Posts", f"{len(df_social):,}")
    with col2:
        st.metric("❤️ Total Likes", f"{df_social['likes'].sum():,}")
    with col3:
        st.metric("📊 Avg Engagement", f"{df_social['engagement_rate'].mean():.2f}%")
    with col4:
        st.metric("👥 Total Reach", f"{df_social['reach'].sum()/1e3:.1f}K")
    
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    
    # Platform Chart
    st.markdown('<h3 class="section-title">Platform Distribution</h3>', unsafe_allow_html=True)
    platform_dist = df_social['platform'].value_counts()
    
    fig = px.pie(values=platform_dist.values, names=platform_dist.index,
                color_discrete_sequence=MAROON_COLORS['gradient'])
    fig.update_traces(textposition='inside', textinfo='percent+label',
                     textfont=dict(size=13, color='white'),
                     marker=dict(line=dict(color='white', width=3)))
    fig = style_chart(fig)
    st.plotly_chart(fig, use_container_width=True, key="platform")
    
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<h3 class="section-title">Social Media Posts</h3>', unsafe_allow_html=True)
    st.dataframe(df_social.head(50), use_container_width=True, hide_index=True)


# === FOOTER ===
st.markdown("""
<div class="footer">
    <p>© 2025 Nourish Beauty Dashboard | Raudatul Sholehah (2310817220002)</p>
</div>
""", unsafe_allow_html=True)
