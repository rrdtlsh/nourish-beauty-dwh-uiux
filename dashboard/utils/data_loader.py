"""
Data Loader Utility
Centralized data loading functions - FIXED VERSION
"""

import pandas as pd
import streamlit as st
from sqlalchemy import text
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from database.connection import get_engine

@st.cache_resource
def get_db_connection():
    """Get database connection"""
    return get_engine()

@st.cache_data(ttl=300)
def load_user_behavior_data(limit=1000):
    """Load user behavior data from user_activity_log"""
    engine = get_db_connection()
    
    query = f"""
    SELECT 
        log_id,
        user_id,
        session_id,
        page,
        action as action_type,
        dwell_time_seconds,
        clicks_count as click_count,
        scroll_depth_percent,
        CASE WHEN is_bounce = 1 THEN TRUE ELSE FALSE END as is_bounce,
        device as device_type,
        'Unknown' as browser,
        timestamp,
        CASE WHEN is_error = 1 THEN TRUE ELSE FALSE END as error_occurred,
        'General Error' as error_type,
        conversion,
        session_duration,
        session_page_count
    FROM user_activity_log
    ORDER BY timestamp DESC
    LIMIT {limit}
    """
    
    return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def load_usability_scores():
    """Load usability evaluation scores"""
    engine = get_db_connection()
    query = """
    SELECT 
        evaluation_date,
        evaluator_id,
        page_evaluated,
        visibility_score,
        match_system_score,
        user_control_score,
        consistency_score,
        error_prevention_score,
        recognition_score,
        flexibility_score,
        aesthetic_score,
        help_users_score,
        documentation_score,
        overall_score,
        sus_score,
        satisfaction_rating,
        comments
    FROM fact_usability_score
    ORDER BY evaluation_date DESC
    """
    df = pd.read_sql(query, engine)
    
    # Convert evaluation_date to datetime
    df['evaluation_date'] = pd.to_datetime(df['evaluation_date'], errors='coerce')
    
    return df

@st.cache_data(ttl=300)
def load_dashboard_usage():
    """Load dashboard usage metrics"""
    engine = get_db_connection()
    query = """
    SELECT 
        usage_date,
        user_id,
        dashboard_page,
        visit_count,
        time_spent_seconds,
        interaction_count,
        filter_used,
        export_count,
        refresh_count,
        error_encountered,
        session_id,
        device_type,
        browser
    FROM fact_dashboard_usage
    ORDER BY usage_date DESC
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def load_user_funnel():
    """Load user funnel conversion data"""
    engine = get_db_connection()
    query = """
    SELECT 
        funnel_date,
        user_id,
        session_id,
        reached_landing as landed_homepage,
        viewed_product,
        added_to_cart,
        initiated_checkout,
        completed_purchase,
        time_to_purchase_minutes as time_to_conversion_minutes,
        exit_stage as drop_off_point,
        device_type,
        product_category,
        traffic_source
    FROM fact_user_funnel
    ORDER BY funnel_date DESC
    """
    df = pd.read_sql(query, engine)
    
    # Add funnel_step_reached column (derived)
    df['funnel_step_reached'] = df.apply(lambda row: 
        'Completed Purchase' if row['completed_purchase'] else
        'Initiated Checkout' if row['initiated_checkout'] else
        'Added to Cart' if row['added_to_cart'] else
        'Viewed Product' if row['viewed_product'] else
        'Landed Homepage' if row['landed_homepage'] else
        'Unknown', axis=1
    )
    
    return df

@st.cache_data(ttl=300)
def load_error_metrics():
    """Calculate error rates from user activity"""
    engine = get_db_connection()
    query = """
    SELECT 
        DATE(timestamp) as error_date,
        page,
        'Error' as error_type,
        COUNT(*) as error_count,
        COUNT(DISTINCT user_id) as affected_users
    FROM user_activity_log
    WHERE is_error = 1
    GROUP BY DATE(timestamp), page
    ORDER BY error_date DESC, error_count DESC
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def calculate_bounce_rate():
    """Calculate bounce rate by page"""
    engine = get_db_connection()
    query = """
    SELECT 
        page,
        COUNT(*) as total_visits,
        SUM(is_bounce) as bounces,
        ROUND(100.0 * SUM(is_bounce) / COUNT(*), 2) as bounce_rate
    FROM user_activity_log
    GROUP BY page
    ORDER BY bounce_rate DESC
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def get_click_path_analysis():
    """Analyze user click paths"""
    engine = get_db_connection()
    
    query = """
    SELECT 
        session_id,
        user_id,
        page,
        action as action_type,
        timestamp,
        ROW_NUMBER() OVER (PARTITION BY session_id ORDER BY timestamp) as step_number
    FROM user_activity_log
    WHERE clicks_count > 0
    ORDER BY session_id, timestamp
    LIMIT 5000
    """
    
    return pd.read_sql(query, engine)
