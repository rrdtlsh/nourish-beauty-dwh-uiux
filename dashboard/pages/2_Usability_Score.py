"""
Page 2: Usability Score Evaluation
Shows: SUS scores, Heuristic evaluation, Nielsen's 10 principles
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from dashboard.utils.data_loader import load_usability_scores
from dashboard.utils.usability_metrics import (
    calculate_sus_score,
    calculate_nps,
    get_usability_status,
    calculate_heuristic_scores
)
from dashboard.components.metrics_card import metric_card, status_badge
from dashboard.components.charts import create_heuristic_radar

st.set_page_config(page_title="Usability Score", page_icon="⭐", layout="wide")

# Header
st.markdown("""
<h1 style='text-align: center; color: #667eea;'>
    ⭐ Usability Score Evaluation
</h1>
<p style='text-align: center; color: #6b7280;'>
    Nielsen's Heuristic Evaluation & System Usability Scale (SUS)
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# Load data
try:
    df_usability = load_usability_scores()
    sus_score = calculate_sus_score(df_usability)
    nps = calculate_nps(df_usability)
    heuristic_scores = calculate_heuristic_scores(df_usability)
    
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# === SECTION 1: SUS SCORE ===
st.subheader("📊 System Usability Scale (SUS) Score")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    # SUS Score Gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=sus_score,
        delta={'reference': 68, 'increasing': {'color': "#10b981"}},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#667eea"},
            'steps': [
                {'range': [0, 50], 'color': "#fee2e2"},
                {'range': [50, 70], 'color': "#fef3c7"},
                {'range': [70, 85], 'color': "#dbeafe"},
                {'range': [85, 100], 'color': "#d1fae5"}
            ],
            'threshold': {
                'line': {'color': "green", 'width': 4},
                'thickness': 0.75,
                'value': 85
            }
        },
        title={'text': "SUS Score"}
    ))
    
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_column_width=True)

with col2:
    status, emoji = get_usability_status(sus_score)
    
    st.markdown("### Usability Status")
    status_badge(status.lower(), f"{emoji} {status}")
    
    st.markdown("---")
    st.markdown("### Score Breakdown")
    st.metric("SUS Score", f"{sus_score:.1f}/100")
    st.metric("Percentile Rank", f"{min(sus_score, 100):.0f}%")
    
with col3:
    st.markdown("### Interpretation")
    st.markdown("""
    **SUS Score Ranges:**
    - 🟢 **85-100**: Excellent
    - 🔵 **70-84**: Good
    - 🟡 **50-69**: OK
    - 🔴 **0-49**: Poor
    
    **Industry Benchmark:**
    - Average SUS: **68**
    - Your Score: **{:.1f}**
    """.format(sus_score))

st.markdown("---")

# === SECTION 2: NIELSEN'S 10 HEURISTICS ===
st.subheader("🎯 Nielsen's 10 Usability Heuristics Evaluation")

col1, col2 = st.columns([2, 1])

with col1:
    # Radar chart
    fig = create_heuristic_radar(heuristic_scores)
    st.plotly_chart(fig, use_column_width=True)

with col2:
    st.markdown("### Heuristic Scores")
    
    for heuristic, score in heuristic_scores.items():
        if score >= 4.5:
            icon = "🟢"
            color = "green"
        elif score >= 3.5:
            icon = "🔵"
            color = "blue"
        elif score >= 2.5:
            icon = "🟡"
            color = "orange"
        else:
            icon = "🔴"
            color = "red"
        
        st.markdown(f"{icon} **{heuristic}**: {score:.2f}/5")

st.markdown("---")

# === SECTION 3: DETAILED HEURISTICS ===
st.subheader("📋 Detailed Heuristic Analysis")

heuristic_details = {
    "Visibility": {
        "score": heuristic_scores.get("Visibility", 0),
        "description": "The system should always keep users informed about what is going on.",
        "criteria": ["Status feedback", "Progress indicators", "Clear system state"]
    },
    "Match System": {
        "score": heuristic_scores.get("Match System", 0),
        "description": "Use language familiar to users, not system-oriented terms.",
        "criteria": ["Natural language", "Real-world conventions", "User terminology"]
    },
    "User Control": {
        "score": heuristic_scores.get("User Control", 0),
        "description": "Users should have control and the ability to undo actions.",
        "criteria": ["Undo/Redo", "Exit options", "Clear navigation"]
    },
    "Consistency": {
        "score": heuristic_scores.get("Consistency", 0),
        "description": "Follow platform conventions and maintain internal consistency.",
        "criteria": ["UI patterns", "Terminology", "Design standards"]
    },
    "Error Prevention": {
        "score": heuristic_scores.get("Error Prevention", 0),
        "description": "Prevent errors before they occur through design.",
        "criteria": ["Constraints", "Confirmations", "Helpful defaults"]
    }
}

cols = st.columns(2)

for idx, (name, details) in enumerate(heuristic_details.items()):
    with cols[idx % 2]:
        score = details['score']
        
        # Color based on score
        if score >= 4.5:
            bg_color = "#d1fae5"
        elif score >= 3.5:
            bg_color = "#dbeafe"
        elif score >= 2.5:
            bg_color = "#fef3c7"
        else:
            bg_color = "#fee2e2"
        
        st.markdown(f"""
        <div style='background-color: {bg_color}; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
            <h4>{name}</h4>
            <p><strong>Score: {score:.2f}/5</strong></p>
            <p><em>{details['description']}</em></p>
            <ul>
                {''.join([f'<li>{c}</li>' for c in details['criteria']])}
            </ul>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# === SECTION 4: SATISFACTION RATINGS ===
st.subheader("😊 User Satisfaction Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    # Satisfaction distribution
    satisfaction_dist = df_usability['satisfaction_rating'].value_counts().sort_index()
    
    fig = px.bar(
        x=satisfaction_dist.index,
        y=satisfaction_dist.values,
        title="Satisfaction Rating Distribution",
        labels={'x': 'Rating (1-5)', 'y': 'Count'},
        color=satisfaction_dist.values,
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig, use_column_width=True)

with col2:
    # Average satisfaction by page
    page_satisfaction = df_usability.groupby('page_evaluated')['satisfaction_rating'].mean().sort_values(ascending=False)
    
    fig = px.bar(
        x=page_satisfaction.values,
        y=page_satisfaction.index,
        orientation='h',
        title="Avg Satisfaction by Page",
        labels={'x': 'Avg Rating', 'y': 'Page'},
        color=page_satisfaction.values,
        color_continuous_scale='Greens'
    )
    st.plotly_chart(fig, use_column_width=True)

with col3:
    st.markdown("### Key Metrics")
    
    avg_satisfaction = df_usability['satisfaction_rating'].mean()
    metric_card("Avg Satisfaction", f"{avg_satisfaction:.2f}/5", icon="⭐")
    
    if nps:
        metric_card("Net Promoter Score", f"{nps:.0f}", icon="📈")
    
    total_evaluations = len(df_usability)
    metric_card("Total Evaluations", f"{total_evaluations:,}", icon="📊")

st.markdown("---")

# === SECTION 5: COMMENTS ANALYSIS ===
st.subheader("💬 Evaluator Comments")

# Convert evaluation_date to datetime if it's not already
if df_usability['evaluation_date'].dtype == 'object':
    df_usability['evaluation_date'] = pd.to_datetime(df_usability['evaluation_date'], errors='coerce')

# Show recent comments - FIXED: sort by datetime properly
# Convert to datetime if needed
if df_usability['evaluation_date'].dtype == 'object':
    df_usability['evaluation_date'] = pd.to_datetime(df_usability['evaluation_date'], errors='coerce')

# Sort properly
recent_comments = df_usability[df_usability['comments'].notna()].sort_values('evaluation_date', ascending=False).head(10)

if len(recent_comments) > 0:
    for idx, row in recent_comments.iterrows():
        page = row['page_evaluated']
        comment = row['comments']
        date = row['evaluation_date']
        overall = row['overall_score']
        
        # Format date properly
        if pd.notna(date):
            date_str = date.strftime('%Y-%m-%d') if isinstance(date, pd.Timestamp) else str(date)
        else:
            date_str = "Unknown date"
        
        st.markdown(f"""
        <div style='background-color: #f9fafb; padding: 1rem; border-left: 4px solid #667eea; margin-bottom: 0.5rem;'>
            <strong>{page}</strong> - Score: {overall:.1f}/5 - {date_str}
            <p style='color: #6b7280; margin-top: 0.5rem;'>{comment}</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No comments available yet.")

st.markdown("---")

# === SECTION 6: UI/UX PRINCIPLES APPLIED ===
st.subheader("🎨 UI/UX Design Principles Applied in This Dashboard")

principles = {
    "1. Visual Hierarchy": {
        "description": "Important information is emphasized through size, color, and position.",
        "implementation": "Large metrics at top, charts in middle, details below"
    },
    "2. Consistency": {
        "description": "Consistent color scheme, typography, and layout across all pages.",
        "implementation": "Blue gradient theme, Roboto font, card-based layouts"
    },
    "3. Clarity": {
        "description": "Information presented in clear, understandable manner.",
        "implementation": "Plain language labels, tooltips, status indicators"
    },
    "4. Accessibility": {
        "description": "WCAG 2.1 AA compliant design with proper contrast ratios.",
        "implementation": "4.5:1 contrast ratio, keyboard navigation, screen reader support"
    },
    "5. Feedback": {
        "description": "System provides immediate feedback to user actions.",
        "implementation": "Loading states, success messages, error notifications"
    },
    "6. Readability": {
        "description": "Typography optimized for reading comfort.",
        "implementation": "16px base font, 1.6 line-height, proper spacing"
    }
}

cols = st.columns(2)

for idx, (principle, details) in enumerate(principles.items()):
    with cols[idx % 2]:
        st.markdown(f"""
        <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
            <h4 style='color: #667eea;'>{principle}</h4>
            <p><strong>Principle:</strong> {details['description']}</p>
            <p><strong>Implementation:</strong> {details['implementation']}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# === FOOTER ===
st.caption("⭐ Usability Score Evaluation | Based on Nielsen's 10 Heuristics | Raudatul Sholehah (2310817220002)")
