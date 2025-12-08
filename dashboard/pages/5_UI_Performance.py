"""
Page 5: UI/UX Performance Trend
Shows: Historical trends, dashboard usage patterns, performance metrics
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
    load_dashboard_usage,
    load_usability_scores
)
from dashboard.components.metrics_card import metric_card, status_badge
from dashboard.components.charts import create_time_series_chart, create_bar_chart

# === PAGE CONFIGURATION ===
st.set_page_config(
    page_title="UI/UX Performance", 
    page_icon="📈", 
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
    <h1 class="page-title">📈 UI/UX Performance Trend</h1>
    <p class="page-subtitle">Historical performance tracking and dashboard usage analytics</p>
</div>
""", unsafe_allow_html=True)

# Load data
try:
    df_dashboard = load_dashboard_usage()
    df_usability = load_usability_scores()
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# === SECTION 1: DASHBOARD USAGE OVERVIEW ===
st.markdown('<h3 class="section-title">Dashboard Usage Overview</h3>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

total_users = df_dashboard['user_id'].nunique()
total_sessions = df_dashboard['session_id'].nunique()
avg_time = df_dashboard['time_spent_seconds'].mean()
total_interactions = df_dashboard['interaction_count'].sum()

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">👥</div>
        <div class="kpi-label">Total Users</div>
        <div class="kpi-value">{total_users:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">🔄</div>
        <div class="kpi-label">Total Sessions</div>
        <div class="kpi-value">{total_sessions:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">⏱️</div>
        <div class="kpi-label">Avg Session Time</div>
        <div class="kpi-value">{avg_time:.0f}s</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">🖱️</div>
        <div class="kpi-label">Total Interactions</div>
        <div class="kpi-value">{total_interactions:,}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 2: USAGE TREND ===
st.markdown('<h3 class="section-title">Dashboard Usage Trend</h3>', unsafe_allow_html=True)

df_dashboard['usage_date'] = pd.to_datetime(df_dashboard['usage_date'])
daily_usage = df_dashboard.groupby('usage_date').agg({
    'user_id': 'nunique',
    'visit_count': 'sum',
    'time_spent_seconds': 'mean',
    'interaction_count': 'mean'
}).reset_index()

col1, col2 = st.columns([3, 1])

with col1:
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_usage['usage_date'], y=daily_usage['user_id'],
        mode='lines+markers', name='Daily Users',
        line=dict(color=PINK_COLORS['primary'], width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_usage['usage_date'], y=daily_usage['visit_count'],
        mode='lines+markers', name='Total Visits',
        yaxis='y2',
        line=dict(color=PINK_COLORS['secondary'], width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        yaxis=dict(title="Users", titlefont=dict(color=PINK_COLORS['primary'])),
        yaxis2=dict(title="Visits", overlaying='y', side='right', 
                   titlefont=dict(color=PINK_COLORS['secondary'])),
        hovermode='x unified',
        height=400
    )
    
    fig = style_chart(fig, "Daily Usage Metrics")
    st.plotly_chart(fig, use_container_width=True, key="usage_trend")

with col2:
    st.markdown("### Trend Summary")
    
    if len(daily_usage) >= 7:
        recent_avg = daily_usage['user_id'].tail(7).mean()
        previous_avg = daily_usage['user_id'].head(7).mean()
        trend_pct = ((recent_avg - previous_avg) / previous_avg) * 100 if previous_avg > 0 else 0
        
        st.metric("Recent Avg Users", f"{recent_avg:.0f}")
        st.metric("Previous Avg", f"{previous_avg:.0f}")
        st.metric("Trend", f"{trend_pct:+.1f}%")
        
        st.markdown("---")
        
        if trend_pct > 5:
            st.success("🟢 **Growing**")
        elif trend_pct > 0:
            st.info("🟡 **Stable**")
        else:
            st.warning("🔴 **Declining**")

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 3: PAGE POPULARITY ===
st.markdown('<h3 class="section-title">Dashboard Page Popularity</h3>', unsafe_allow_html=True)

page_metrics = df_dashboard.groupby('dashboard_page').agg({
    'visit_count': 'sum',
    'time_spent_seconds': 'mean',
    'interaction_count': 'mean',
    'user_id': 'nunique'
}).reset_index()
page_metrics = page_metrics.sort_values('visit_count', ascending=False)

col1, col2 = st.columns([2, 1])

with col1:
    fig = px.bar(page_metrics, x='dashboard_page', y='visit_count',
                labels={'visit_count': 'Total Visits', 'dashboard_page': 'Page'},
                color='visit_count',
                color_continuous_scale=['#FCE4EC', PINK_COLORS['primary']],
                text='visit_count')
    fig.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig = style_chart(fig, "Total Visits by Page")
    st.plotly_chart(fig, use_container_width=True, key="page_visits")

with col2:
    st.markdown("### Top Pages")
    
    for idx, row in page_metrics.head(5).iterrows():
        page = row['dashboard_page']
        visits = row['visit_count']
        users = row['user_id']
        
        st.markdown(f"""
        <div style='background-color: #FCE4EC; padding: 0.75rem; border-radius: 8px; 
                    margin-bottom: 0.5rem; border-left: 4px solid {PINK_COLORS['primary']}; color: #2D2D2D;'>
            <strong style='color: #2D2D2D;'>{page}</strong><br>
            <span style='color: #4A4A4A;'>Visits: {visits:,} | Users: {users:,}</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 4: ENGAGEMENT METRICS ===
st.markdown('<h3 class="section-title">User Engagement Metrics</h3>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(page_metrics, x='dashboard_page', y='time_spent_seconds',
                labels={'time_spent_seconds': 'Avg Time (seconds)', 'dashboard_page': 'Page'},
                color='time_spent_seconds',
                color_continuous_scale=['#FCE4EC', PINK_COLORS['primary']])
    fig = style_chart(fig, "Avg Time Spent per Page")
    st.plotly_chart(fig, use_container_width=True, key="page_time")

with col2:
    fig = px.bar(page_metrics, x='dashboard_page', y='interaction_count',
                labels={'interaction_count': 'Avg Interactions', 'dashboard_page': 'Page'},
                color='interaction_count',
                color_continuous_scale=['#FCE4EC', PINK_COLORS['secondary']])
    fig = style_chart(fig, "Avg Interactions per Page")
    st.plotly_chart(fig, use_container_width=True, key="page_interactions")

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 5: FEATURE USAGE ===
st.markdown('<h3 class="section-title">Feature Usage Analysis</h3>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

filter_usage = (df_dashboard['filter_used'].sum() / len(df_dashboard)) * 100
export_rate = (df_dashboard[df_dashboard['export_count'] > 0].shape[0] / len(df_dashboard)) * 100
error_rate = (df_dashboard['error_encountered'].sum() / len(df_dashboard)) * 100

with col1:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=filter_usage,
        title={'text': "Filter Usage (%)", 'font': {'size': 16, 'color': '#2D2D2D'}},
        gauge={
            'axis': {'range': [None, 100], 'tickfont': {'size': 12, 'color': '#2D2D2D'}},
            'bar': {'color': PINK_COLORS['primary']},
            'steps': [
                {'range': [0, 30], 'color': "#fee2e2"},
                {'range': [30, 60], 'color': "#fef3c7"},
                {'range': [60, 100], 'color': "#d1fae5"}
            ]
        }
    ))
    fig = style_chart(fig)
    st.plotly_chart(fig, use_container_width=True, key="filter_gauge")

with col2:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=export_rate,
        title={'text': "Export Usage (%)", 'font': {'size': 16, 'color': '#2D2D2D'}},
        gauge={
            'axis': {'range': [None, 100], 'tickfont': {'size': 12, 'color': '#2D2D2D'}},
            'bar': {'color': PINK_COLORS['secondary']},
            'steps': [
                {'range': [0, 20], 'color': "#fee2e2"},
                {'range': [20, 50], 'color': "#fef3c7"},
                {'range': [50, 100], 'color': "#d1fae5"}
            ]
        }
    ))
    fig = style_chart(fig)
    st.plotly_chart(fig, use_container_width=True, key="export_gauge")

with col3:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=error_rate,
        title={'text': "Error Rate (%)", 'font': {'size': 16, 'color': '#2D2D2D'}},
        gauge={
            'axis': {'range': [None, 10], 'tickfont': {'size': 12, 'color': '#2D2D2D'}},
            'bar': {'color': '#ef4444'},
            'steps': [
                {'range': [0, 3], 'color': "#d1fae5"},
                {'range': [3, 5], 'color': "#fef3c7"},
                {'range': [5, 10], 'color': "#fee2e2"}
            ]
        }
    ))
    fig = style_chart(fig)
    st.plotly_chart(fig, use_container_width=True, key="error_gauge")

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 6: USABILITY SCORE TREND ===
st.markdown('<h3 class="section-title">Usability Score Historical Trend</h3>', unsafe_allow_html=True)

if not df_usability.empty:
    df_usability['evaluation_date'] = pd.to_datetime(df_usability['evaluation_date'])
    usability_trend = df_usability.groupby('evaluation_date').agg({
        'overall_score': 'mean',
        'sus_score': 'mean',
        'satisfaction_rating': 'mean'
    }).reset_index()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=usability_trend['evaluation_date'], y=usability_trend['overall_score'],
            mode='lines+markers', name='Overall Score',
            line=dict(color=PINK_COLORS['primary'], width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=usability_trend['evaluation_date'], y=usability_trend['sus_score'] / 20,
            mode='lines+markers', name='SUS Score (scaled)',
            line=dict(color=PINK_COLORS['secondary'], width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=usability_trend['evaluation_date'], y=usability_trend['satisfaction_rating'],
            mode='lines+markers', name='Satisfaction',
            line=dict(color=PINK_COLORS['accent'], width=3)
        ))
        
        fig.update_layout(yaxis_title="Score (0-5)", hovermode='x unified', height=400)
        fig = style_chart(fig, "Usability Metrics Over Time")
        st.plotly_chart(fig, use_container_width=True, key="usability_trend")
    
    with col2:
        st.markdown("### Current Scores")
        
        current_overall = df_usability['overall_score'].mean()
        current_sus = df_usability['sus_score'].mean()
        current_satisfaction = df_usability['satisfaction_rating'].mean()
        
        st.metric("Overall Score", f"{current_overall:.2f}/5")
        st.metric("SUS Score", f"{current_sus:.1f}/100")
        st.metric("Satisfaction", f"{current_satisfaction:.2f}/5")
        
        st.markdown("---")
        
        if current_sus >= 80:
            st.success("🟢 **Excellent**")
        elif current_sus >= 70:
            st.info("🟡 **Good**")
        else:
            st.warning("🟠 **Needs Work**")
else:
    st.info("No usability evaluation data available yet.")

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 7: DEVICE & BROWSER PERFORMANCE ===
st.markdown('<h3 class="section-title">Device & Browser Performance</h3>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    device_perf = df_dashboard.groupby('device_type').agg({
        'time_spent_seconds': 'mean',
        'interaction_count': 'mean',
        'error_encountered': lambda x: (x.sum() / len(x)) * 100
    }).reset_index()
    device_perf.columns = ['device_type', 'avg_time', 'avg_interactions', 'error_rate']
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=device_perf['device_type'], y=device_perf['avg_time'],
        name='Avg Time (s)', marker_color=PINK_COLORS['primary']
    ))
    fig.add_trace(go.Bar(
        x=device_perf['device_type'], y=device_perf['avg_interactions'],
        name='Avg Interactions', marker_color=PINK_COLORS['secondary']
    ))
    fig.update_layout(barmode='group', height=350)
    fig = style_chart(fig, "Performance by Device")
    st.plotly_chart(fig, use_container_width=True, key="device_perf")

with col2:
    browser_perf = df_dashboard.groupby('browser').agg({
        'time_spent_seconds': 'mean',
        'error_encountered': lambda x: (x.sum() / len(x)) * 100
    }).reset_index()
    browser_perf.columns = ['browser', 'avg_time', 'error_rate']
    
    fig = px.bar(browser_perf, x='browser', y='avg_time',
                labels={'avg_time': 'Avg Time (seconds)', 'browser': 'Browser'},
                color='avg_time',
                color_continuous_scale=['#FCE4EC', PINK_COLORS['primary']])
    fig = style_chart(fig, "Avg Session Time by Browser")
    st.plotly_chart(fig, use_container_width=True, key="browser_perf")

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 8: PERFORMANCE INSIGHTS ===
st.markdown('<h3 class="section-title">Performance Insights & Recommendations</h3>', unsafe_allow_html=True)

# (Keep your insights logic, just add pink styling to cards)

# === FOOTER ===
st.markdown("""
<div class="footer">
    <p>© 2025 UI/UX Performance Trend | Historical analysis from Data Warehouse | Raudatul Sholehah (2310817220002)</p>
</div>
""", unsafe_allow_html=True)
