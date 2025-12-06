"""
Filter Components
Reusable filter components for data filtering
"""

import streamlit as st
from datetime import datetime, timedelta

def date_range_filter():
    """
    Date range filter component
    """
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30),
            max_value=datetime.now()
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            max_value=datetime.now()
        )
    
    return start_date, end_date

def page_selector(pages_list):
    """
    Page multiselect filter
    """
    selected_pages = st.multiselect(
        "Select Pages",
        options=pages_list,
        default=pages_list
    )
    
    return selected_pages

def device_type_filter():
    """
    Device type filter
    """
    device_types = ['All', 'Desktop', 'Mobile', 'Tablet']
    selected_device = st.selectbox("Device Type", device_types)
    
    return selected_device if selected_device != 'All' else None
