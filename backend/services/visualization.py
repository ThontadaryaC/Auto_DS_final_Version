import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import plotly.utils
from utils.viz_utils import get_seaborn_colors, apply_premium_style

def generate_insights_chart(df: pd.DataFrame) -> dict:
    """Generates a premium interactive bar chart for insights using Seaborn-style colors."""
    if df.empty:
        return {"data": [], "layout": {"title": "No data available"}}

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
    
    try:
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
    except Exception as e:
        print(f"Error in generate_insights_chart: {e}")
        return {"data": [], "layout": {"title": f"Visualization error: {str(e)}"}}

def generate_strategy_chart(df: pd.DataFrame, strategy: dict) -> dict:
    """Generates a high-level strategic overview chart based on the AI plan."""
    if df.empty:
        return {"data": [], "layout": {"title": "No data for strategy map"}}

    viz_config = strategy.get("strategy_viz", {})
    v_type = viz_config.get("type", "bar").lower()
    
    try:
        num_cols = df.select_dtypes(include='number').columns.tolist()
        
        if v_type == "radar" and len(num_cols) >= 3:
            categories = num_cols[:5]
            values = df[categories].mean().tolist()
            fig = go.Figure(data=go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                marker=dict(color='#6366f1')
            ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True)), title="Strategic Attribute Matrix")
        elif v_type == "scatter" and len(num_cols) >= 2:
            fig = px.scatter(df, x=num_cols[0], y=num_cols[1], title=f"Strategic Focus: {viz_config.get('data_focus', 'Relationship Overview')}")
        else:
            # Default to cardinality bar chart
            counts = df.nunique().sort_values(ascending=False).head(10)
            fig = px.bar(
                x=counts.index, y=counts.values,
                title="Strategic Dataset Overview (Cardinality Map)",
                labels={'x': 'Feature Name', 'y': 'Unique Count'},
                color_discrete_sequence=['#6366f1']
            )
            fig.update_layout(xaxis_title="Features", yaxis_title="Distinct Values")
            
        apply_premium_style(fig)
        return json.loads(fig.to_json())
    except Exception as e:
        print(f"Error in generate_strategy_chart: {e}")
        return generate_insights_chart(df)

def generate_insights_suite(df: pd.DataFrame, semantic_profile: dict = None) -> dict:
    """Generates a suite of statistical insights charts."""
    charts = {}
    mako_colors = get_seaborn_colors("mako", 10)
    flare_colors = get_seaborn_colors("flare", 10)
    
    num_cols = df.select_dtypes(include='number').columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
    
    # 1. Primary Feature Distribution
    if num_cols:
        col = num_cols[0]
        fig = px.histogram(df, x=col, title=f"Statistical Distribution: {col}", 
                          color_discrete_sequence=[mako_colors[0]], marginal="box", nbins=40)
        apply_premium_style(fig)
        charts['distribution'] = json.loads(fig.to_json())
        
    # 2. Correlation Multi-Matrix (if enough num cols)
    if len(num_cols) >= 2:
        corr = df[num_cols].corr().reset_index()
        fig = px.imshow(df[num_cols].corr(), text_auto=True, title="Feature Correlation Matrix",
                       color_continuous_scale="RdBu_r")
        apply_premium_style(fig)
        charts['correlation'] = json.loads(fig.to_json())

    # 3. Categorical Breakdown
    best_cat = None
    if cat_cols:
        for c in cat_cols:
            if 2 <= df[c].nunique() <= 15:
                best_cat = c
                break
        if not best_cat: best_cat = cat_cols[0]
        
        summary = df[best_cat].value_counts().reset_index().head(10)
        summary.columns = [best_cat, 'Count']
        fig = px.bar(summary, x=best_cat, y='Count', title=f"Population by {best_cat}",
                    color=best_cat, color_discrete_sequence=flare_colors)
        apply_premium_style(fig)
        charts['breakdown'] = json.loads(fig.to_json())

    # 4. Outlier Analysis (Boxplot)
    if num_cols:
        cols_to_plot = num_cols[:min(3, len(num_cols))]
        fig = px.box(df, y=cols_to_plot, title="Multi-Feature Value Variance",
                    color_discrete_sequence=[mako_colors[2]])
        apply_premium_style(fig)
        charts['outliers'] = json.loads(fig.to_json())
        
    return charts

def generate_dashboard(df: pd.DataFrame, semantic_profile: dict = None) -> dict:
    """Generate a comprehensive suite of PowerBI-style charts using semantic intelligence."""
    date_cols = []
    num_cols = []
    cat_cols = []
    
    # Smarter detection logic
    potential_pie_cols = []
    
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
                if 2 <= df[name].nunique() <= 12:
                    potential_pie_cols.append(name)
    
    if not num_cols:
        num_cols = df.select_dtypes(include='number').columns.tolist()
    if not cat_cols:
        cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
    if not date_cols:
        date_cols = df.select_dtypes(include=['datetime', 'datetimetz']).columns.tolist()

    # Also check numeric cols with low cardinality for pie charts (e.g. 1/0 or small ratings)
    for col in num_cols:
        if 2 <= df[col].nunique() <= 5:
            potential_pie_cols.append(col)

    charts = {}
    mako_colors = get_seaborn_colors("mako", 10)
    flare_colors = get_seaborn_colors("flare", 10)
    rocket_colors = get_seaborn_colors("rocket", 10)
    
    # 1. AI Recommended Plots
    if semantic_profile and "recommended_plots" in semantic_profile:
        for i, rec in enumerate(semantic_profile["recommended_plots"][:2]):
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

    # 2. Time Series
    if date_cols and num_cols:
        time_col = date_cols[0]
        val_col = num_cols[0]
        # Resample if needed? For now just plot first 500 for performance
        trend_data = df.sort_values(by=time_col).head(500).copy()
        fig_trend = px.area(
            trend_data, x=time_col, y=val_col,
            title=f"Trend Intensity: {val_col} over {time_col}",
            color_discrete_sequence=[mako_colors[0]]
        )
        apply_premium_style(fig_trend)
        charts['time_series'] = json.loads(fig_trend.to_json())

    # 3. Multi-Metric Histogram
    if len(num_cols) >= 2:
        fig_hist = px.histogram(
            df, x=num_cols[0], y=num_cols[1], histfunc="avg",
            title=f"Value Distribution Matrix: {num_cols[0]}",
            color_discrete_sequence=[flare_colors[4]],
            nbins=30
        )
        apply_premium_style(fig_hist)
        charts['dist_matrix'] = json.loads(fig_hist.to_json())

    # 4. COMPOSITION PIE CHART (Improved)
    best_pie = potential_pie_cols[0] if potential_pie_cols else (cat_cols[0] if cat_cols else None)
    if best_pie:
        pie_data = df[best_pie].value_counts().reset_index().head(8)
        pie_data.columns = [best_pie, 'Count']
        fig_pie = px.pie(
            pie_data, names=best_pie, values='Count',
            title=f"Composition Insight: {best_pie}",
            color_discrete_sequence=rocket_colors,
            hole=0.45
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        apply_premium_style(fig_pie)
        charts['pie_composition'] = json.loads(fig_pie.to_json())

    # 5. Correlation Scatter
    if len(num_cols) >= 2:
        fig_scatter = px.scatter(
            df, x=num_cols[0], y=num_cols[1], 
            marginal_x="histogram", marginal_y="rug",
            title=f"Impact Correlation: {num_cols[0]} ↔ {num_cols[1]}",
            color_discrete_sequence=[mako_colors[2]]
        )
        apply_premium_style(fig_scatter)
        charts['impact_scatter'] = json.loads(fig_scatter.to_json())

    # 6. Sunburst or Treemap for Complex Hierarchies (Bonus PowerBI vibe)
    if len(cat_cols) >= 2:
        path = cat_cols[:2]
        # Only use if cardinality is reasonable
        if df[path[0]].nunique() < 10 and df[path[1]].nunique() < 20:
            fig_tree = px.treemap(df, path=path, color=path[0],
                                 title="Hierarchical Feature Map",
                                 color_discrete_sequence=mako_colors)
            apply_premium_style(fig_tree)
            charts['hierarchy'] = json.loads(fig_tree.to_json())

    return charts

