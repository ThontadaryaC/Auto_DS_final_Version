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

def predict_future_trends(df: pd.DataFrame, model_name: str = "auto", periods: int = 10) -> dict:
    """Uses AutoML or specific ML models to predict future values."""
    num_cols = df.select_dtypes(include='number').columns.tolist()
    if not num_cols:
        return {"error": "No numerical columns available for prediction"}
        
    # Pick target column based on variance (basic automation)
    target_col = num_cols[0]
    for col in num_cols:
        if df[col].var() > df[target_col].var():
            target_col = col
            
    X = np.arange(len(df)).reshape(-1, 1)
    y = df[target_col].fillna(df[target_col].mean()).values
    
    best_name = model_name
    
    # Model Selection logic
    if model_name == "auto":
        model, best_name, _ = evaluate_best_model(X, y)
        future_X = np.arange(len(df), len(df) + periods).reshape(-1, 1)
        future_y = model.predict(future_X)
    elif model_name == "random_forest":
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        future_X = np.arange(len(df), len(df) + periods).reshape(-1, 1)
        future_y = model.predict(future_X)
    elif model_name == "moving_average":
        window = 5
        last_values = y[-window:].tolist()
        future_y = []
        for _ in range(periods):
            avg = sum(last_values) / len(last_values)
            future_y.append(avg)
            last_values.pop(0)
            last_values.append(avg)
        future_X = np.arange(len(df), len(df) + periods).reshape(-1, 1)
    else: # Default: Linear Regression
        model = LinearRegression()
        model.fit(X, y)
        future_X = np.arange(len(df), len(df) + periods).reshape(-1, 1)
        future_y = model.predict(future_X)
        best_name = "linear"
    
    # Generate Premium Visualization using Seaborn colors
    colors = get_seaborn_colors("rocket", 2)
    fig = go.Figure()
    
    # Actual Data
    fig.add_trace(go.Scatter(
        x=X.flatten(), y=y, 
        mode='lines+markers', 
        name='Historical Data',
        line=dict(color=colors[0], width=3),
        marker=dict(size=6, opacity=0.7)
    ))
    
    # Prediction
    fig.add_trace(go.Scatter(
        x=future_X.flatten(), y=future_y, 
        mode='lines+markers', 
        name=f'Forecast ({best_name.replace("_", " ").title()})',
        line=dict(color=colors[1], width=3, dash='dash'),
        marker=dict(size=8, symbol='diamond')
    ))
    
    fig.update_layout(
        title=f"AutoML Analysis: {best_name.replace('_', ' ').title()} Forecast for {target_col}", 
        xaxis_title="Timeline/Index", 
        yaxis_title=target_col
    )
    
    apply_premium_style(fig)
    
    return {
        "chart": json.loads(fig.to_json()),
        "model_name": best_name.replace("_", " ").title()
    }
