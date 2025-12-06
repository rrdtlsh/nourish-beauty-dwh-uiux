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

st.set_page_config(page_title="UI/UX Performance", page_icon="📈", layout="wide")

# Header
st.markdown("""
<h1 style='text-align: center; color: #667eea;'>
    📈 UI/UX Performance Trend Analysis
</h1>
<p style='text-align: center; color: #6b7280;'>
    Historical performance tracking and dashboard usage analytics
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# Load data
try:
    df_dashboard = load_dashboard_usage()
    df_usability = load_usability_scores()
    
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# === SECTION 1: DASHBOARD USAGE OVERVIEW ===
st.subheader("📊 Dashboard Usage Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_users = df_dashboard['user_id'].nunique()
    metric_card("Total Users", f"{total_users:,}", icon="👥")

with col2:
    total_sessions = df_dashboard['session_id'].nunique()
    metric_card("Total Sessions", f"{total_sessions:,}", icon="🔄")

with col3:
    avg_time = df_dashboard['time_spent_seconds'].mean()
    metric_card("Avg Session Time", f"{avg_time:.0f}s", icon="⏱️")

with col4:
    total_interactions = df_dashboard['interaction_count'].sum()
    metric_card("Total Interactions", f"{total_interactions:,}", icon="🖱️")

st.markdown("---")

# === SECTION 2: USAGE TREND OVER TIME ===
st.subheader("📈 Dashboard Usage Trend")

# Prepare time series data
df_dashboard['usage_date'] = pd.to_datetime(df_dashboard['usage_date'])
daily_usage = df_dashboard.groupby('usage_date').agg({
    'user_id': 'nunique',
    'visit_count': 'sum',
    'time_spent_seconds': 'mean',
    'interaction_count': 'mean'
}).reset_index()

col1, col2 = st.columns([3, 1])

with col1:
    # Multi-line chart
    fig = go.Figure()
    
    # Add traces
    fig.add_trace(go.Scatter(
        x=daily_usage['usage_date'],
        y=daily_usage['user_id'],
        mode='lines+markers',
        name='Daily Users',
        line=dict(color='#667eea', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_usage['usage_date'],
        y=daily_usage['visit_count'],
        mode='lines+markers',
        name='Total Visits',
        yaxis='y2',
        line=dict(color='#764ba2', width=2)
    ))
    
    fig.update_layout(
        title="Daily Usage Metrics",
        xaxis_title="Date",
        yaxis_title="Users",
        yaxis2=dict(
            title="Visits",
            overlaying='y',
            side='right'
        ),
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_column_width=True)

with col2:
    st.markdown("### Trend Summary")
    
    # Calculate trend
    if len(daily_usage) >= 7:
        recent_avg = daily_usage['user_id'].tail(7).mean()
        previous_avg = daily_usage['user_id'].head(7).mean()
        trend_pct = ((recent_avg - previous_avg) / previous_avg) * 100 if previous_avg > 0 else 0
        
        st.metric("Recent Avg Users", f"{recent_avg:.0f}")
        st.metric("Previous Avg", f"{previous_avg:.0f}")
        st.metric("Trend", f"{trend_pct:+.1f}%")
    
    st.markdown("---")
    
    if trend_pct > 5:
        status_badge("excellent", "🟢 Growing")
    elif trend_pct > 0:
        status_badge("good", "🟡 Stable")
    else:
        status_badge("warning", "🔴 Declining")

st.markdown("---")

# === SECTION 3: PAGE POPULARITY ===
st.subheader("📄 Dashboard Page Popularity")

# Calculate page metrics
page_metrics = df_dashboard.groupby('dashboard_page').agg({
    'visit_count': 'sum',
    'time_spent_seconds': 'mean',
    'interaction_count': 'mean',
    'user_id': 'nunique'
}).reset_index()
page_metrics = page_metrics.sort_values('visit_count', ascending=False)

col1, col2 = st.columns([2, 1])

with col1:
    # Bar chart
    fig = px.bar(
        page_metrics,
        x='dashboard_page',
        y='visit_count',
        title="Total Visits by Page",
        labels={'visit_count': 'Total Visits', 'dashboard_page': 'Page'},
        color='visit_count',
        color_continuous_scale='Blues',
        text='visit_count'
    )
    fig.update_traces(texttemplate='%{text:,}', textposition='outside')
    st.plotly_chart(fig, use_column_width=True)

with col2:
    st.markdown("### Top Pages")
    
    for idx, row in page_metrics.head(5).iterrows():
        page = row['dashboard_page']
        visits = row['visit_count']
        users = row['user_id']
        
        st.markdown(f"""
        <div style='background-color: #f9fafb; padding: 0.75rem; border-radius: 0.5rem; margin-bottom: 0.5rem;'>
            <strong>{page}</strong><br>
            Visits: {visits:,} | Users: {users:,}
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# === SECTION 4: ENGAGEMENT METRICS ===
st.subheader("🎯 User Engagement Metrics")

col1, col2 = st.columns(2)

with col1:
    # Average time spent by page
    fig = px.bar(
        page_metrics,
        x='dashboard_page',
        y='time_spent_seconds',
        title="Avg Time Spent per Page",
        labels={'time_spent_seconds': 'Avg Time (seconds)', 'dashboard_page': 'Page'},
        color='time_spent_seconds',
        color_continuous_scale='Greens'
    )
    st.plotly_chart(fig, use_column_width=True)

with col2:
    # Average interactions by page
    fig = px.bar(
        page_metrics,
        x='dashboard_page',
        y='interaction_count',
        title="Avg Interactions per Page",
        labels={'interaction_count': 'Avg Interactions', 'dashboard_page': 'Page'},
        color='interaction_count',
        color_continuous_scale='Purples'
    )
    st.plotly_chart(fig, use_column_width=True)

st.markdown("---")

# === SECTION 5: FEATURE USAGE ===
st.subheader("🔧 Feature Usage Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    # Filter usage
    filter_usage = (df_dashboard['filter_used'].sum() / len(df_dashboard)) * 100
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=filter_usage,
        title={'text': "Filter Usage (%)"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#667eea"},
            'steps': [
                {'range': [0, 30], 'color': "#fee2e2"},
                {'range': [30, 60], 'color': "#fef3c7"},
                {'range': [60, 100], 'color': "#d1fae5"}
            ]
        }
    ))
    fig.update_layout(height=250)
    st.plotly_chart(fig, use_column_width=True)

with col2:
    # Export usage
    export_rate = (df_dashboard[df_dashboard['export_count'] > 0].shape[0] / len(df_dashboard)) * 100
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=export_rate,
        title={'text': "Export Usage (%)"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#764ba2"},
            'steps': [
                {'range': [0, 20], 'color': "#fee2e2"},
                {'range': [20, 50], 'color': "#fef3c7"},
                {'range': [50, 100], 'color': "#d1fae5"}
            ]
        }
    ))
    fig.update_layout(height=250)
    st.plotly_chart(fig, use_column_width=True)

with col3:
    # Error rate
    error_rate = (df_dashboard['error_encountered'].sum() / len(df_dashboard)) * 100
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=error_rate,
        title={'text': "Error Rate (%)"},
        gauge={
            'axis': {'range': [None, 10]},
            'bar': {'color': "#ef4444"},
            'steps': [
                {'range': [0, 3], 'color': "#d1fae5"},
                {'range': [3, 5], 'color': "#fef3c7"},
                {'range': [5, 10], 'color': "#fee2e2"}
            ]
        }
    ))
    fig.update_layout(height=250)
    st.plotly_chart(fig, use_column_width=True)

st.markdown("---")

# === SECTION 6: USABILITY SCORE TREND ===
st.subheader("⭐ Usability Score Historical Trend")

if not df_usability.empty:
    # Prepare time series
    df_usability['evaluation_date'] = pd.to_datetime(df_usability['evaluation_date'])
    usability_trend = df_usability.groupby('evaluation_date').agg({
        'overall_score': 'mean',
        'sus_score': 'mean',
        'satisfaction_rating': 'mean'
    }).reset_index()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Multi-line chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=usability_trend['evaluation_date'],
            y=usability_trend['overall_score'],
            mode='lines+markers',
            name='Overall Score',
            line=dict(color='#667eea', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=usability_trend['evaluation_date'],
            y=usability_trend['sus_score'] / 20,  # Scale to 0-5
            mode='lines+markers',
            name='SUS Score (scaled)',
            line=dict(color='#10b981', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=usability_trend['evaluation_date'],
            y=usability_trend['satisfaction_rating'],
            mode='lines+markers',
            name='Satisfaction',
            line=dict(color='#f59e0b', width=2)
        ))
        
        fig.update_layout(
            title="Usability Metrics Over Time",
            xaxis_title="Date",
            yaxis_title="Score (0-5)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_column_width=True)
    
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
            status_badge("excellent", "🟢 Excellent")
        elif current_sus >= 70:
            status_badge("good", "🟡 Good")
        else:
            status_badge("warning", "🟠 Needs Work")

else:
    st.info("No usability evaluation data available yet.")

st.markdown("---")

# === SECTION 7: DEVICE & BROWSER PERFORMANCE ===
st.subheader("📱 Device & Browser Performance")

col1, col2 = st.columns(2)

with col1:
    # Device performance
    device_perf = df_dashboard.groupby('device_type').agg({
        'time_spent_seconds': 'mean',
        'interaction_count': 'mean',
        'error_encountered': lambda x: (x.sum() / len(x)) * 100
    }).reset_index()
    device_perf.columns = ['device_type', 'avg_time', 'avg_interactions', 'error_rate']
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=device_perf['device_type'],
        y=device_perf['avg_time'],
        name='Avg Time (s)',
        marker_color='#667eea'
    ))
    fig.add_trace(go.Bar(
        x=device_perf['device_type'],
        y=device_perf['avg_interactions'],
        name='Avg Interactions',
        marker_color='#764ba2'
    ))
    fig.update_layout(
        title="Performance by Device",
        barmode='group',
        height=350
    )
    st.plotly_chart(fig, use_column_width=True)

with col2:
    # Browser performance
    browser_perf = df_dashboard.groupby('browser').agg({
        'time_spent_seconds': 'mean',
        'error_encountered': lambda x: (x.sum() / len(x)) * 100
    }).reset_index()
    browser_perf.columns = ['browser', 'avg_time', 'error_rate']
    
    fig = px.bar(
        browser_perf,
        x='browser',
        y='avg_time',
        title="Avg Session Time by Browser",
        labels={'avg_time': 'Avg Time (seconds)', 'browser': 'Browser'},
        color='avg_time',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig, use_column_width=True)

st.markdown("---")

# === SECTION 8: PERFORMANCE INSIGHTS ===
st.subheader("💡 Performance Insights & Recommendations")

insights = []

# Check for declining trend
if len(daily_usage) >= 14:
    recent_week = daily_usage['user_id'].tail(7).mean()
    previous_week = daily_usage['user_id'].iloc[-14:-7].mean()
    
    if recent_week < previous_week * 0.9:
        insights.append({
            'type': 'warning',
            'title': 'Declining User Activity',
            'message': f'User activity decreased by {((previous_week - recent_week) / previous_week * 100):.1f}% in the last week.',
            'action': 'Investigate recent changes or run user satisfaction survey.'
        })

# Check for high-performing pages
top_page = page_metrics.iloc[0]
if top_page['visit_count'] > page_metrics['visit_count'].mean() * 2:
    insights.append({
        'type': 'success',
        'title': 'High-Performing Page Identified',
        'message': f'{top_page["dashboard_page"]} receives {top_page["visit_count"]:,} visits - 2x more than average.',
        'action': 'Analyze success factors and apply to other pages.'
    })

# Check feature adoption
if filter_usage < 50:
    insights.append({
        'type': 'info',
        'title': 'Low Filter Usage',
        'message': f'Only {filter_usage:.1f}% of users utilize filters.',
        'action': 'Consider adding filter tutorials or improving visibility.'
    })

# Display insights
if insights:
    for insight in insights:
        type_config = {
            'warning': {'icon': '⚠️', 'color': '#fef3c7'},
            'success': {'icon': '✅', 'color': '#d1fae5'},
            'info': {'icon': 'ℹ️', 'color': '#dbeafe'}
        }
        
        config = type_config.get(insight['type'], {'icon': 'ℹ️', 'color': '#f0f2f6'})
        
        st.markdown(f"""
        <div style='background-color: {config["color"]}; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
            <h4>{config["icon"]} {insight["title"]}</h4>
            <p><strong>Insight:</strong> {insight["message"]}</p>
            <p><strong>Recommended Action:</strong> {insight["action"]}</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.success("✅ All performance metrics are healthy. Continue monitoring.")

st.markdown("---")

# === FOOTER ===
st.caption("📈 UI/UX Performance Trend | Historical analysis from Data Warehouse | Raudatul Sholehah (2310817220002)")
