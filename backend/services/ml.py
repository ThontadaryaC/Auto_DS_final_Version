import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import plotly.express as px
import plotly.graph_objects as go
import json
from utils.viz_utils import get_seaborn_colors, apply_premium_style

def evaluate_best_model(X: np.ndarray, y: np.ndarray):
    """Trains multiple models and selects the one with the lowest MSE using a chronological split."""
    if len(X) < 5:
        return LinearRegression(), "linear", 0
        
    # Chronological Split: use the last 20% of the data to test forecasting ability
    split_idx = max(int(len(X) * 0.8), 2)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    from sklearn.linear_model import LinearRegression, Ridge
    from sklearn.svm import SVR
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.pipeline import make_pipeline
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

    # Models to evaluate for forecasting
    models = {
        "linear": LinearRegression(),
        "ridge": Ridge(alpha=1.0),
        "polynomial_degree_2": make_pipeline(PolynomialFeatures(degree=2), LinearRegression()),
        "polynomial_degree_3": make_pipeline(PolynomialFeatures(degree=3), Ridge(alpha=1.0)),
        "svr_linear": SVR(kernel='linear', C=1.0),
        "gradient_boosting": GradientBoostingRegressor(n_estimators=50, random_state=42),
        "random_forest": RandomForestRegressor(n_estimators=50, random_state=42)
    }
    
    best_model_name = "linear"
    min_mse = float('inf')
    best_model = models["linear"]
    
    for name, model in models.items():
        try:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            mse = mean_squared_error(y_test, preds)
            
            if mse < min_mse:
                min_mse = mse
                best_model_name = name
                best_model = model
        except Exception:
            continue
            
    # Retrain best model on full data
    best_model.fit(X, y)
    return best_model, best_model_name, min_mse

def predict_future_trends(df: pd.DataFrame, model_name: str = "auto", periods: int = 10, semantic_profile: dict = None) -> dict:
    """Uses AutoML or specific ML models to predict future values with semester awareness."""
    date_cols = []
    num_cols = []
    
    if semantic_profile and "columns" in semantic_profile:
        for col_info in semantic_profile["columns"]:
            if col_info["semantic_type"] == "Date":
                date_cols.append(col_info["name"])
            elif col_info["semantic_type"] in ["Numeric", "Currency", "Age"]:
                num_cols.append(col_info["name"])
    
    if not num_cols:
        num_cols = df.select_dtypes(include='number').columns.tolist()
    if not date_cols:
        date_cols = df.select_dtypes(include=['datetime', 'datetimetz']).columns.tolist()

    if not num_cols:
        return {"error": "No numerical columns available for prediction"}
        
    # Target column selection
    target_col = num_cols[0]
    
    # Timeline generation
    if date_cols:
        time_col = date_cols[0]
        # Convert date to numeric ordinal for regression
        df_sorted = df.sort_values(by=time_col).dropna(subset=[time_col, target_col])
        X = df_sorted[time_col].apply(lambda x: x.toordinal()).values.reshape(-1, 1)
        y = df_sorted[target_col].values
        
        last_date = df_sorted[time_col].max()
        future_dates = [last_date + pd.Timedelta(days=i+1) for i in range(periods)]
        future_X = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
        x_axis_labels = future_dates
        hist_x = df_sorted[time_col]
        future_x = future_dates
    else:
        X = np.arange(len(df)).reshape(-1, 1)
        y = df[target_col].fillna(df[target_col].mean()).values
        future_X = np.arange(len(df), len(df) + periods).reshape(-1, 1)
        hist_x = X.flatten()
        future_x = future_X.flatten()

    best_name = model_name
    if model_name == "auto":
        model, best_name, _ = evaluate_best_model(X, y)
        future_y = model.predict(future_X)
    else:
        model = LinearRegression()
        model.fit(X, y)
        future_y = model.predict(future_X)
        best_name = "linear"
    
    # Generate Premium Visualization
    colors = get_seaborn_colors("rocket", 2)
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hist_x, y=y, 
        mode='lines+markers', 
        name='Historical Data',
        line=dict(color=colors[0], width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=future_x, y=future_y, 
        mode='lines+markers', 
        name=f'Forecast ({best_name.title()})',
        line=dict(color=colors[1], width=3, dash='dash')
    ))
    
    fig.update_layout(
        title=f"AI Forecast: {target_col} Trends", 
        xaxis_title="Timeline" if date_cols else "Index", 
        yaxis_title=target_col
    )
    
    apply_premium_style(fig)
    
    return {
        "chart": json.loads(fig.to_json()),
        "model_name": best_name.title()
    }
