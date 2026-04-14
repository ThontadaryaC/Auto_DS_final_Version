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

def generate_dashboard(df: pd.DataFrame, semantic_profile: dict = None) -> dict:
    """Generate a comprehensive suite of PowerBI-style charts using semantic intelligence."""
    # Extract semantic info
    date_cols = []
    num_cols = []
    cat_cols = []
    
    if semantic_profile and "columns" in semantic_profile:
        for col_info in semantic_profile["columns"]:
            name = col_info["name"]
            stype = col_info["semantic_type"]
            if name not in df.columns: continue
            
            if stype == "Date":
                date_cols.append(name)
            elif stype in ["Numeric", "Currency", "Age"]:
                num_cols.append(name)
            elif stype in ["Category", "Geographic"]:
                cat_cols.append(name)
    
    # Fallback to dtypes if semantic profile is missing or incomplete
    if not num_cols:
        num_cols = df.select_dtypes(include='number').columns.tolist()
    if not cat_cols:
        cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
    if not date_cols:
        date_cols = df.select_dtypes(include=['datetime', 'datetimetz']).columns.tolist()

    charts = {}
    mako_colors = get_seaborn_colors("mako", 5)
    flare_colors = get_seaborn_colors("flare", 5)
    rocket_colors = get_seaborn_colors("rocket", 10)
    
    # 1. AI RECOMMENDED PLOTS (Highest Priority)
    if semantic_profile and "recommended_plots" in semantic_profile:
        for i, rec in enumerate(semantic_profile["recommended_plots"][:2]): # Top 2 AI recs
            try:
                ptype = rec["type"].lower()
                x, y = rec["x"], rec["y"]
                if x not in df.columns or y not in df.columns: continue
                
                if ptype == "line":
                    fig = px.line(df.sort_values(by=x), x=x, y=y, title=rec["reason"])
                elif ptype == "scatter":
                    fig = px.scatter(df, x=x, y=y, title=rec["reason"])
                elif ptype == "bar":
                    summary = df.groupby(x)[y].mean().reset_index().sort_values(by=y, ascending=False).head(10)
                    fig = px.bar(summary, x=x, y=y, title=rec["reason"])
                else:
                    continue
                
                apply_premium_style(fig)
                charts[f'ai_rec_{i}'] = json.loads(fig.to_json())
            except Exception:
                continue

    # 2. TREND OVER TIME (Using semantic Date)
    if date_cols and num_cols:
        time_col = date_cols[0]
        val_col = num_cols[0]
        # Resample or just sort for better line charts
        trend_data = df.sort_values(by=time_col).copy()
        fig_trend = px.line(
            trend_data, x=time_col, y=val_col,
            title=f"Evolution of {val_col} over {time_col}",
            color_discrete_sequence=[mako_colors[0]]
        )
        apply_premium_style(fig_trend)
        charts['time_series'] = json.loads(fig_trend.to_json())

    # 3. DISTRIBUTION (Histogram)
    if num_cols:
        fig_hist = px.histogram(
            df, x=num_cols[0], 
            title=f"Distribution Profile: {num_cols[0]}",
            color_discrete_sequence=[flare_colors[0]],
            nbins=30
        )
        apply_premium_style(fig_hist)
        charts['histogram'] = json.loads(fig_hist.to_json())

    # 4. COMPOSITION (Pie/Donut)
    if cat_cols:
        # Find best cat col (not unique, but not too many)
        best_cat = cat_cols[0]
        for c in cat_cols:
            if 2 <= df[c].nunique() <= 10:
                best_cat = c
                break
        
        pie_data = df[best_cat].value_counts().reset_index().head(10)
        pie_data.columns = [best_cat, 'Count']
        fig_pie = px.pie(
            pie_data, names=best_cat, values='Count',
            title=f"Composition of {best_cat}",
            color_discrete_sequence=rocket_colors,
            hole=0.4
        )
        apply_premium_style(fig_pie)
        charts['pie'] = json.loads(fig_pie.to_json())

    # 5. RELATIONSHIP (Scatter)
    if len(num_cols) >= 2:
        fig_scatter = px.scatter(
            df, x=num_cols[0], y=num_cols[1], 
            title=f"Correlation: {num_cols[0]} vs {num_cols[1]}",
            color_discrete_sequence=[mako_colors[1]]
        )
        apply_premium_style(fig_scatter)
        charts['scatter'] = json.loads(fig_scatter.to_json())

    return charts
