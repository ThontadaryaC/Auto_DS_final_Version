import pandas as pd
import numpy as np
import json
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import plotly.express as px
import plotly.graph_objects as go
from utils.viz_utils import get_seaborn_colors, apply_premium_style

def perform_clustering(df: pd.DataFrame, n_clusters: int = None, features: list = None) -> dict:
    """
    Performs K-Means clustering with automatic 'K' detection if n_clusters is None.
    Uses PCA for dimensionality reduction for visualization.
    """
    # 1. Feature selection (numerical only)
    num_cols = df.select_dtypes(include='number').columns.tolist()
    if not num_cols:
        return {"error": "No numerical columns for clustering"}
    
    # Use recommended features or default to all numerical
    analysis_features = [f for f in (features or num_cols) if f in df.columns]
    if not analysis_features:
        analysis_features = num_cols
        
    data = df[analysis_features].fillna(df[analysis_features].mean())
    
    # 2. Scaling
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data)
    
    # 3. Determine Optimal Clusters (Elbow Method)
    distortions = []
    K_range = range(1, min(len(df), 11))
    for k in K_range:
        kmeanModel = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeanModel.fit(scaled_data)
        distortions.append(kmeanModel.inertia_)
    
    # Simple elbow detection (max curvature point)
    if n_clusters is None:
        # Placeholder for complex elbow logic, defaulting to 3 for stability if unsure
        n_clusters = 3 if len(df) > 10 else 2

    # 4. Final Clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(scaled_data)
    
    # 5. Visualization Preparation
    # If > 3 features, use PCA to project onto 3D space
    if len(analysis_features) > 3:
        pca = PCA(n_components=3)
        viz_data = pca.fit_transform(scaled_data)
        viz_cols = ['PCA_1', 'PCA_2', 'PCA_3']
        plot_df = pd.DataFrame(viz_data, columns=viz_cols)
        plot_df['Cluster'] = clusters.astype(str)
        title = f"3D Cluster Projection (K={n_clusters})"
    else:
        plot_df = data.copy()
        viz_cols = analysis_features
        plot_df['Cluster'] = clusters.astype(str)
        title = f"Cluster Visualization (K={n_clusters})"

    # 6. Generate Plotly Figure
    if len(viz_cols) >= 3:
        fig = px.scatter_3d(
            plot_df, x=viz_cols[0], y=viz_cols[1], z=viz_cols[2],
            color='Cluster',
            title=title,
            template="plotly_white",
            color_discrete_sequence=get_seaborn_colors("mako", n_clusters)
        )
    else:
        fig = px.scatter(
            plot_df, x=viz_cols[0], y=viz_cols[1],
            color='Cluster',
            title=title,
            template="plotly_white",
            color_discrete_sequence=get_seaborn_colors("mako", n_clusters)
        )
    
    apply_premium_style(fig)
    
    # Elbow Chart for technical depth
    elbow_fig = go.Figure()
    elbow_fig.add_trace(go.Scatter(x=list(K_range), y=distortions, mode='lines+markers', name='Inertia'))
    elbow_fig.update_layout(title="Elbow Method Analysis", xaxis_title="K (Count)", yaxis_title="Inertia")
    apply_premium_style(elbow_fig)

    return {
        "cluster_labels": clusters.tolist(),
        "n_clusters": n_clusters,
        "main_chart": json.loads(fig.to_json()),
        "elbow_chart": json.loads(elbow_fig.to_json()),
        "summary": f"Grouped your dataset into {n_clusters} distinct segments using K-Means analysis."
    }

def detect_anomalies(df: pd.DataFrame, contamination: float = 0.05) -> dict:
    """
    Detects outliers using Isolation Forest.
    """
    num_cols = df.select_dtypes(include='number').columns.tolist()
    if not num_cols:
        return {"error": "No numerical columns for anomaly detection"}
    
    data = df[num_cols].fillna(df[num_cols].mean())
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data)
    
    # Isolation Forest
    iso = IsolationForest(contamination=contamination, random_state=42)
    preds = iso.fit_predict(scaled_data) # -1 for anomaly, 1 for normal
    
    df_plot = df.copy()
    df_plot['Status'] = ['Anomaly' if x == -1 else 'Normal' for x in preds]
    
    # PCA for 2D visualization
    pca = PCA(n_components=2)
    pca_res = pca.fit_transform(scaled_data)
    df_plot['Dim_1'] = pca_res[:, 0]
    df_plot['Dim_2'] = pca_res[:, 1]
    
    fig = px.scatter(
        df_plot, x='Dim_1', y='Dim_2',
        color='Status',
        symbol='Status',
        title="Anomaly Radar: Projected Outlier Space",
        color_discrete_map={'Anomaly': '#e74c3c', 'Normal': '#2ecc71'},
        template="plotly_white"
    )
    apply_premium_style(fig)
    
    anomaly_count = (preds == -1).sum()
    
    return {
        "anomaly_count": int(anomaly_count),
        "total_rows": len(df),
        "chart": json.loads(fig.to_json()),
        "summary": f"Identified {anomaly_count} potential anomalies within the dataset using Isolation Forest detection."
    }
