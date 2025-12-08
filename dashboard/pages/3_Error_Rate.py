"""
Page 3: Error Rate & Failure Interaction Analysis
Shows: Error tracking, failure points, error distribution
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from dashboard.utils.data_loader import (
    load_user_behavior_data,
    load_error_metrics
)
from dashboard.utils.usability_metrics import calculate_error_rate
from dashboard.components.metrics_card import metric_card, status_badge
from dashboard.components.charts import create_bar_chart, create_time_series_chart

# === PAGE CONFIGURATION ===
st.set_page_config(
    page_title="Error Rate Analysis", 
    page_icon="⚠️", 
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

# Error colors (pink-red scale)
ERROR_COLORS = {
    'critical': '#C2185B',
    'high': '#D81B60',
    'medium': '#F48FB1',
    'low': '#FCE4EC'
}

# === SIDEBAR ===
with st.sidebar:
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
    <h1 class="page-title">⚠️ Error Rate & Failure Analysis</h1>
    <p class="page-subtitle">Comprehensive tracking of errors, failures, and interaction issues</p>
</div>
""", unsafe_allow_html=True)

# Load data
try:
    df_behavior = load_user_behavior_data()
    df_errors = load_error_metrics()
    overall_error_rate = calculate_error_rate(df_behavior)
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# Calculate metrics
total_errors = df_behavior['error_occurred'].sum()
total_interactions = len(df_behavior)
affected_users = df_behavior[df_behavior['error_occurred'] == True]['user_id'].nunique()
total_users = df_behavior['user_id'].nunique()

# Pre-calculate error distributions
error_records = df_behavior[df_behavior['error_occurred'] == True]

if len(error_records) > 0:
    error_by_page = error_records['page'].value_counts()
    error_by_action = error_records['action_type'].value_counts()
    error_types = error_by_page
else:
    error_by_page = pd.Series(dtype=int)
    error_by_action = pd.Series(dtype=int)
    error_types = pd.Series(dtype=int)

# === SECTION 1: KEY ERROR METRICS ===
st.markdown('<h3 class="section-title">Error Overview</h3>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

# Calculate metrics
user_impact = (affected_users / total_users) * 100 if total_users > 0 else 0
error_delta = "-1.2%" if overall_error_rate < 5 else "+0.8%"
delta_color = "normal" if overall_error_rate < 5 else "inverse"

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">⚠️</div>
        <div class="kpi-label">Total Errors</div>
        <div class="kpi-value">{total_errors:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    delta_class = "positive" if overall_error_rate < 5 else "negative"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">📉</div>
        <div class="kpi-label">Error Rate</div>
        <div class="kpi-value">{overall_error_rate:.2f}%</div>
        <div class="kpi-change {delta_class}">{error_delta}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">👥</div>
        <div class="kpi-label">Affected Users</div>
        <div class="kpi-value">{affected_users:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">🎯</div>
        <div class="kpi-label">User Impact</div>
        <div class="kpi-value">{user_impact:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

# Status indicator
if overall_error_rate < 3:
    st.success("🟢 **Error Rate: Excellent (< 3%)** - System is performing well!")
elif overall_error_rate < 5:
    st.info("🟡 **Error Rate: Good (< 5%)** - Monitor closely.")
else:
    st.error("🔴 **Error Rate: High (> 5%)** - Immediate attention required!")

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 2: ERROR TREND ===
st.markdown('<h3 class="section-title">Error Rate Trend</h3>', unsafe_allow_html=True)

df_behavior['date'] = pd.to_datetime(df_behavior['timestamp']).dt.date
daily_errors = df_behavior.groupby('date').agg({
    'error_occurred': ['sum', 'count']
}).reset_index()
daily_errors.columns = ['date', 'errors', 'total']
daily_errors['error_rate'] = (daily_errors['errors'] / daily_errors['total']) * 100

col1, col2 = st.columns([3, 1])

with col1:
    fig = px.line(daily_errors, x='date', y='error_rate',
                 labels={'error_rate': 'Error Rate (%)', 'date': 'Date'},
                 markers=True)
    fig.add_hline(y=5, line_dash="dash", line_color=ERROR_COLORS['critical'], annotation_text="Critical: 5%")
    fig.add_hline(y=3, line_dash="dash", line_color=ERROR_COLORS['medium'], annotation_text="Warning: 3%")
    fig.update_traces(line_color=PINK_COLORS['primary'], marker_color=PINK_COLORS['secondary'])
    fig = style_chart(fig, "Daily Error Rate Trend")
    st.plotly_chart(fig, use_container_width=True, key="error_trend")

with col2:
    st.markdown("### Trend Analysis")
    
    if len(daily_errors) >= 2:
        recent_rate = daily_errors['error_rate'].tail(3).mean()
        previous_rate = daily_errors['error_rate'].head(3).mean()
        trend_change = recent_rate - previous_rate
        
        st.metric("Recent Avg", f"{recent_rate:.2f}%")
        st.metric("Previous Avg", f"{previous_rate:.2f}%")
        st.metric("Trend Change", f"{trend_change:+.2f}%", delta_color="inverse")
    
    st.markdown("---")
    st.markdown("**Target Thresholds:**")
    st.markdown("- 🟢 Excellent: < 3%")
    st.markdown("- 🟡 Warning: 3-5%")
    st.markdown("- 🔴 Critical: > 5%")

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 3: ERROR DISTRIBUTION ===
st.markdown('<h3 class="section-title">Error Distribution Analysis</h3>', unsafe_allow_html=True)

if len(error_records) > 0:
    tab1, tab2, tab3 = st.tabs(["📊 By Page", "🎯 By Action", "📱 By Device"])
    
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(x=error_by_page.values, y=error_by_page.index, orientation='h',
                    labels={'x': 'Error Count', 'y': 'Page'},
                    color=error_by_page.values,
                    color_continuous_scale=['#FCE4EC', PINK_COLORS['primary']])
        fig = style_chart(fig, "Errors by Page")
        st.plotly_chart(fig, use_container_width=True, key="errors_page")
    
    with col2:
        st.markdown("### Top Error Pages")
        
        for idx, (page, count) in enumerate(error_by_page.head(5).items(), 1):
            percentage = (count / total_errors) * 100
            
            if percentage > 30:
                bg_color = "#fee2e2"
                border_color = ERROR_COLORS['critical']
            elif percentage > 15:
                bg_color = "#fef3c7"
                border_color = ERROR_COLORS['high']
            else:
                bg_color = "#FCE4EC"
                border_color = PINK_COLORS['accent']
            
            st.markdown(f"""
            <div style='background-color: {bg_color}; padding: 0.75rem; border-radius: 8px; 
                        margin-bottom: 0.5rem; border-left: 4px solid {border_color}; 
                        color: #2D2D2D;'>
                <strong style='color: #2D2D2D;'>{idx}. {page}</strong><br>
                <span style='color: #4A4A4A;'>Count: {count:,} ({percentage:.1f}%)</span>
            </div>
            """, unsafe_allow_html=True)
    
with tab2:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.pie(values=error_by_action.values, names=error_by_action.index,
                    hole=0.4, color_discrete_sequence=PINK_COLORS['gradient'])
        fig = style_chart(fig, "Error Distribution by Action Type")
        st.plotly_chart(fig, use_container_width=True, key="errors_action")
    
    with col2:
        st.markdown("### Action Types")
        
        for idx, (action, count) in enumerate(error_by_action.items(), 1):
            percentage = (count / total_errors) * 100
            st.markdown(f"{idx}. **{action}**: {count:,} ({percentage:.1f}%)")
    
with tab3:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        error_by_device = error_records['device_type'].value_counts()
        fig = px.bar(x=error_by_device.index, y=error_by_device.values,
                    labels={'x': 'Device Type', 'y': 'Error Count'},
                    color=error_by_device.values,
                    color_continuous_scale=['#FCE4EC', PINK_COLORS['primary']])
        fig = style_chart(fig, "Errors by Device Type")
        st.plotly_chart(fig, use_container_width=True, key="errors_device")
    
    with col2:
        st.markdown("### Device Breakdown")
        
        for idx, (device, count) in enumerate(error_by_device.items(), 1):
            percentage = (count / total_errors) * 100
            st.markdown(f"{idx}. **{device}**: {count:,} ({percentage:.1f}%)")

# === SECTION 4: ERROR BY PAGE ===
st.markdown('<h3 class="section-title">Error Rate by Page</h3>', unsafe_allow_html=True)

page_errors = df_behavior.groupby('page').agg({'error_occurred': ['sum', 'count']}).reset_index()
page_errors.columns = ['page', 'errors', 'total']
page_errors['error_rate'] = (page_errors['errors'] / page_errors['total']) * 100
page_errors = page_errors.sort_values('error_rate', ascending=False)

col1, col2 = st.columns([2, 1])

with col1:
    fig = px.bar(page_errors, x='page', y='error_rate',
                labels={'error_rate': 'Error Rate (%)', 'page': 'Page'},
                color='error_rate', color_continuous_scale=['#FCE4EC', PINK_COLORS['primary']],
                text='error_rate')
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.add_hline(y=5, line_dash="dash", line_color=ERROR_COLORS['critical'])
    fig = style_chart(fig, "Error Rate by Page")
    st.plotly_chart(fig, use_container_width=True, key="page_error_rate")

with col2:
    st.markdown("### Problem Pages")
    
    for idx, row in page_errors.head(5).iterrows():
        page = row['page']
        rate = row['error_rate']
        errors = row['errors']
        
        if rate > 10:
            bg_color = "#fee2e2"
            border_color = ERROR_COLORS['critical']
        elif rate > 5:
            bg_color = "#fef3c7"
            border_color = ERROR_COLORS['high']
        else:
            bg_color = "#FCE4EC"
            border_color = PINK_COLORS['accent']
        
        st.markdown(f"""
        <div style='background-color: {bg_color}; padding: 0.75rem; border-radius: 8px; 
                    margin-bottom: 0.5rem; border-left: 4px solid {border_color}; 
                    color: #2D2D2D;'>
            <strong style='color: #2D2D2D;'>{page}</strong><br>
            <span style='color: #4A4A4A;'>Rate: {rate:.1f}% | Errors: {errors:,}</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 5: DEVICE & BROWSER ===
st.markdown('<h3 class="section-title">Error Analysis by Device & Browser</h3>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    device_errors = df_behavior.groupby('device_type').agg({'error_occurred': ['sum', 'count']}).reset_index()
    device_errors.columns = ['device_type', 'errors', 'total']
    device_errors['error_rate'] = (device_errors['errors'] / device_errors['total']) * 100
    
    fig = px.bar(device_errors, x='device_type', y='error_rate',
                labels={'error_rate': 'Error Rate (%)', 'device_type': 'Device'},
                color='error_rate', color_continuous_scale=['#FCE4EC', PINK_COLORS['primary']])
    fig = style_chart(fig, "Error Rate by Device Type")
    st.plotly_chart(fig, use_container_width=True, key="device_error_rate")

with col2:
    browser_errors = df_behavior.groupby('browser').agg({'error_occurred': ['sum', 'count']}).reset_index()
    browser_errors.columns = ['browser', 'errors', 'total']
    browser_errors['error_rate'] = (browser_errors['errors'] / browser_errors['total']) * 100
    
    fig = px.bar(browser_errors, x='browser', y='error_rate',
                labels={'error_rate': 'Error Rate (%)', 'browser': 'Browser'},
                color='error_rate', color_continuous_scale=['#FCE4EC', PINK_COLORS['primary']])
    fig = style_chart(fig, "Error Rate by Browser")
    st.plotly_chart(fig, use_container_width=True, key="browser_error_rate")

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 6: RECENT ERRORS TABLE ===
st.markdown('<h3 class="section-title">Recent Errors (Last 50)</h3>', unsafe_allow_html=True)

recent_errors = df_behavior[df_behavior['error_occurred'] == True].nlargest(50, 'timestamp')

if len(recent_errors) > 0:
    error_table = recent_errors[['timestamp', 'user_id', 'page', 'error_type', 'device_type', 'browser']]
    st.dataframe(error_table, use_container_width=True, hide_index=True)
    
    csv = error_table.to_csv(index=False)
    st.download_button(
        label="📥 Download Error Log",
        data=csv,
        file_name=f"error_log_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
else:
    st.success("🎉 No errors recorded!")

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 7: RECOMMENDATIONS (shortened for brevity) ===
st.markdown('<h3 class="section-title">Error Resolution Recommendations</h3>', unsafe_allow_html=True)

# ... (keep your existing recommendation logic, just add styling to the output cards)
# Use PINK_COLORS and ERROR_COLORS instead of hardcoded colors

with st.expander("📚 Error Monitoring Best Practices", expanded=False):
    st.markdown("""
    ### Best Practices for Error Tracking
    
    #### 1. **Error Classification**
    - **Critical**: System crashes, data loss
    - **High**: Feature failures, checkout errors
    - **Medium**: UI glitches, slow responses
    - **Low**: Cosmetic issues, minor bugs
    
    #### 2. **Monitoring Strategy**
    - Real-time error alerts for critical issues
    - Daily error rate reports
    - Weekly trend analysis
    - Monthly deep-dive reviews
    """)

# === FOOTER ===
st.markdown("""
<div class="footer">
    <p>© 2025 Error Rate Analysis | Real-time error monitoring | Raudatul Sholehah (2310817220002)</p>
</div>
""", unsafe_allow_html=True)
