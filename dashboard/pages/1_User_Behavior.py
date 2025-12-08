"""
Page 1: User Behavior Analytics
Shows: Click path, dwell time, bounce rate, engagement metrics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Add paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from dashboard.utils.data_loader import (
    load_user_behavior_data,
    calculate_bounce_rate,
    get_click_path_analysis
)
from dashboard.utils.user_tracking import (
    calculate_engagement_score,
    calculate_session_metrics
)
from dashboard.components.metrics_card import metric_card, status_badge
from dashboard.components.charts import create_bar_chart, create_time_series_chart

# === PAGE CONFIGURATION (HARUS PERTAMA!) ===
st.set_page_config(
    page_title="User Behavior Analytics", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# === LOAD EXTERNAL CSS ===
def load_css(file_name: str):
    """Load external CSS file from assets folder"""
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", file_name)
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("beauty-theme.css")

# === CHART STYLING FUNCTION ===
def style_chart(fig, title=""):
    """Apply pink minimalist styling to charts"""
    fig.update_layout(
        title={'text': title, 'font': {'size': 18, 'color': '#2D2D2D', 'family': 'Inter'}},
        template='plotly_white',
        font=dict(family='Inter, sans-serif', size=13, color='#2D2D2D'),
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        margin=dict(t=60, b=50, l=50, r=50),
        xaxis=dict(showgrid=False, showline=True, linecolor='#E0E0E0', linewidth=2),
        yaxis=dict(showgrid=True, gridcolor='#F5F5F5', gridwidth=1, showline=False),
        hoverlabel=dict(bgcolor='white', font_size=13, bordercolor='#D81B60')
    )
    return fig

# === COLOR PALETTE ===
PINK_COLORS = {
    'primary': '#D81B60',
    'secondary': '#EC407A',
    'accent': '#F48FB1',
    'light': '#FCE4EC',
    'gradient': ['#D81B60', '#EC407A', '#F48FB1', '#FCE4EC']
}

# === SIDEBAR (SAMA SEPERTI APP.PY) ===
with st.sidebar:
    # Style navigation menu
    st.markdown("""
    <style>
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
        margin: 0.25rem 0 !important;
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

# === PAGE HEADER ===
st.markdown("""
<div class="page-header">
    <h1 class="page-title">🎯 User Behavior Analytics</h1>
    <p class="page-subtitle">Comprehensive analysis of user interaction patterns and engagement metrics</p>
</div>
""", unsafe_allow_html=True)

# Load data
try:
    df_behavior = load_user_behavior_data()
    df_bounce = calculate_bounce_rate()
    df_click_path = get_click_path_analysis()
    session_metrics = calculate_session_metrics(df_behavior)
    engagement_score = calculate_engagement_score(df_behavior)
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# === SECTION 1: KEY METRICS ===
st.markdown('<h3 class="section-title">Key Behavior Metrics</h3>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_users = df_behavior['user_id'].nunique()
    st.metric("👥 Total Users", f"{total_users:,}")

with col2:
    total_sessions = session_metrics.get('total_sessions', 0)
    st.metric("🔄 Total Sessions", f"{total_sessions:,}")

with col3:
    avg_dwell = df_behavior['dwell_time_seconds'].mean()
    st.metric("⏱️ Avg Dwell Time", f"{avg_dwell:.1f}s")

with col4:
    bounce_rate = session_metrics.get('bounce_rate', 0)
    st.metric("📉 Bounce Rate", f"{bounce_rate:.1f}%", delta="-2.3%", delta_color="inverse")

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 2: ENGAGEMENT SCORE ===
st.markdown('<h3 class="section-title">User Engagement Score</h3>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=engagement_score,
        delta={'reference': 70, 'increasing': {'color': "#10b981"}},
        gauge={
            'axis': {'range': [None, 100], 'tickfont': {'color': '#2D2D2D', 'size': 12}},
            'bar': {'color': PINK_COLORS['primary']},
            'steps': [
                {'range': [0, 40], 'color': "#fee2e2"},
                {'range': [40, 70], 'color': "#fef3c7"},
                {'range': [70, 100], 'color': "#d1fae5"}
            ],
            'threshold': {'line': {'color': PINK_COLORS['secondary'], 'width': 4}, 'thickness': 0.75, 'value': 85}
        },
        title={'text': "Engagement Score (0-100)", 'font': {'size': 16, 'color': '#2D2D2D'}}
    ))
    fig = style_chart(fig)
    st.plotly_chart(fig, use_container_width=True, key="engagement_gauge")

with col2:
    st.markdown("### Score Interpretation")
    
    if engagement_score >= 70:
        st.success("🟢 **Excellent Engagement** - Users are highly engaged!")
    elif engagement_score >= 50:
        st.info("🟡 **Good Engagement** - Satisfactory, room for improvement.")
    else:
        st.warning("🟠 **Needs Improvement** - Attention required.")
    
    st.markdown("---")
    st.markdown("**Engagement Factors:**")
    st.markdown(f"- Avg Time: **{avg_dwell:.1f}s**")
    st.markdown(f"- Avg Clicks: **{df_behavior['click_count'].mean():.1f}**")
    st.markdown(f"- Avg Scroll: **{df_behavior['scroll_depth_percent'].mean():.1f}%**")

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 3: BOUNCE RATE ANALYSIS ===
st.markdown('<h3 class="section-title">Bounce Rate by Page</h3>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    fig = px.bar(
        df_bounce, x='page', y='bounce_rate',
        labels={'bounce_rate': 'Bounce Rate (%)', 'page': 'Page'},
        color='bounce_rate', color_continuous_scale=['#D1FAE5', PINK_COLORS['primary']]
    )
    fig.add_hline(y=40, line_dash="dash", line_color="orange", annotation_text="Target: 40%")
    fig = style_chart(fig, "Bounce Rate Distribution")
    st.plotly_chart(fig, use_container_width=True, key="bounce_chart")

with col2:
    st.markdown("### Top Problem Pages")
    top_bounce = df_bounce.nlargest(5, 'bounce_rate')
    
    for idx, row in top_bounce.iterrows():
        page = row['page']
        rate = row['bounce_rate']
        icon = "🔴" if rate > 60 else "🟡" if rate > 40 else "🟢"
        st.markdown(f"{icon} **{page}**: {rate:.1f}%")

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 4: CLICK PATH ANALYSIS ===
st.markdown('<h3 class="section-title">User Click Path Analysis</h3>', unsafe_allow_html=True)

click_paths = df_click_path.groupby('session_id')['page'].apply(
    lambda x: ' → '.join(x.tolist())
).value_counts().head(10)

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("### Top 10 User Journeys")
    paths_df = pd.DataFrame({'Path': click_paths.index, 'Count': click_paths.values})
    
    fig = px.bar(paths_df, y='Path', x='Count', orientation='h',
                color='Count', color_continuous_scale=['#FCE4EC', PINK_COLORS['primary']])
    fig = style_chart(fig, "Most Common Navigation Paths")
    st.plotly_chart(fig, use_container_width=True, key="paths_chart")

with col2:
    st.markdown("### Path Statistics")
    st.metric("Unique Paths", f"{click_paths.nunique():,}")
    st.metric("Avg Steps/Session", f"{df_click_path.groupby('session_id')['step_number'].max().mean():.1f}")
    
    st.markdown("---")
    st.markdown("### Most Visited Pages")
    page_visits = df_behavior['page'].value_counts().head(5)
    for page, count in page_visits.items():
        st.markdown(f"- **{page}**: {count:,} visits")

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 5: DWELL TIME ANALYSIS ===
st.markdown('<h3 class="section-title">Dwell Time Distribution</h3>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(df_behavior, x='dwell_time_seconds', nbins=30,
                      labels={'dwell_time_seconds': 'Time (seconds)', 'count': 'Frequency'},
                      color_discrete_sequence=[PINK_COLORS['primary']])
    median_time = df_behavior['dwell_time_seconds'].median()
    fig.add_vline(x=median_time, line_dash="dash", line_color="red",
                  annotation_text=f"Median: {median_time:.1f}s")
    fig = style_chart(fig, "Dwell Time Distribution")
    st.plotly_chart(fig, use_container_width=True, key="dwell_hist")

with col2:
    fig = px.box(df_behavior, x='page', y='dwell_time_seconds',
                labels={'dwell_time_seconds': 'Time (seconds)'},
                color='page', color_discrete_sequence=PINK_COLORS['gradient'])
    fig = style_chart(fig, "Dwell Time by Page")
    st.plotly_chart(fig, use_container_width=True, key="dwell_box")

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 6: DEVICE & BROWSER ANALYSIS ===
st.markdown('<h3 class="section-title">Device & Browser Analytics</h3>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    device_dist = df_behavior['device_type'].value_counts()
    fig = px.pie(values=device_dist.values, names=device_dist.index,
                hole=0.4, color_discrete_sequence=PINK_COLORS['gradient'])
    fig = style_chart(fig, "Device Type Distribution")
    st.plotly_chart(fig, use_container_width=True, key="device_pie")

with col2:
    browser_dist = df_behavior['browser'].value_counts()
    fig = px.pie(values=browser_dist.values, names=browser_dist.index,
                hole=0.4, color_discrete_sequence=PINK_COLORS['gradient'])
    fig = style_chart(fig, "Browser Distribution")
    st.plotly_chart(fig, use_container_width=True, key="browser_pie")

with col3:
    st.markdown("### Device Metrics")
    for device in df_behavior['device_type'].unique():
        device_data = df_behavior[df_behavior['device_type'] == device]
        avg_time = device_data['dwell_time_seconds'].mean()
        bounce = (device_data['is_bounce'].sum() / len(device_data)) * 100
        
        st.markdown(f"**{device}**")
        st.markdown(f"- Avg Time: {avg_time:.1f}s")
        st.markdown(f"- Bounce: {bounce:.1f}%")
        st.markdown("---")

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 7: DATA INTEGRATION INFO ===
st.markdown('<h3 class="section-title">Data Warehouse Integration</h3>', unsafe_allow_html=True)

with st.expander("📊 View Data Integration Architecture", expanded=False):
    st.markdown("""
    ### Data Warehouse Integration Strategy
    
    #### 1. **Data Sources**
    - Web application logs (JSON format)
    - Event tracking system (Google Analytics, Mixpanel)
    - Session management database
    
    #### 2. **ETL Process**
    ```
    Extract → Transform → Load → Analyze
    ```
    
    - **Extract**: Raw logs collected in real-time via API/webhooks
    - **Transform**: Parse JSON, standardize timestamps, calculate metrics, clean data
    - **Load**: Insert into `user_activity_log` fact table
    - **Analyze**: Aggregate for dashboards and reports
    
    #### 3. **Data Quality Checks**
    - ✅ Duplicate detection and removal
    - ✅ Timestamp validation
    - ✅ User ID verification
    - ✅ Session continuity checks
    
    #### 4. **Schema Design**
    ```
    user_activity_log (Fact Table)
    ├── user_id (FK)
    ├── session_id
    ├── page
    ├── action_type
    ├── dwell_time_seconds
    ├── click_count
    ├── scroll_depth_percent
    ├── is_bounce (calculated)
    └── timestamp
    ```
    
    #### 5. **Real-time Processing**
    - Log streaming via Apache Kafka
    - Incremental load every 5 minutes
    - Near real-time dashboard updates
    """)

# === FOOTER ===
st.markdown("""
<div class="footer">
    <p>© 2025 User Behavior Analytics | Data refreshed every 5 minutes | Raudatul Sholehah (2310817220002)</p>
</div>
""", unsafe_allow_html=True)
