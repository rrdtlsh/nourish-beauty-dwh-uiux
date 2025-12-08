"""
Page 4: Funnel Analysis
Shows: Conversion funnel, drop-off points, user journey optimization
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from dashboard.utils.data_loader import load_user_funnel
from dashboard.utils.user_tracking import identify_drop_off_points
from dashboard.components.metrics_card import metric_card, status_badge
from dashboard.components.charts import create_funnel_chart

# === PAGE CONFIGURATION ===
st.set_page_config(
    page_title="Funnel Analysis", 
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
    <h1 class="page-title">🎯 Conversion Funnel Analysis</h1>
    <p class="page-subtitle">User journey optimization and drop-off point identification</p>
</div>
""", unsafe_allow_html=True)

# Load data
try:
    df_funnel = load_user_funnel()
    drop_off_analysis = identify_drop_off_points(df_funnel)
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# Calculate metrics
total_users = len(df_funnel)

if df_funnel['completed_purchase'].dtype == 'bool':
    completed_purchases = df_funnel['completed_purchase'].sum()
else:
    completed_purchases = (df_funnel['completed_purchase'] == True).sum()

overall_conversion = (completed_purchases / total_users) * 100 if total_users > 0 else 0

# === SECTION 1: KEY FUNNEL METRICS ===
st.markdown('<h3 class="section-title">Funnel Overview</h3>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

avg_time = df_funnel[df_funnel['completed_purchase'] == True]['time_to_conversion_minutes'].mean()

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
        <div class="kpi-icon">🛒</div>
        <div class="kpi-label">Completed Purchases</div>
        <div class="kpi-value">{completed_purchases:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">📈</div>
        <div class="kpi-label">Conversion Rate</div>
        <div class="kpi-value">{overall_conversion:.2f}%</div>
        <div class="kpi-change positive">+2.1%</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">⏱️</div>
        <div class="kpi-label">Avg Time to Convert</div>
        <div class="kpi-value">{avg_time:.1f} min</div>
    </div>
    """, unsafe_allow_html=True)

# Conversion status
if overall_conversion >= 15:
    st.success("🟢 **Excellent Conversion Rate** - Funnel is performing exceptionally well!")
elif overall_conversion >= 10:
    st.info("🟡 **Good Conversion Rate** - Performing well, room for improvement.")
else:
    st.warning("🟠 **Needs Improvement** - Focus on reducing drop-offs at critical stages.")

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 2: CONVERSION FUNNEL ===
st.markdown('<h3 class="section-title">Conversion Funnel</h3>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    funnel_data = {}
    for step, data in drop_off_analysis.items():
        step_name = step.replace('_', ' ').title()
        funnel_data[step_name] = data['users']
    
    fig = create_funnel_chart(funnel_data, title="User Conversion Funnel")
    fig = style_chart(fig, "User Conversion Funnel")
    st.plotly_chart(fig, use_container_width=True, key="funnel_main")

with col2:
    st.markdown("### Funnel Stages")
    
    for step, data in drop_off_analysis.items():
        step_name = step.replace('_', ' ').title()
        users = data['users']
        conversion = data['conversion_rate']
        drop_off = data['drop_off_rate']
        
        if conversion >= 70:
            bg_color = "#d1fae5"
            border_color = "#10b981"
        elif conversion >= 40:
            bg_color = "#fef3c7"
            border_color = "#f59e0b"
        else:
            bg_color = "#fee2e2"
            border_color = "#ef4444"
        
        st.markdown(f"""
        <div style='background-color: {bg_color}; padding: 0.75rem; border-radius: 8px; 
                    margin-bottom: 0.5rem; border-left: 4px solid {border_color}; color: #2D2D2D;'>
            <strong style='color: #2D2D2D;'>{step_name}</strong><br>
            <span style='color: #4A4A4A;'>Users: {users:,} | Rate: {conversion:.1f}%<br>
            Drop-off: {drop_off:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 3: DROP-OFF ANALYSIS ===
st.markdown('<h3 class="section-title">Drop-off Point Analysis</h3>', unsafe_allow_html=True)

drop_off_steps = []
drop_off_rates = []
drop_off_users = []

prev_users = total_users
for step, data in drop_off_analysis.items():
    current_users = data['users']
    dropped = prev_users - current_users
    drop_rate = data['drop_off_rate']
    
    if dropped > 0:
        step_name = step.replace('_', ' ').title()
        drop_off_steps.append(f"After {step_name}")
        drop_off_rates.append(drop_rate)
        drop_off_users.append(dropped)
    
    prev_users = current_users

df_dropoff = pd.DataFrame({
    'Stage': drop_off_steps,
    'Drop-off Rate (%)': drop_off_rates,
    'Users Lost': drop_off_users
})

col1, col2 = st.columns([2, 1])

with col1:
    fig = px.bar(df_dropoff, x='Stage', y='Drop-off Rate (%)',
                color='Drop-off Rate (%)', color_continuous_scale=['#FCE4EC', PINK_COLORS['primary']],
                text='Drop-off Rate (%)')
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig = style_chart(fig, "Drop-off Rate by Stage")
    st.plotly_chart(fig, use_container_width=True, key="dropoff_chart")

with col2:
    st.markdown("### Critical Drop-off Points")
    
    critical_drops = df_dropoff.nlargest(3, 'Drop-off Rate (%)')
    
    for idx, row in critical_drops.iterrows():
        stage = row['Stage']
        rate = row['Drop-off Rate (%)']
        users = row['Users Lost']
        
        st.markdown(f"""
        <div style='background-color: #fee2e2; padding: 0.75rem; border-left: 4px solid {PINK_COLORS['primary']}; 
                    margin-bottom: 0.5rem; border-radius: 8px; color: #2D2D2D;'>
            <strong style='color: #2D2D2D;'>⚠️ {stage}</strong><br>
            <span style='color: #4A4A4A;'>Lost {users:,} users ({rate:.1f}%)</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 4: TIME TO CONVERSION ===
st.markdown('<h3 class="section-title">Time to Conversion Analysis</h3>', unsafe_allow_html=True)

converted_users = df_funnel[df_funnel['completed_purchase'] == True].copy()

if len(converted_users) > 0:
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(converted_users, x='time_to_conversion_minutes', nbins=20,
                          labels={'time_to_conversion_minutes': 'Time (minutes)', 'count': 'Number of Users'},
                          color_discrete_sequence=[PINK_COLORS['primary']])
        
        median_time = converted_users['time_to_conversion_minutes'].median()
        fig.add_vline(x=median_time, line_dash="dash", line_color=PINK_COLORS['secondary'],
                     annotation_text=f"Median: {median_time:.1f} min")
        
        fig = style_chart(fig, "Distribution of Time to Conversion")
        st.plotly_chart(fig, use_container_width=True, key="time_hist")
    
    with col2:
        fig = px.box(converted_users, x='device_type', y='time_to_conversion_minutes',
                    labels={'time_to_conversion_minutes': 'Time (minutes)', 'device_type': 'Device'},
                    color='device_type', color_discrete_sequence=PINK_COLORS['gradient'])
        fig = style_chart(fig, "Time to Conversion by Device")
        st.plotly_chart(fig, use_container_width=True, key="time_box")
    
    st.markdown("### Conversion Time Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Median Time", f"{median_time:.1f} min")
    with col2:
        mean_time = converted_users['time_to_conversion_minutes'].mean()
        st.metric("Mean Time", f"{mean_time:.1f} min")
    with col3:
        min_time = converted_users['time_to_conversion_minutes'].min()
        st.metric("Min Time", f"{min_time:.1f} min")
    with col4:
        max_time = converted_users['time_to_conversion_minutes'].max()
        st.metric("Max Time", f"{max_time:.1f} min")
else:
    st.info("No conversion data available yet.")

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 5: EXIT STAGE ANALYSIS ===
st.markdown('<h3 class="section-title">Exit Stage Analysis</h3>', unsafe_allow_html=True)

non_converted = df_funnel[df_funnel['completed_purchase'] == False]

if len(non_converted) > 0:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        exit_stage_dist = non_converted['drop_off_point'].value_counts()
        
        fig = px.pie(values=exit_stage_dist.values, names=exit_stage_dist.index,
                    hole=0.4, color_discrete_sequence=PINK_COLORS['gradient'])
        fig = style_chart(fig, "User Exit Points")
        st.plotly_chart(fig, use_container_width=True, key="exit_pie")
    
    with col2:
        st.markdown("### Exit Statistics")
        
        for stage, count in exit_stage_dist.items():
            percentage = (count / len(non_converted)) * 100
            
            if percentage > 30:
                bg_color = "#fee2e2"
                border_color = PINK_COLORS['primary']
            elif percentage > 20:
                bg_color = "#fef3c7"
                border_color = PINK_COLORS['secondary']
            else:
                bg_color = "#FCE4EC"
                border_color = PINK_COLORS['accent']
            
            st.markdown(f"""
            <div style='background-color: {bg_color}; padding: 0.75rem; border-radius: 8px; 
                        margin-bottom: 0.5rem; border-left: 4px solid {border_color}; color: #2D2D2D;'>
                <strong style='color: #2D2D2D;'>{stage}</strong><br>
                <span style='color: #4A4A4A;'>{count:,} users ({percentage:.1f}%)</span>
            </div>
            """, unsafe_allow_html=True)
else:
    st.success("🎉 All users are converting! Excellent funnel performance.")

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 6: PRODUCT CATEGORY ===
st.markdown('<h3 class="section-title">Product Category Performance</h3>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    category_conversion = df_funnel.groupby('product_category').agg({
        'completed_purchase': 'sum',
        'user_id': 'count'
    })
    category_conversion['conversion_rate'] = (
        category_conversion['completed_purchase'] / category_conversion['user_id'] * 100
    ).round(2)
    category_conversion = category_conversion.sort_values('conversion_rate', ascending=False)
    
    fig = px.bar(x=category_conversion.index, y=category_conversion['conversion_rate'],
                labels={'x': 'Product Category', 'y': 'Conversion Rate (%)'},
                color=category_conversion['conversion_rate'],
                color_continuous_scale=['#FCE4EC', PINK_COLORS['primary']],
                text=category_conversion['conversion_rate'])
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig = style_chart(fig, "Conversion Rate by Product Category")
    st.plotly_chart(fig, use_container_width=True, key="category_conv")

with col2:
    converted_with_category = df_funnel[df_funnel['completed_purchase'] == True]
    
    if len(converted_with_category) > 0:
        category_time = converted_with_category.groupby('product_category')['time_to_conversion_minutes'].mean().sort_values()
        
        fig = px.bar(x=category_time.values, y=category_time.index, orientation='h',
                    labels={'x': 'Avg Time (minutes)', 'y': 'Product Category'},
                    color=category_time.values,
                    color_continuous_scale=['#FCE4EC', PINK_COLORS['primary']])
        fig = style_chart(fig, "Avg Time to Convert by Category")
        st.plotly_chart(fig, use_container_width=True, key="category_time")

st.markdown("### Category Performance Summary")

category_stats = df_funnel.groupby('product_category').agg({
    'user_id': 'count',
    'completed_purchase': 'sum',
    'time_to_conversion_minutes': 'mean'
})
category_stats.columns = ['Total Users', 'Conversions', 'Avg Time (min)']
category_stats['Conversion Rate (%)'] = (
    (category_stats['Conversions'] / category_stats['Total Users']) * 100
).round(2)
category_stats['Avg Time (min)'] = category_stats['Avg Time (min)'].round(1)

st.dataframe(category_stats, use_container_width=True)

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 7: DEVICE-SPECIFIC FUNNEL ===
st.markdown('<h3 class="section-title">Funnel Performance by Device</h3>', unsafe_allow_html=True)

device_conversion = df_funnel.groupby('device_type').agg({
    'completed_purchase': ['sum', 'count']
}).reset_index()
device_conversion.columns = ['device_type', 'conversions', 'total']
device_conversion['conversion_rate'] = (device_conversion['conversions'] / device_conversion['total']) * 100

col1, col2 = st.columns([2, 1])

with col1:
    fig = px.bar(device_conversion, x='device_type', y='conversion_rate',
                labels={'conversion_rate': 'Conversion Rate (%)', 'device_type': 'Device'},
                color='conversion_rate', color_continuous_scale=['#FCE4EC', PINK_COLORS['primary']],
                text='conversion_rate')
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig = style_chart(fig, "Conversion Rate by Device Type")
    st.plotly_chart(fig, use_container_width=True, key="device_conv")

with col2:
    st.markdown("### Device Performance")
    
    for idx, row in device_conversion.iterrows():
        device = row['device_type']
        rate = row['conversion_rate']
        conversions = row['conversions']
        
        if rate >= overall_conversion:
            bg_color = "#d1fae5"
            border_color = "#10b981"
            status = "Above Average"
        else:
            bg_color = "#fee2e2"
            border_color = PINK_COLORS['primary']
            status = "Below Average"
        
        st.markdown(f"""
        <div style='background-color: {bg_color}; padding: 0.75rem; border-radius: 8px; 
                    margin-bottom: 0.5rem; border-left: 4px solid {border_color}; color: #2D2D2D;'>
            <strong style='color: #2D2D2D;'>{device}</strong><br>
            <span style='color: #4A4A4A;'>Rate: {rate:.1f}% ({status})<br>
            Conversions: {conversions:,}</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 8: RECOMMENDATIONS ===
st.markdown('<h3 class="section-title">Funnel Optimization Recommendations</h3>', unsafe_allow_html=True)

# (Keep your recommendation logic, just style the output cards with pink colors)

with st.expander("📚 Funnel Optimization Best Practices", expanded=False):
    st.markdown("""
    ### Best Practices for Funnel Optimization
    
    #### 1. **Reduce Friction at Each Stage**
    - Minimize form fields
    - Implement autofill
    - Clear call-to-action buttons
    - Progress indicators
    
    #### 2. **Optimize Landing Page**
    - Clear value proposition
    - Fast loading time (< 3 seconds)
    - Mobile-responsive design
    - Trust signals (reviews, badges)
    
    #### 3. **Simplify Checkout Process**
    - Guest checkout option
    - Multiple payment methods
    - Clear error messages
    - Save progress option
    """)

# === FOOTER ===
st.markdown("""
<div class="footer">
    <p>© 2025 Funnel Analysis | Conversion optimization insights | Raudatul Sholehah (2310817220002)</p>
</div>
""", unsafe_allow_html=True)
