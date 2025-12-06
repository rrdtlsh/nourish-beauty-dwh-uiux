"""
Usability Metrics Calculator - FIXED VERSION
"""

import pandas as pd
import numpy as np

def calculate_sus_score(df):
    """Calculate System Usability Scale (SUS) Score"""
    if 'sus_score' in df.columns:
        return df['sus_score'].mean()
    return None

def calculate_nps(df):
    """Calculate Net Promoter Score (NPS)"""
    if 'satisfaction_rating' not in df.columns:
        return None
    
    promoters = (df['satisfaction_rating'] >= 4).sum()
    detractors = (df['satisfaction_rating'] <= 2).sum()
    total = len(df)
    
    nps = ((promoters - detractors) / total) * 100
    return round(nps, 2)

def calculate_task_success_rate(df):
    """Calculate task completion success rate"""
    if 'completed_purchase' not in df.columns:
        return None
    
    success_rate = (df['completed_purchase'].sum() / len(df)) * 100
    return round(success_rate, 2)

def calculate_time_on_task(df):
    """Average time spent on completing tasks"""
    if 'dwell_time_seconds' in df.columns:
        return df['dwell_time_seconds'].mean()
    elif 'time_to_conversion_minutes' in df.columns:
        return df['time_to_conversion_minutes'].mean()
    return None

def calculate_error_rate(df):
    """Calculate error rate percentage - FIXED"""
    # Handle both 'error_occurred' (boolean) and 'is_error' (integer)
    if 'error_occurred' in df.columns:
        error_rate = (df['error_occurred'].sum() / len(df)) * 100
    elif 'is_error' in df.columns:
        error_rate = (df['is_error'].sum() / len(df)) * 100
    else:
        return None
    
    return round(error_rate, 2)

def get_usability_status(score):
    """Get usability status based on score"""
    if score >= 85:
        return "Excellent", "🟢"
    elif score >= 70:
        return "Good", "🟡"
    elif score >= 50:
        return "OK", "🟠"
    else:
        return "Poor", "🔴"

def calculate_heuristic_scores(df):
    """Calculate average scores for Nielsen's 10 Heuristics"""
    heuristic_columns = [
        'visibility_score',
        'match_system_score',
        'user_control_score',
        'consistency_score',
        'error_prevention_score',
        'recognition_score',
        'flexibility_score',
        'aesthetic_score',
        'help_users_score',
        'documentation_score'
    ]
    
    scores = {}
    for col in heuristic_columns:
        if col in df.columns:
            scores[col.replace('_score', '').replace('_', ' ').title()] = df[col].mean()
    
    return scores
