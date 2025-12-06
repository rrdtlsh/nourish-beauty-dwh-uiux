"""
User Tracking Analytics - FIXED VERSION
"""

import pandas as pd
import numpy as np

def calculate_engagement_score(df):
    """Calculate user engagement score - FIXED"""
    if len(df) == 0:
        return 0
    
    # Normalize metrics to 0-100 scale
    time_score = min((df['dwell_time_seconds'].mean() / 180) * 100, 100)
    
    # Handle both click_count and clicks_count
    if 'click_count' in df.columns:
        click_score = min((df['click_count'].mean() / 20) * 100, 100)
    elif 'clicks_count' in df.columns:
        click_score = min((df['clicks_count'].mean() / 20) * 100, 100)
    else:
        click_score = 0
    
    scroll_score = df['scroll_depth_percent'].mean()
    
    # Weighted average
    engagement = (time_score * 0.4 + click_score * 0.3 + scroll_score * 0.3)
    return round(engagement, 2)

def identify_drop_off_points(df):
    """Identify where users drop off in the funnel"""
    funnel_steps = [
        'landed_homepage',
        'viewed_product',
        'added_to_cart',
        'initiated_checkout',
        'completed_purchase'
    ]
    
    drop_off_analysis = {}
    total_users = len(df)
    
    if total_users == 0:
        return drop_off_analysis
    
    for i, step in enumerate(funnel_steps):
        if step in df.columns:
            # Count TRUE values (boolean columns)
            users_at_step = df[step].sum()
            conversion_rate = (users_at_step / total_users) * 100
            
            if i > 0:
                prev_step = funnel_steps[i-1]
                prev_users = df[prev_step].sum()
                drop_off = prev_users - users_at_step
                drop_off_rate = (drop_off / prev_users) * 100 if prev_users > 0 else 0
            else:
                drop_off_rate = 0
            
            drop_off_analysis[step] = {
                'users': int(users_at_step),
                'conversion_rate': round(conversion_rate, 2),
                'drop_off_rate': round(drop_off_rate, 2)
            }
    
    return drop_off_analysis

def calculate_session_metrics(df):
    """Calculate session-level metrics - FIXED"""
    if len(df) == 0:
        return {}
    
    # Handle boolean vs integer is_bounce
    if 'is_bounce' in df.columns:
        if df['is_bounce'].dtype == 'int64':
            bounce_sum = df['is_bounce'].sum()
        else:
            bounce_sum = df['is_bounce'].sum()
        bounce_rate = (bounce_sum / len(df)) * 100
    else:
        bounce_rate = 0
    
    metrics = {
        'total_sessions': df['session_id'].nunique(),
        'avg_session_duration': df.groupby('session_id')['dwell_time_seconds'].sum().mean(),
        'avg_pages_per_session': df.groupby('session_id')['page'].count().mean(),
        'bounce_rate': bounce_rate
    }
    
    return {k: round(v, 2) for k, v in metrics.items()}

def analyze_user_journey(df):
    """Analyze common user journeys through the site"""
    # Group by session and create journey paths
    journeys = df.groupby('session_id')['page'].apply(lambda x: ' → '.join(x.tolist()))
    
    # Get most common paths
    common_paths = journeys.value_counts().head(10)
    
    return common_paths.to_dict()
