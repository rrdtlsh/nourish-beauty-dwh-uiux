"""
Chart Components
Reusable chart functions with consistent styling
"""

import plotly.express as px
import plotly.graph_objects as go

# Color palette for charts
COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'info': '#3b82f6'
}

def create_funnel_chart(data, title="Conversion Funnel"):
    """
    Create a funnel chart for conversion analysis
    """
    fig = go.Figure(go.Funnel(
        y=list(data.keys()),
        x=list(data.values()),
        textinfo="value+percent initial",
        marker=dict(
            color=[COLORS['primary'], COLORS['info'], COLORS['warning'], 
                   COLORS['success'], COLORS['secondary']]
        )
    ))
    
    fig.update_layout(
        title=title,
        height=500,
        showlegend=False
    )
    
    return fig

def create_heuristic_radar(scores):
    """
    Create radar chart for heuristic evaluation scores
    """
    categories = list(scores.keys())
    values = list(scores.values())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Heuristic Scores',
        line_color=COLORS['primary']
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )
        ),
        showlegend=False,
        title="Nielsen's 10 Heuristics Evaluation",
        height=500
    )
    
    return fig

def create_time_series_chart(df, x_col, y_col, title):
    """
    Create time series line chart
    """
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        title=title,
        markers=True
    )
    
    fig.update_traces(line_color=COLORS['primary'])
    fig.update_layout(height=400)
    
    return fig

def create_bar_chart(df, x_col, y_col, title, orientation='v'):
    """
    Create bar chart with consistent styling
    """
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        title=title,
        orientation=orientation,
        color=y_col,
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(height=400)
    
    return fig
