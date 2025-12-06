"""
Page 4: Funnel Analysis
Shows: Conversion funnel, drop-off points, user journey optimization
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from dashboard.utils.data_loader import load_user_funnel
from dashboard.utils.user_tracking import identify_drop_off_points
from dashboard.components.metrics_card import metric_card, status_badge
from dashboard.components.charts import create_funnel_chart

st.set_page_config(page_title="Funnel Analysis", page_icon="🎯", layout="wide")

# Header
st.markdown("""
<h1 style='text-align: center; color: #667eea;'>
    🎯 Conversion Funnel Analysis
</h1>
<p style='text-align: center; color: #6b7280;'>
    User journey optimization and drop-off point identification
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# Load data
try:
    df_funnel = load_user_funnel()
    drop_off_analysis = identify_drop_off_points(df_funnel)
    
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Calculate overall metrics
total_users = len(df_funnel)

# Handle boolean completed_purchase
if df_funnel['completed_purchase'].dtype == 'bool':
    completed_purchases = df_funnel['completed_purchase'].sum()
else:
    completed_purchases = (df_funnel['completed_purchase'] == True).sum()

overall_conversion = (completed_purchases / total_users) * 100 if total_users > 0 else 0

# === SECTION 1: KEY FUNNEL METRICS ===
st.subheader("📊 Funnel Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    metric_card("Total Users", f"{total_users:,}", icon="👥")

with col2:
    metric_card("Completed Purchases", f"{completed_purchases:,}", icon="🛒")

with col3:
    metric_card("Conversion Rate", f"{overall_conversion:.2f}%", 
                delta="+2.1%", delta_color="normal", icon="📈")

with col4:
    avg_time = df_funnel[df_funnel['completed_purchase'] == True]['time_to_conversion_minutes'].mean()
    metric_card("Avg Time to Convert", f"{avg_time:.1f} min", icon="⏱️")

# Conversion status
st.markdown("---")
if overall_conversion >= 15:
    status_badge("excellent", "🟢 Excellent Conversion Rate")
    st.success("Funnel is performing exceptionally well!")
elif overall_conversion >= 10:
    status_badge("good", "🟡 Good Conversion Rate")
    st.info("Funnel is performing well, room for improvement.")
else:
    status_badge("warning", "🟠 Conversion Rate Needs Improvement")
    st.warning("Focus on reducing drop-offs at critical stages.")

st.markdown("---")

# === SECTION 2: CONVERSION FUNNEL VISUALIZATION ===
st.subheader("📉 Conversion Funnel")

col1, col2 = st.columns([2, 1])

with col1:
    # Create funnel data
    funnel_data = {}
    for step, data in drop_off_analysis.items():
        step_name = step.replace('_', ' ').title()
        funnel_data[step_name] = data['users']
    
    # Funnel chart
    fig = create_funnel_chart(funnel_data, title="User Conversion Funnel")
    st.plotly_chart(fig, use_column_width=True)

with col2:
    st.markdown("### Funnel Stages")
    
    for step, data in drop_off_analysis.items():
        step_name = step.replace('_', ' ').title()
        users = data['users']
        conversion = data['conversion_rate']
        drop_off = data['drop_off_rate']
        
        # Color based on conversion
        if conversion >= 70:
            bg_color = "#d1fae5"
            icon = "🟢"
        elif conversion >= 40:
            bg_color = "#fef3c7"
            icon = "🟡"
        else:
            bg_color = "#fee2e2"
            icon = "🔴"
        
        st.markdown(f"""
        <div style='background-color: {bg_color}; padding: 0.75rem; border-radius: 0.5rem; margin-bottom: 0.5rem;'>
            <strong>{icon} {step_name}</strong><br>
            Users: {users:,} | Rate: {conversion:.1f}%<br>
            Drop-off: {drop_off:.1f}%
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# === SECTION 3: DROP-OFF ANALYSIS ===
st.subheader("🚪 Drop-off Point Analysis")

# Prepare drop-off data
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
    # Bar chart for drop-offs
    fig = px.bar(
        df_dropoff,
        x='Stage',
        y='Drop-off Rate (%)',
        title="Drop-off Rate by Stage",
        color='Drop-off Rate (%)',
        color_continuous_scale='Reds',
        text='Drop-off Rate (%)'
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig, use_column_width=True)

with col2:
    st.markdown("### Critical Drop-off Points")
    
    # Sort by drop-off rate
    critical_drops = df_dropoff.nlargest(3, 'Drop-off Rate (%)')
    
    for idx, row in critical_drops.iterrows():
        stage = row['Stage']
        rate = row['Drop-off Rate (%)']
        users = row['Users Lost']
        
        st.markdown(f"""
        <div style='background-color: #fee2e2; padding: 0.75rem; border-left: 4px solid #ef4444; margin-bottom: 0.5rem;'>
            <strong>⚠️ {stage}</strong><br>
            Lost {users:,} users ({rate:.1f}%)
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# === SECTION 4: TIME TO CONVERSION ===
st.subheader("⏱️ Time to Conversion Analysis")

# Filter users who completed purchase
converted_users = df_funnel[df_funnel['completed_purchase'] == True].copy()

if len(converted_users) > 0:
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogram of conversion times
        fig = px.histogram(
            converted_users,
            x='time_to_conversion_minutes',
            nbins=20,
            title="Distribution of Time to Conversion",
            labels={'time_to_conversion_minutes': 'Time (minutes)', 'count': 'Number of Users'},
            color_discrete_sequence=['#667eea']
        )
        
        # Add median line
        median_time = converted_users['time_to_conversion_minutes'].median()
        fig.add_vline(x=median_time, line_dash="dash", line_color="red",
                     annotation_text=f"Median: {median_time:.1f} min")
        
        st.plotly_chart(fig, use_column_width=True)
    
    with col2:
        # Box plot by device
        fig = px.box(
            converted_users,
            x='device_type',
            y='time_to_conversion_minutes',
            title="Time to Conversion by Device",
            labels={'time_to_conversion_minutes': 'Time (minutes)', 'device_type': 'Device'},
            color='device_type'
        )
        st.plotly_chart(fig, use_column_width=True)
    
    # Statistics
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

st.markdown("---")

# === SECTION 4.5: EXIT STAGE ANALYSIS ===
st.subheader("🚪 Exit Stage Analysis")

# Analyze where users exit without converting
non_converted = df_funnel[df_funnel['completed_purchase'] == False]

if len(non_converted) > 0:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Exit stage distribution
        exit_stage_dist = non_converted['drop_off_point'].value_counts()
        
        fig = px.pie(
            values=exit_stage_dist.values,
            names=exit_stage_dist.index,
            title="User Exit Points",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Reds_r
        )
        st.plotly_chart(fig, use_column_width=True)
        
        # Exit stage by traffic source
        st.markdown("#### Exit Stage by Traffic Source")
        
        exit_traffic = pd.crosstab(
            non_converted['drop_off_point'], 
            non_converted['traffic_source'],
            normalize='columns'
        ) * 100
        
        fig = px.bar(
            exit_traffic,
            barmode='group',
            title="Exit Rate by Traffic Source (%)",
            labels={'value': 'Percentage (%)', 'drop_off_point': 'Exit Stage'}
        )
        st.plotly_chart(fig, use_column_width=True)
    
    with col2:
        st.markdown("### Exit Statistics")
        
        for stage, count in exit_stage_dist.items():
            percentage = (count / len(non_converted)) * 100
            
            if percentage > 30:
                icon = "🔴"
                color = "#fee2e2"
            elif percentage > 20:
                icon = "🟡"
                color = "#fef3c7"
            else:
                icon = "🟢"
                color = "#dbeafe"
            
            st.markdown(f"""
            <div style='background-color: {color}; padding: 0.75rem; border-radius: 0.5rem; margin-bottom: 0.5rem;'>
                {icon} <strong>{stage}</strong><br>
                {count:,} users ({percentage:.1f}%)
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### Traffic Source Performance")
        
        # Conversion rate by traffic source
        traffic_conversion = df_funnel.groupby('traffic_source').agg({
            'completed_purchase': 'sum',
            'user_id': 'count'
        })
        traffic_conversion['conversion_rate'] = (
            traffic_conversion['completed_purchase'] / traffic_conversion['user_id'] * 100
        ).round(2)
        
        for source in traffic_conversion.index:
            rate = traffic_conversion.loc[source, 'conversion_rate']
            st.markdown(f"**{source}**: {rate:.1f}%")

else:
    st.success("🎉 All users are converting! Excellent funnel performance.")

st.markdown("---")

# === SECTION 4.6: PRODUCT CATEGORY ANALYSIS ===
st.subheader("📦 Product Category Performance")

col1, col2 = st.columns(2)

with col1:
    # Conversion rate by product category
    category_conversion = df_funnel.groupby('product_category').agg({
        'completed_purchase': 'sum',
        'user_id': 'count'
    })
    category_conversion['conversion_rate'] = (
        category_conversion['completed_purchase'] / category_conversion['user_id'] * 100
    ).round(2)
    category_conversion = category_conversion.sort_values('conversion_rate', ascending=False)
    
    fig = px.bar(
        x=category_conversion.index,
        y=category_conversion['conversion_rate'],
        title="Conversion Rate by Product Category",
        labels={'x': 'Product Category', 'y': 'Conversion Rate (%)'},
        color=category_conversion['conversion_rate'],
        color_continuous_scale='Blues',
        text=category_conversion['conversion_rate']
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig, use_column_width=True)

with col2:
    # Time to conversion by category
    converted_with_category = df_funnel[df_funnel['completed_purchase'] == True]
    
    if len(converted_with_category) > 0:
        category_time = converted_with_category.groupby('product_category')['time_to_conversion_minutes'].mean().sort_values()
        
        fig = px.bar(
            x=category_time.values,
            y=category_time.index,
            orientation='h',
            title="Avg Time to Convert by Category",
            labels={'x': 'Avg Time (minutes)', 'y': 'Product Category'},
            color=category_time.values,
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig, use_column_width=True)

# Category statistics table
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

st.dataframe(
    category_stats.style.background_gradient(subset=['Conversion Rate (%)'], cmap='RdYlGn'),
    use_container_width=True
)

st.markdown("---")

# === SECTION 5: DEVICE-SPECIFIC FUNNEL ===
st.subheader("📱 Funnel Performance by Device")

# Calculate conversion rate by device
device_conversion = df_funnel.groupby('device_type').agg({
    'completed_purchase': ['sum', 'count']
}).reset_index()
device_conversion.columns = ['device_type', 'conversions', 'total']
device_conversion['conversion_rate'] = (device_conversion['conversions'] / device_conversion['total']) * 100

col1, col2 = st.columns([2, 1])

with col1:
    # Bar chart
    fig = px.bar(
        device_conversion,
        x='device_type',
        y='conversion_rate',
        title="Conversion Rate by Device Type",
        labels={'conversion_rate': 'Conversion Rate (%)', 'device_type': 'Device'},
        color='conversion_rate',
        color_continuous_scale='Blues',
        text='conversion_rate'
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig, use_column_width=True)

with col2:
    st.markdown("### Device Performance")
    
    for idx, row in device_conversion.iterrows():
        device = row['device_type']
        rate = row['conversion_rate']
        conversions = row['conversions']
        
        if rate >= overall_conversion:
            icon = "🟢"
            status = "Above Average"
        else:
            icon = "🔴"
            status = "Below Average"
        
        st.markdown(f"""
        <div style='background-color: #f9fafb; padding: 0.75rem; border-radius: 0.5rem; margin-bottom: 0.5rem;'>
            {icon} <strong>{device}</strong><br>
            Rate: {rate:.1f}% ({status})<br>
            Conversions: {conversions:,}
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# === SECTION 6: FUNNEL OPTIMIZATION RECOMMENDATIONS ===
st.subheader("💡 Funnel Optimization Recommendations")

recommendations = []

# Identify highest drop-off stage
if len(df_dropoff) > 0:
    highest_dropoff = df_dropoff.loc[df_dropoff['Drop-off Rate (%)'].idxmax()]
    recommendations.append({
        'priority': 'High',
        'stage': highest_dropoff['Stage'],
        'issue': f"Highest drop-off rate: {highest_dropoff['Drop-off Rate (%)']:.1f}%",
        'recommendation': f"Investigate and optimize user experience at {highest_dropoff['Stage']}",
        'expected_impact': f"Potential to recover {highest_dropoff['Users Lost']:,} users"
    })

# Check conversion rate
if overall_conversion < 10:
    recommendations.append({
        'priority': 'High',
        'stage': 'Overall Funnel',
        'issue': f"Low overall conversion rate: {overall_conversion:.1f}%",
        'recommendation': "Conduct user testing to identify friction points throughout the funnel",
        'expected_impact': "Improve overall conversion by 2-3%"
    })

# Check device disparity
if len(device_conversion) > 1:
    device_gap = device_conversion['conversion_rate'].max() - device_conversion['conversion_rate'].min()
    if device_gap > 5:
        worst_device = device_conversion.loc[device_conversion['conversion_rate'].idxmin(), 'device_type']
        recommendations.append({
            'priority': 'Medium',
            'stage': 'Device Optimization',
            'issue': f"Large conversion gap ({device_gap:.1f}%) between devices",
            'recommendation': f"Optimize user experience for {worst_device} users",
            'expected_impact': "Reduce device conversion gap by 50%"
        })

# Display recommendations
if recommendations:
    for idx, rec in enumerate(recommendations, 1):
        priority_colors = {
            'High': '#fee2e2',
            'Medium': '#fef3c7',
            'Low': '#dbeafe'
        }
        
        color = priority_colors.get(rec['priority'], '#f0f2f6')
        
        st.markdown(f"""
        <div style='background-color: {color}; padding: 1rem; border-left: 4px solid #667eea; margin-bottom: 1rem;'>
            <h4>#{idx} - {rec['stage']} (Priority: {rec['priority']})</h4>
            <p><strong>Issue:</strong> {rec['issue']}</p>
            <p><strong>Recommendation:</strong> {rec['recommendation']}</p>
            <p><strong>Expected Impact:</strong> {rec['expected_impact']}</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.success("✅ Funnel is performing optimally. Continue monitoring for changes.")

st.markdown("---")

# === SECTION 7: FUNNEL OPTIMIZATION BEST PRACTICES ===
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
    
    #### 4. **A/B Testing Strategy**
    - Test one element at a time
    - Sufficient sample size (95% confidence)
    - Test duration: minimum 2 weeks
    - Focus on high-impact stages
    
    #### 5. **Monitoring Metrics**
    - Conversion rate per stage
    - Average time to convert
    - Drop-off points
    - Device-specific performance
    - Traffic source analysis
    
    #### 6. **Recovery Tactics**
    - Email reminders for abandoned carts
    - Retargeting campaigns
    - Limited-time offers
    - Exit-intent popups (use sparingly)
    """)

# === FOOTER ===
st.markdown("---")
st.caption("🎯 Funnel Analysis | Conversion optimization insights | Raudatul Sholehah (2310817220002)")
