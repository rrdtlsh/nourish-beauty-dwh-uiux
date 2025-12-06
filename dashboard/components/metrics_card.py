"""
Reusable Metric Card Component
"""

import streamlit as st

def metric_card(title, value, delta=None, delta_color="normal", icon="📊"):
    """
    Display a styled metric card
    
    Args:
        title: Metric title
        value: Metric value
        delta: Change value (optional)
        delta_color: Color of delta (normal, inverse, off)
        icon: Emoji icon
    """
    col1, col2 = st.columns([1, 5])
    
    with col1:
        st.markdown(f"<div style='font-size: 2.5rem;'>{icon}</div>", unsafe_allow_html=True)
    
    with col2:
        if delta:
            st.metric(
                label=title,
                value=value,
                delta=delta,
                delta_color=delta_color
            )
        else:
            st.metric(label=title, value=value)

def status_badge(status, message):
    """
    Display a status badge
    """
    colors = {
        'excellent': '#10b981',
        'good': '#3b82f6',
        'warning': '#f59e0b',
        'danger': '#ef4444'
    }
    
    color = colors.get(status.lower(), '#6b7280')
    
    st.markdown(
        f"""
        <div style='background-color: {color}; color: white; padding: 0.5rem 1rem; 
                    border-radius: 0.5rem; display: inline-block; font-weight: 600;'>
            {message}
        </div>
        """,
        unsafe_allow_html=True
    )
