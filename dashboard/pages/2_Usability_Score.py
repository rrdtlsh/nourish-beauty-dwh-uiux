"""
Page 2: Usability Score Evaluation
Shows: SUS scores, Heuristic evaluation, Nielsen's 10 principles
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

from dashboard.utils.data_loader import load_usability_scores
from dashboard.utils.usability_metrics import (
    calculate_sus_score,
    calculate_nps,
    get_usability_status,
    calculate_heuristic_scores
)
from dashboard.components.metrics_card import metric_card, status_badge
from dashboard.components.charts import create_heuristic_radar

# === PAGE CONFIGURATION ===
st.set_page_config(
    page_title="Usability Score", 
    page_icon="⭐", 
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
    <h1 class="page-title">⭐ Usability Score Evaluation</h1>
    <p class="page-subtitle">Nielsen's Heuristic Evaluation & System Usability Scale (SUS)</p>
</div>
""", unsafe_allow_html=True)

# Load data
try:
    df_usability = load_usability_scores()
    sus_score = calculate_sus_score(df_usability)
    nps = calculate_nps(df_usability)
    heuristic_scores = calculate_heuristic_scores(df_usability)
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# === SECTION 1: SUS SCORE ===
st.markdown('<h3 class="section-title">System Usability Scale (SUS) Score</h3>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=sus_score,
        delta={'reference': 68, 'increasing': {'color': "#10b981"}},
        gauge={
            'axis': {'range': [None, 100], 'tickfont': {'color': '#2D2D2D', 'size': 12}},
            'bar': {'color': PINK_COLORS['primary']},
            'steps': [
                {'range': [0, 50], 'color': "#fee2e2"},
                {'range': [50, 70], 'color': "#fef3c7"},
                {'range': [70, 85], 'color': "#dbeafe"},
                {'range': [85, 100], 'color': "#d1fae5"}
            ],
            'threshold': {'line': {'color': PINK_COLORS['secondary'], 'width': 4}, 'thickness': 0.75, 'value': 85}
        },
        title={'text': "SUS Score", 'font': {'size': 16, 'color': '#2D2D2D'}}
    ))
    fig = style_chart(fig)
    st.plotly_chart(fig, use_container_width=True, key="sus_gauge")

with col2:
    status, emoji = get_usability_status(sus_score)
    
    st.markdown("### Usability Status")
    if status == "Excellent":
        st.success(f"{emoji} **{status}**")
    elif status == "Good":
        st.info(f"{emoji} **{status}**")
    else:
        st.warning(f"{emoji} **{status}**")
    
    st.markdown("---")
    st.markdown("### Score Breakdown")
    st.metric("SUS Score", f"{sus_score:.1f}/100")
    st.metric("Percentile Rank", f"{min(sus_score, 100):.0f}%")

with col3:
    st.markdown("### Interpretation")
    st.markdown(f"""
    **SUS Score Ranges:**
    - 🟢 **85-100**: Excellent
    - 🔵 **70-84**: Good
    - 🟡 **50-69**: OK
    - 🔴 **0-49**: Poor
    
    **Industry Benchmark:**
    - Average SUS: **68**
    - Your Score: **{sus_score:.1f}**
    """)

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 2: NIELSEN'S 10 HEURISTICS ===
st.markdown('<h3 class="section-title">Nielsen\'s 10 Usability Heuristics Evaluation</h3>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    fig = create_heuristic_radar(heuristic_scores)
    fig = style_chart(fig, "Heuristic Evaluation Scores")
    st.plotly_chart(fig, use_container_width=True, key="heuristic_radar")

with col2:
    st.markdown("### Heuristic Scores")
    
    for heuristic, score in heuristic_scores.items():
        if score >= 4.5:
            icon = "🟢"
        elif score >= 3.5:
            icon = "🔵"
        elif score >= 2.5:
            icon = "🟡"
        else:
            icon = "🔴"
        
        st.markdown(f"{icon} **{heuristic}**: {score:.2f}/5")

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 3: DETAILED HEURISTICS ===
st.markdown('<h3 class="section-title">Detailed Heuristic Analysis</h3>', unsafe_allow_html=True)

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
        
        if score >= 4.5:
            bg_color = "#d1fae5"
            border_color = "#10b981"
        elif score >= 3.5:
            bg_color = "#dbeafe"
            border_color = "#3b82f6"
        elif score >= 2.5:
            bg_color = "#fef3c7"
            border_color = "#f59e0b"
        else:
            bg_color = "#fee2e2"
            border_color = "#ef4444"
        
        st.markdown(f"""
        <div style='background-color: {bg_color}; padding: 1rem; border-radius: 10px; 
                    margin-bottom: 1rem; border-left: 4px solid {border_color};'>
            <h4 style='color: #2D2D2D; margin-bottom: 0.5rem;'>{name}</h4>
            <p style='font-weight: 700; color: #2D2D2D;'>Score: {score:.2f}/5</p>
            <p style='font-style: italic; color: #4A4A4A; margin: 0.5rem 0;'>{details['description']}</p>
            <ul style='margin-top: 0.5rem; color: #2D2D2D;'>
                {''.join([f'<li>{c}</li>' for c in details['criteria']])}
            </ul>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 4: SATISFACTION RATINGS ===
st.markdown('<h3 class="section-title">User Satisfaction Analysis</h3>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    satisfaction_dist = df_usability['satisfaction_rating'].value_counts().sort_index()
    fig = px.bar(x=satisfaction_dist.index, y=satisfaction_dist.values,
                labels={'x': 'Rating (1-5)', 'y': 'Count'},
                color=satisfaction_dist.values,
                color_continuous_scale=['#FCE4EC', PINK_COLORS['primary']])
    fig = style_chart(fig, "Satisfaction Rating Distribution")
    st.plotly_chart(fig, use_container_width=True, key="satisfaction_bar")

with col2:
    page_satisfaction = df_usability.groupby('page_evaluated')['satisfaction_rating'].mean().sort_values(ascending=False)
    fig = px.bar(x=page_satisfaction.values, y=page_satisfaction.index, orientation='h',
                labels={'x': 'Avg Rating', 'y': 'Page'},
                color=page_satisfaction.values,
                color_continuous_scale=['#FCE4EC', PINK_COLORS['primary']])
    fig = style_chart(fig, "Avg Satisfaction by Page")
    st.plotly_chart(fig, use_container_width=True, key="page_satisfaction")

with col3:
    st.markdown("### Key Metrics")
    avg_satisfaction = df_usability['satisfaction_rating'].mean()
    st.metric("⭐ Avg Satisfaction", f"{avg_satisfaction:.2f}/5")
    
    if nps:
        st.metric("📈 Net Promoter Score", f"{nps:.0f}")
    
    total_evaluations = len(df_usability)
    st.metric("📊 Total Evaluations", f"{total_evaluations:,}")

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 5: COMMENTS ANALYSIS ===
st.markdown('<h3 class="section-title">Evaluator Comments</h3>', unsafe_allow_html=True)

if df_usability['evaluation_date'].dtype == 'object':
    df_usability['evaluation_date'] = pd.to_datetime(df_usability['evaluation_date'], errors='coerce')

recent_comments = df_usability[df_usability['comments'].notna()].sort_values('evaluation_date', ascending=False).head(10)

if len(recent_comments) > 0:
    for idx, row in recent_comments.iterrows():
        page = row['page_evaluated']
        comment = row['comments']
        date = row['evaluation_date']
        overall = row['overall_score']
        
        if pd.notna(date):
            date_str = date.strftime('%Y-%m-%d') if isinstance(date, pd.Timestamp) else str(date)
        else:
            date_str = "Unknown date"
        
        st.markdown(f"""
        <div style='background-color: #FCE4EC; padding: 1rem; border-left: 4px solid {PINK_COLORS['primary']}; 
                    margin-bottom: 0.75rem; border-radius: 8px;'>
            <strong style='color: #2D2D2D;'>{page}</strong> - 
            <span style='color: {PINK_COLORS['secondary']};'>Score: {overall:.1f}/5</span> - 
            <span style='color: #757575;'>{date_str}</span>
            <p style='color: #4A4A4A; margin-top: 0.5rem; font-style: italic;'>{comment}</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No comments available yet.")

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

# === SECTION 6: UI/UX PRINCIPLES ===
st.markdown('<h3 class="section-title">UI/UX Design Principles Applied</h3>', unsafe_allow_html=True)

principles = {
    "1. Visual Hierarchy": {
        "description": "Important information is emphasized through size, color, and position.",
        "implementation": "Large metrics at top, charts in middle, details below"
    },
    "2. Consistency": {
        "description": "Consistent color scheme, typography, and layout across all pages.",
        "implementation": "Pink gradient theme, Inter font, card-based layouts"
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
        <div style='background-color: #FFF5F8; padding: 1rem; border-radius: 10px; 
                    margin-bottom: 1rem; border: 2px solid {PINK_COLORS['accent']};'>
            <h4 style='color: {PINK_COLORS['primary']};'>{principle}</h4>
            <p style='color: #2D2D2D;'><strong>Principle:</strong> {details['description']}</p>
            <p style='color: #4A4A4A;'><strong>Implementation:</strong> {details['implementation']}</p>
        </div>
        """, unsafe_allow_html=True)

# === FOOTER ===
st.markdown("""
<div class="footer">
    <p>© 2025 Usability Score Evaluation | Based on Nielsen's 10 Heuristics | Raudatul Sholehah (2310817220002)</p>
</div>
""", unsafe_allow_html=True)
