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

st.set_page_config(page_title="Error Rate Analysis", page_icon="⚠️", layout="wide")

# Header
st.markdown("""
<h1 style='text-align: center; color: #667eea;'>
    ⚠️ Error Rate & Failure Interaction Analysis
</h1>
<p style='text-align: center; color: #6b7280;'>
    Comprehensive tracking of errors, failures, and interaction issues
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# Load data - FIXED
try:
    df_behavior = load_user_behavior_data()
    df_errors = load_error_metrics()
    overall_error_rate = calculate_error_rate(df_behavior)
    
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Calculate metrics - FIXED
total_errors = df_behavior['error_occurred'].sum()  # Already converted to boolean in load function
total_interactions = len(df_behavior)
affected_users = df_behavior[df_behavior['error_occurred'] == True]['user_id'].nunique()
total_users = df_behavior['user_id'].nunique()

# TAMBAHKAN INI: Pre-calculate error distributions for use throughout the page
error_records = df_behavior[df_behavior['error_occurred'] == True]

if len(error_records) > 0:
    error_by_page = error_records['page'].value_counts()
    error_by_action = error_records['action_type'].value_counts()
    # For backward compatibility with variable name 'error_types'
    error_types = error_by_page  # atau error_by_action, sesuai kebutuhan
else:
    error_by_page = pd.Series(dtype=int)
    error_by_action = pd.Series(dtype=int)
    error_types = pd.Series(dtype=int)

# === SECTION 1: KEY ERROR METRICS ===
st.subheader("📊 Error Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    metric_card("Total Errors", f"{total_errors:,}", icon="⚠️")

with col2:
    metric_card("Error Rate", f"{overall_error_rate:.2f}%", 
                delta="-1.2%" if overall_error_rate < 5 else "+0.8%",
                delta_color="inverse", icon="📉")

with col3:
    metric_card("Affected Users", f"{affected_users:,}", icon="👥")

with col4:
    user_impact = (affected_users / total_users) * 100 if total_users > 0 else 0
    metric_card("User Impact", f"{user_impact:.1f}%", icon="🎯")

# Status indicator
st.markdown("---")
if overall_error_rate < 3:
    status_badge("excellent", "🟢 Error Rate: Excellent (< 3%)")
    st.success("Error rate is within acceptable limits!")
elif overall_error_rate < 5:
    status_badge("good", "🟡 Error Rate: Good (< 5%)")
    st.info("Error rate is acceptable but monitor closely.")
else:
    status_badge("danger", "🔴 Error Rate: High (> 5%)")
    st.error("Error rate requires immediate attention!")

st.markdown("---")

# === SECTION 2: ERROR TREND ===
st.subheader("📈 Error Rate Trend")

# Calculate daily error rates
df_behavior['date'] = pd.to_datetime(df_behavior['timestamp']).dt.date
daily_errors = df_behavior.groupby('date').agg({
    'error_occurred': ['sum', 'count']
}).reset_index()
daily_errors.columns = ['date', 'errors', 'total']
daily_errors['error_rate'] = (daily_errors['errors'] / daily_errors['total']) * 100

col1, col2 = st.columns([3, 1])

with col1:
    # Line chart for error trend
    fig = px.line(
        daily_errors,
        x='date',
        y='error_rate',
        title="Daily Error Rate Trend",
        labels={'error_rate': 'Error Rate (%)', 'date': 'Date'},
        markers=True
    )
    
    fig.add_hline(y=5, line_dash="dash", line_color="red", 
                  annotation_text="Critical Threshold: 5%")
    fig.add_hline(y=3, line_dash="dash", line_color="orange", 
                  annotation_text="Warning Threshold: 3%")
    
    fig.update_traces(line_color='#ef4444')
    st.plotly_chart(fig, use_column_width=True)

with col2:
    st.markdown("### Trend Analysis")
    
    # Calculate trend
    if len(daily_errors) >= 2:
        recent_rate = daily_errors['error_rate'].tail(3).mean()
        previous_rate = daily_errors['error_rate'].head(3).mean()
        trend_change = recent_rate - previous_rate
        
        st.metric("Recent Avg", f"{recent_rate:.2f}%")
        st.metric("Previous Avg", f"{previous_rate:.2f}%")
        st.metric("Trend Change", f"{trend_change:+.2f}%",
                 delta_color="inverse")
    
    st.markdown("---")
    st.markdown("**Target Thresholds:**")
    st.markdown("- 🟢 Excellent: < 3%")
    st.markdown("- 🟡 Warning: 3-5%")
    st.markdown("- 🔴 Critical: > 5%")

st.markdown("---")

# === SECTION 3: ERROR DISTRIBUTION ANALYSIS ===
st.subheader("🔍 Error Distribution Analysis")

# Filter error records
error_records = df_behavior[df_behavior['error_occurred'] == True]

if len(error_records) > 0:
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 By Page", "🎯 By Action", "📱 By Device"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Errors by page
            error_by_page = error_records['page'].value_counts()
            
            fig = px.bar(
                x=error_by_page.values,
                y=error_by_page.index,
                orientation='h',
                title="Errors by Page",
                labels={'x': 'Error Count', 'y': 'Page'},
                color=error_by_page.values,
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_column_width=True)
        
        with col2:
            st.markdown("### Top Error Pages")
            
            for idx, (page, count) in enumerate(error_by_page.head(5).items(), 1):
                percentage = (count / total_errors) * 100
                
                if percentage > 30:
                    icon = "🔴"
                    color = "#fee2e2"
                elif percentage > 15:
                    icon = "🟡"
                    color = "#fef3c7"
                else:
                    icon = "🟢"
                    color = "#dbeafe"
                
                st.markdown(f"""
                <div style='background-color: {color}; padding: 0.5rem; border-radius: 0.5rem; margin-bottom: 0.5rem;'>
                    {idx}. {icon} <strong>{page}</strong><br>
                    Count: {count:,} ({percentage:.1f}%)
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Errors by action type
            error_by_action = error_records['action_type'].value_counts()
            
            fig = px.pie(
                values=error_by_action.values,
                names=error_by_action.index,
                title="Error Distribution by Action Type",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Reds_r
            )
            st.plotly_chart(fig, use_column_width=True)
        
        with col2:
            st.markdown("### Action Types")
            
            for idx, (action, count) in enumerate(error_by_action.items(), 1):
                percentage = (count / total_errors) * 100
                st.markdown(f"{idx}. **{action}**: {count:,} ({percentage:.1f}%)")
    
    with tab3:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Errors by device
            error_by_device = error_records['device_type'].value_counts()
            
            fig = px.bar(
                x=error_by_device.index,
                y=error_by_device.values,
                title="Errors by Device Type",
                labels={'x': 'Device Type', 'y': 'Error Count'},
                color=error_by_device.values,
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_column_width=True)
        
        with col2:
            st.markdown("### Device Breakdown")
            
            for idx, (device, count) in enumerate(error_by_device.items(), 1):
                percentage = (count / total_errors) * 100
                st.markdown(f"{idx}. **{device}**: {count:,} ({percentage:.1f}%)")

else:
    st.success("🎉 No errors recorded! System is running smoothly.")

st.markdown("---")

# === SECTION 4: ERROR BY PAGE ===
st.subheader("📄 Error Distribution by Page")

# Calculate error rate by page
page_errors = df_behavior.groupby('page').agg({
    'error_occurred': ['sum', 'count']
}).reset_index()
page_errors.columns = ['page', 'errors', 'total']
page_errors['error_rate'] = (page_errors['errors'] / page_errors['total']) * 100
page_errors = page_errors.sort_values('error_rate', ascending=False)

col1, col2 = st.columns([2, 1])

with col1:
    # Heatmap style visualization
    fig = px.bar(
        page_errors,
        x='page',
        y='error_rate',
        title="Error Rate by Page",
        labels={'error_rate': 'Error Rate (%)', 'page': 'Page'},
        color='error_rate',
        color_continuous_scale='Reds',
        text='error_rate'
    )
    
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.add_hline(y=5, line_dash="dash", line_color="red")
    st.plotly_chart(fig, use_column_width=True)

with col2:
    st.markdown("### Problem Pages")
    st.markdown("*Pages with highest error rates*")
    
    for idx, row in page_errors.head(5).iterrows():
        page = row['page']
        rate = row['error_rate']
        errors = row['errors']
        
        if rate > 10:
            color = "#fee2e2"
            icon = "🔴"
        elif rate > 5:
            color = "#fef3c7"
            icon = "🟡"
        else:
            color = "#dbeafe"
            icon = "🟢"
        
        st.markdown(f"""
        <div style='background-color: {color}; padding: 0.5rem; border-radius: 0.5rem; margin-bottom: 0.5rem;'>
            {icon} <strong>{page}</strong><br>
            Rate: {rate:.1f}% | Errors: {errors:,}
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# === SECTION 5: ERROR BY DEVICE & BROWSER ===
st.subheader("📱 Error Analysis by Device & Browser")

col1, col2 = st.columns(2)

with col1:
    # Error rate by device
    device_errors = df_behavior.groupby('device_type').agg({
        'error_occurred': ['sum', 'count']
    }).reset_index()
    device_errors.columns = ['device_type', 'errors', 'total']
    device_errors['error_rate'] = (device_errors['errors'] / device_errors['total']) * 100
    
    fig = px.bar(
        device_errors,
        x='device_type',
        y='error_rate',
        title="Error Rate by Device Type",
        labels={'error_rate': 'Error Rate (%)', 'device_type': 'Device'},
        color='error_rate',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig, use_column_width=True)

with col2:
    # Error rate by browser
    browser_errors = df_behavior.groupby('browser').agg({
        'error_occurred': ['sum', 'count']
    }).reset_index()
    browser_errors.columns = ['browser', 'errors', 'total']
    browser_errors['error_rate'] = (browser_errors['errors'] / browser_errors['total']) * 100
    
    fig = px.bar(
        browser_errors,
        x='browser',
        y='error_rate',
        title="Error Rate by Browser",
        labels={'error_rate': 'Error Rate (%)', 'browser': 'Browser'},
        color='error_rate',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig, use_column_width=True)

st.markdown("---")

# === SECTION 6: ERROR DETAILS TABLE ===
st.subheader("📋 Recent Errors (Last 50)")

# Filter errors only
recent_errors = df_behavior[df_behavior['error_occurred'] == True].nlargest(50, 'timestamp')

if len(recent_errors) > 0:
    # Display table
    error_table = recent_errors[['timestamp', 'user_id', 'page', 'error_type', 'device_type', 'browser']]
    
    st.dataframe(
        error_table.style.apply(
            lambda x: ['background-color: #fee2e2' if i % 2 == 0 else 'background-color: #ffffff' 
                      for i in range(len(x))],
            axis=0
        ),
        use_container_width=True
    )
    
    # Download button
    csv = error_table.to_csv(index=False)
    st.download_button(
        label="📥 Download Error Log",
        data=csv,
        file_name=f"error_log_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
else:
    st.success("🎉 No errors recorded! System is running smoothly.")

st.markdown("---")

# === SECTION 7: ERROR RESOLUTION RECOMMENDATIONS ===
st.subheader("💡 Error Resolution Recommendations")

recommendations = []

# Re-calculate error distributions for this section
error_records_current = df_behavior[df_behavior['error_occurred'] == True]

# 1. Check for high error pages
high_error_pages = page_errors[page_errors['error_rate'] > 5]
if len(high_error_pages) > 0:
    page_list = ', '.join(high_error_pages['page'].head(3).tolist())
    recommendations.append({
        'priority': 'High',
        'issue': f"{len(high_error_pages)} pages with error rate > 5%",
        'recommendation': f'Review and fix error handling on: {page_list}',
        'impact': 'User experience degradation affecting multiple pages',
        'action_items': [
            'Add detailed error logging',
            'Implement user-friendly error messages',
            'Add error recovery mechanisms'
        ]
    })

# 2. Check for device-specific issues
if not device_errors.empty and overall_error_rate > 0:
    high_device_errors = device_errors[device_errors['error_rate'] > overall_error_rate * 1.5]
    if len(high_device_errors) > 0:
        device_list = ', '.join(high_device_errors['device_type'].tolist())
        recommendations.append({
            'priority': 'Medium',
            'issue': 'Device-specific error rates above average',
            'recommendation': f'Test and optimize for: {device_list}',
            'impact': 'Platform compatibility issues',
            'action_items': [
                'Cross-device testing',
                'Device-specific error handling',
                'Responsive design improvements'
            ]
        })

# 3. Check for most problematic pages
if len(error_records_current) > 0:
    error_page_dist = error_records_current['page'].value_counts()
    if len(error_page_dist) > 0:
        top_error_page = error_page_dist.index[0]
        top_error_count = error_page_dist.iloc[0]
        error_percentage = (top_error_count / total_errors) * 100
        
        recommendations.append({
            'priority': 'High',
            'issue': f'Highest error concentration on "{top_error_page}" ({error_percentage:.1f}% of all errors)',
            'recommendation': f'Prioritize debugging {top_error_page} page with {top_error_count:,} errors',
            'impact': 'Single page causing majority of user frustration',
            'action_items': [
                'Code review for this page',
                'Add comprehensive error tracking',
                'User testing on this specific page'
            ]
        })

# 4. Overall error rate check
if overall_error_rate > 5:
    recommendations.append({
        'priority': 'Critical',
        'issue': f'Overall error rate is {overall_error_rate:.2f}% (CRITICAL - above 5% threshold)',
        'recommendation': 'Immediate action required: Implement comprehensive error tracking and prevention',
        'impact': 'Severe user experience degradation, potential revenue loss',
        'action_items': [
            'Emergency code review',
            'Implement global error handler',
            'Set up real-time alerting',
            'User communication plan'
        ]
    })
elif overall_error_rate > 3:
    recommendations.append({
        'priority': 'Medium',
        'issue': f'Error rate is {overall_error_rate:.2f}% (above warning threshold of 3%)',
        'recommendation': 'Review error logs and implement preventive measures',
        'impact': 'Potential user frustration and abandonment',
        'action_items': [
            'Weekly error log review',
            'Improve input validation',
            'Add error prevention checks'
        ]
    })

# 5. Check for action-specific errors
if len(error_records_current) > 0:
    error_action_dist = error_records_current['action_type'].value_counts()
    if len(error_action_dist) > 0:
        top_action = error_action_dist.index[0]
        action_count = error_action_dist.iloc[0]
        action_percentage = (action_count / total_errors) * 100
        
        if action_percentage > 50:
            recommendations.append({
                'priority': 'Medium',
                'issue': f'{action_percentage:.1f}% of errors occur during "{top_action}" action',
                'recommendation': f'Investigate and improve error handling for {top_action} interactions',
                'impact': 'Concentrated error pattern indicates specific functionality issue',
                'action_items': [
                    f'Debug {top_action} functionality',
                    'Add action-specific validation',
                    'Improve user guidance for this action'
                ]
            })

# Display recommendations
if recommendations:
    st.markdown(f"**Found {len(recommendations)} recommendations for improvement:**")
    
    for idx, rec in enumerate(recommendations, 1):
        priority_colors = {
            'Critical': '#fee2e2',
            'High': '#fef3c7',
            'Medium': '#dbeafe',
            'Low': '#f0f9ff'
        }
        
        priority_icons = {
            'Critical': '🚨',
            'High': '⚠️',
            'Medium': 'ℹ️',
            'Low': '💡'
        }
        
        color = priority_colors.get(rec['priority'], '#f0f2f6')
        icon = priority_icons.get(rec['priority'], '📌')
        
        # Build action items HTML
        action_items_html = ""
        if 'action_items' in rec:
            action_items_html = "<p><strong>Action Items:</strong></p><ul>"
            for item in rec['action_items']:
                action_items_html += f"<li>{item}</li>"
            action_items_html += "</ul>"
        
        st.markdown(f"""
        <div style='background-color: {color}; padding: 1rem; border-left: 4px solid #ef4444; margin-bottom: 1rem; border-radius: 0.5rem;'>
            <h4>{icon} #{idx} - Priority: {rec['priority']}</h4>
            <p><strong>Issue:</strong> {rec['issue']}</p>
            <p><strong>Recommendation:</strong> {rec['recommendation']}</p>
            <p><strong>Impact:</strong> {rec['impact']}</p>
            {action_items_html}
        </div>
        """, unsafe_allow_html=True)
else:
    st.success("✅ No critical issues detected. System is performing well!")
    
    st.markdown("""
    <div style='background-color: #d1fae5; padding: 1rem; border-radius: 0.5rem; margin-top: 1rem;'>
        <h4>🎉 Excellent Error Management!</h4>
        <p>Your system is running smoothly with minimal errors. Continue monitoring and maintaining current practices:</p>
        <ul>
            <li>✅ Error rate below 3% threshold</li>
            <li>✅ No critical error concentrations detected</li>
            <li>✅ Consistent performance across all devices</li>
            <li>✅ No single page or action causing significant issues</li>
        </ul>
        <p><strong>Recommended Actions:</strong></p>
        <ul>
            <li>Continue daily monitoring</li>
            <li>Maintain current error handling practices</li>
            <li>Regular code reviews</li>
            <li>User feedback collection</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# === SECTION 8: ERROR MONITORING BEST PRACTICES ===
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
    
    #### 3. **Error Prevention**
    - Input validation at frontend and backend
    - Comprehensive error handling
    - User-friendly error messages
    - Graceful degradation
    
    #### 4. **Resolution Process**
    ```
    Detect → Log → Classify → Prioritize → Fix → Verify → Document
    ```
    
    #### 5. **Key Metrics to Track**
    - Error rate (%)
    - Mean Time To Detect (MTTD)
    - Mean Time To Resolve (MTTR)
    - Error recurrence rate
    - User impact percentage
    """)

# === FOOTER ===
st.markdown("---")
st.caption("⚠️ Error Rate Analysis | Real-time error monitoring | Raudatul Sholehah (2310817220002)")
