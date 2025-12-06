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

# Page config
st.set_page_config(page_title="User Behavior Analytics", page_icon="🎯", layout="wide")

# Header
st.markdown("""
<h1 style='text-align: center; color: #667eea;'>
    🎯 User Behavior Analytics
</h1>
<p style='text-align: center; color: #6b7280;'>
    Comprehensive analysis of user interaction patterns and engagement metrics
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# Load data
try:
    df_behavior = load_user_behavior_data()
    df_bounce = calculate_bounce_rate()
    df_click_path = get_click_path_analysis()
    session_metrics = calculate_session_metrics(df_behavior)
    engagement_score = calculate_engagement_score(df_behavior)
    
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# === SECTION 1: KEY METRICS ===
st.subheader("📊 Key Behavior Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_users = df_behavior['user_id'].nunique()
    metric_card("Total Users", f"{total_users:,}", icon="👥")

with col2:
    total_sessions = session_metrics.get('total_sessions', 0)
    metric_card("Total Sessions", f"{total_sessions:,}", icon="🔄")

with col3:
    avg_dwell = df_behavior['dwell_time_seconds'].mean()
    metric_card("Avg Dwell Time", f"{avg_dwell:.1f}s", icon="⏱️")

with col4:
    bounce_rate = session_metrics.get('bounce_rate', 0)
    delta_color = "inverse" if bounce_rate < 40 else "normal"
    metric_card("Bounce Rate", f"{bounce_rate:.1f}%", delta="-2.3%", delta_color=delta_color, icon="📉")

st.markdown("---")

# === SECTION 2: ENGAGEMENT SCORE ===
st.subheader("🎯 User Engagement Score")

col1, col2 = st.columns([2, 1])

with col1:
    # Engagement gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=engagement_score,
        delta={'reference': 70, 'increasing': {'color': "#10b981"}},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#667eea"},
            'steps': [
                {'range': [0, 40], 'color': "#fee2e2"},
                {'range': [40, 70], 'color': "#fef3c7"},
                {'range': [70, 100], 'color': "#d1fae5"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 85
            }
        },
        title={'text': "Engagement Score (0-100)"}
    ))
    
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_column_width=True)

with col2:
    st.markdown("### Score Interpretation")
    
    if engagement_score >= 70:
        status_badge("excellent", "🟢 Excellent Engagement")
        st.success("Users are highly engaged with the platform!")
    elif engagement_score >= 50:
        status_badge("good", "🟡 Good Engagement")
        st.info("Engagement is satisfactory, room for improvement.")
    else:
        status_badge("warning", "🟠 Needs Improvement")
        st.warning("User engagement needs attention.")
    
    st.markdown("---")
    st.markdown("**Engagement Factors:**")
    st.markdown(f"- Avg Time: {avg_dwell:.1f}s")
    st.markdown(f"- Avg Clicks: {df_behavior['click_count'].mean():.1f}")
    st.markdown(f"- Avg Scroll: {df_behavior['scroll_depth_percent'].mean():.1f}%")

st.markdown("---")

# === SECTION 3: BOUNCE RATE ANALYSIS ===
st.subheader("📉 Bounce Rate by Page")

col1, col2 = st.columns([2, 1])

with col1:
    # Bar chart for bounce rates
    fig = px.bar(
        df_bounce,
        x='page',
        y='bounce_rate',
        title="Bounce Rate Distribution",
        labels={'bounce_rate': 'Bounce Rate (%)', 'page': 'Page'},
        color='bounce_rate',
        color_continuous_scale='Reds'
    )
    fig.add_hline(y=40, line_dash="dash", line_color="orange", 
                  annotation_text="Target: 40%")
    st.plotly_chart(fig, use_column_width=True)

with col2:
    st.markdown("### Top Problem Pages")
    
    top_bounce = df_bounce.nlargest(5, 'bounce_rate')
    
    for idx, row in top_bounce.iterrows():
        page = row['page']
        rate = row['bounce_rate']
        
        if rate > 60:
            icon = "🔴"
        elif rate > 40:
            icon = "🟡"
        else:
            icon = "🟢"
        
        st.markdown(f"{icon} **{page}**: {rate:.1f}%")

st.markdown("---")

# === SECTION 4: CLICK PATH ANALYSIS ===
st.subheader("🖱️ User Click Path Analysis")

# Most common paths
click_paths = df_click_path.groupby('session_id')['page'].apply(
    lambda x: ' → '.join(x.tolist())
).value_counts().head(10)

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("### Top 10 User Journeys")
    
    paths_df = pd.DataFrame({
        'Path': click_paths.index,
        'Count': click_paths.values
    })
    
    fig = px.bar(
        paths_df,
        y='Path',
        x='Count',
        orientation='h',
        title="Most Common Navigation Paths",
        color='Count',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig, use_column_width=True)

with col2:
    st.markdown("### Path Statistics")
    st.metric("Unique Paths", f"{click_paths.nunique():,}")
    st.metric("Avg Steps per Session", f"{df_click_path.groupby('session_id')['step_number'].max().mean():.1f}")
    
    st.markdown("---")
    st.markdown("### Most Visited Pages")
    
    page_visits = df_behavior['page'].value_counts().head(5)
    for page, count in page_visits.items():
        st.markdown(f"- **{page}**: {count:,} visits")

st.markdown("---")

# === SECTION 5: DWELL TIME ANALYSIS ===
st.subheader("⏱️ Dwell Time Distribution")

col1, col2 = st.columns(2)

with col1:
    # Histogram of dwell times
    fig = px.histogram(
        df_behavior,
        x='dwell_time_seconds',
        nbins=30,
        title="Dwell Time Distribution",
        labels={'dwell_time_seconds': 'Time (seconds)', 'count': 'Frequency'},
        color_discrete_sequence=['#667eea']
    )
    fig.add_vline(x=df_behavior['dwell_time_seconds'].median(), 
                  line_dash="dash", line_color="red",
                  annotation_text=f"Median: {df_behavior['dwell_time_seconds'].median():.1f}s")
    st.plotly_chart(fig, use_column_width=True)

with col2:
    # Box plot by page
    fig = px.box(
        df_behavior,
        x='page',
        y='dwell_time_seconds',
        title="Dwell Time by Page",
        labels={'dwell_time_seconds': 'Time (seconds)'},
        color='page'
    )
    st.plotly_chart(fig, use_column_width=True)

st.markdown("---")

# === SECTION 6: DEVICE & BROWSER ANALYSIS ===
st.subheader("📱 Device & Browser Analytics")

col1, col2, col3 = st.columns(3)

with col1:
    # Device distribution
    device_dist = df_behavior['device_type'].value_counts()
    fig = px.pie(
        values=device_dist.values,
        names=device_dist.index,
        title="Device Type Distribution",
        hole=0.4,
        color_discrete_sequence=['#667eea', '#764ba2', '#3b82f6']
    )
    st.plotly_chart(fig, use_column_width=True)

with col2:
    # Browser distribution
    browser_dist = df_behavior['browser'].value_counts()
    fig = px.pie(
        values=browser_dist.values,
        names=browser_dist.index,
        title="Browser Distribution",
        hole=0.4
    )
    st.plotly_chart(fig, use_column_width=True)

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

st.markdown("---")

# === SECTION 7: DATA INTEGRATION INFO ===
st.subheader("🔗 How Data Warehouse Integrates User Activity Logs")

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
    - **Transform**: 
        - Parse JSON logs
        - Standardize timestamps (UTC)
        - Calculate derived metrics (bounce, engagement)
        - Clean and validate data (remove bot traffic)
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
st.markdown("---")
st.caption("📊 User Behavior Analytics | Data refreshed every 5 minutes | Raudatul Sholehah (2310817220002)")
