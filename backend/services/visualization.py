import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import plotly.utils
from utils.viz_utils import get_seaborn_colors, apply_premium_style

def generate_insights_chart(df: pd.DataFrame) -> dict:
    """Generates a premium interactive bar chart for insights using Seaborn-style colors."""
    cat_col = None
    num_col = None
    for col in df.columns:
        if df[col].dtype == 'object' or pd.api.types.is_categorical_dtype(df[col]) or str(df[col].dtype) == 'string':
            if not cat_col:
                cat_col = col
        elif pd.api.types.is_numeric_dtype(df[col]):
            if not num_col:
                num_col = col
                
    colors = get_seaborn_colors("mako", 10)
    
    if cat_col and num_col:
        summary = df.groupby(cat_col)[num_col].sum().reset_index().sort_values(by=num_col, ascending=False).head(10)
        fig = px.bar(
            summary, x=cat_col, y=num_col, 
            title=f"Top {num_col} by {cat_col}",
            color=cat_col,
            color_discrete_sequence=colors
        )
    else:
        col = df.columns[0]
        summary = df[col].value_counts().reset_index().head(10)
        summary.columns = [col, 'Count']
        fig = px.bar(
            summary, x=col, y='Count', 
            title=f"Frequency analysis: {col}",
            color=col,
            color_discrete_sequence=colors
        )
        
    apply_premium_style(fig)
    return json.loads(fig.to_json())

def generate_dashboard(df: pd.DataFrame) -> dict:
    """Generate a comprehensive suite of PowerBI-style charts."""
    num_cols = df.select_dtypes(include='number').columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
    
    charts = {}
    mako_colors = get_seaborn_colors("mako", 5)
    flare_colors = get_seaborn_colors("flare", 5)
    rocket_colors = get_seaborn_colors("rocket", 10)
    
    # Scatter Plot (Relationship)
    if len(num_cols) >= 2:
        fig_scatter = px.scatter(
            df, x=num_cols[0], y=num_cols[1], 
            title=f"Relationship: {num_cols[0]} vs {num_cols[1]}",
            template="plotly_white",
            color_discrete_sequence=mako_colors
        )
        apply_premium_style(fig_scatter)
        fig_scatter.update_traces(marker=dict(size=10, opacity=0.6, line=dict(width=1, color='DarkSlateGrey')))
        charts['scatter'] = json.loads(fig_scatter.to_json())
    
    # Bar Chart (Averages)
    if len(cat_cols) > 0 and len(num_cols) > 0:
        summary = df.groupby(cat_cols[0])[num_cols[0]].mean().reset_index().sort_values(by=num_cols[0], ascending=False).head(10)
        fig_bar = px.bar(
            summary, x=cat_cols[0], y=num_cols[0], 
            title=f"Average {num_cols[0]} per {cat_cols[0]}",
            color=cat_cols[0],
            color_discrete_sequence=flare_colors
        )
        apply_premium_style(fig_bar)
        charts['bar'] = json.loads(fig_bar.to_json())
        
    # Histogram (Distribution)
    if len(num_cols) > 0:
        fig_hist = px.histogram(
            df, x=num_cols[0], 
            title=f"Distribution Profile: {num_cols[0]}",
            color_discrete_sequence=[mako_colors[0]],
            nbins=30
        )
        apply_premium_style(fig_hist)
        fig_hist.update_layout(bargap=0.1)
        charts['histogram'] = json.loads(fig_hist.to_json())

    # Pie Chart (Market Share / Composition)
    if len(cat_cols) > 0:
        best_pie_col = cat_cols[0]
        for col in cat_cols:
            if 2 <= df[col].nunique() <= 10:
                best_pie_col = col
                break
        
        pie_data = df[best_pie_col].value_counts().reset_index().head(10)
        pie_data.columns = [best_pie_col, 'Count']
        fig_pie = px.pie(
            pie_data, names=best_pie_col, values='Count',
            title=f"Composition: {best_pie_col}",
            color_discrete_sequence=rocket_colors,
            hole=0.4 # Donut format
        )
        apply_premium_style(fig_pie)
        charts['pie'] = json.loads(fig_pie.to_json())

    # Box Plot (Outliers and Quartiles)
    if len(num_cols) > 0:
        if len(cat_cols) > 0 and df[cat_cols[0]].nunique() <= 10:
            fig_box = px.box(
                df, x=cat_cols[0], y=num_cols[0],
                title=f"Spread & Outliers: {num_cols[0]} by {cat_cols[0]}",
                color=cat_cols[0],
                color_discrete_sequence=flare_colors
            )
        else:
            fig_box = px.box(
                df, y=num_cols[0],
                title=f"Statistical Spread: {num_cols[0]}",
                color_discrete_sequence=[flare_colors[0]]
            )
        apply_premium_style(fig_box)
        charts['box'] = json.loads(fig_box.to_json())
        
    # Line Chart (Trend over Index)
    if len(num_cols) > 0:
        trend_col = num_cols[1] if len(num_cols) > 1 else num_cols[0]
        trend_data = df.head(100).reset_index()
        fig_line = px.line(
            trend_data, x=trend_data.index, y=trend_col,
            title=f"Sequential Trend: {trend_col} (Sample)",
            color_discrete_sequence=[rocket_colors[0]],
            markers=True
        )
        apply_premium_style(fig_line)
        charts['line'] = json.loads(fig_line.to_json())

    return charts
