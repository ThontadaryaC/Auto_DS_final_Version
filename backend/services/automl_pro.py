import pandas as pd
import numpy as np
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import r2_score, accuracy_score, f1_score
import plotly.express as px
import plotly.graph_objects as go
from utils.viz_utils import apply_premium_style, get_seaborn_colors

def run_advanced_automl(df: pd.DataFrame, target_col: str, task_type: str = "auto", semantic_profile: dict = None) -> dict:
    """
    High-precision AutoML engine.
    - Automatic task detection
    - Robust preprocessing (Scaling + OHE)
    - Model comparison
    """
    if target_col not in df.columns:
        return {"error": f"Target column '{target_col}' not found"}

    # Identify Features using Semantic Profile if available
    cols_to_drop = [target_col]
    if semantic_profile and "columns" in semantic_profile:
        for col_info in semantic_profile["columns"]:
            if col_info["semantic_type"] == "ID":
                cols_to_drop.append(col_info["name"])
    
    X = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
    y = df[target_col]
    
    # Pre-process Dates in X to numeric
    for col in X.columns:
        if pd.api.types.is_datetime64_any_dtype(X[col]):
            X[col] = X[col].apply(lambda x: x.toordinal() if pd.notnull(x) else 0)
    
    # Handle missing values in target
    mask = y.notna()
    X = X[mask]
    y = y[mask]

    # Detect Task Type
    if task_type == "auto":
        if pd.api.types.is_numeric_dtype(y) and y.nunique() > 10:
            task_type = "regression"
        else:
            task_type = "classification"

    # Identify Features
    num_features = X.select_dtypes(include=['number']).columns.tolist()
    cat_features = X.select_dtypes(exclude=['number']).columns.tolist()

    # Preprocessing Pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_features),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_features)
        ]
    )

    # 2. Define Models based on task
    if task_type == "regression":
        models = {
            "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
            "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42)
        }
        metric_name = "R-Squared"
    else:
        models = {
            "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
            "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, random_state=42)
        }
        metric_name = "Accuracy"

    # 3. Training & Selection
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    best_score = -np.inf
    best_model_name = ""
    best_pipe = None
    scores = {}

    for name, model in models.items():
        pipe = Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])
        try:
            pipe.fit(X_train, y_train)
            preds = pipe.predict(X_test)
            
            if task_type == "regression":
                score = r2_score(y_test, preds)
            else:
                score = accuracy_score(y_test, preds)
                
            scores[name] = score
            if score > best_score:
                best_score = score
                best_model_name = name
                best_pipe = pipe
        except Exception as e:
            print(f"Error training {name}: {e}")

    if best_pipe is None:
        return {"error": "AutoML training failed for all models"}

    # 4. Generate Performance Visualization
    test_preds = best_pipe.predict(X_test)
    colors = get_seaborn_colors("rocket", 2)
    
    if task_type == "regression":
        # Actual vs Predicted Plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=y_test, y=test_preds, mode='markers', name='Predictions', marker=dict(color=colors[0], opacity=0.6)))
        fig.add_trace(go.Scatter(x=[y_test.min(), y_test.max()], y=[y_test.min(), y_test.max()], mode='lines', name='Ideal Line', line=dict(color=colors[1], dash='dash')))
        fig.update_layout(title=f"AutoML Analysis: {target_col} (R²: {best_score:.4f})", xaxis_title="Actual Values", yaxis_title="Predicted Values")
    else:
        # Simple Bar for Accuracy
        fig = px.bar(
            x=list(scores.keys()), y=list(scores.values()),
            title=f"AutoML Task: {target_col} Classification",
            labels={'x': 'Model', 'y': 'Accuracy Score'},
            color=list(scores.values()),
            color_continuous_scale="Viridis",
            template="plotly_white"
        )

    apply_premium_style(fig)
    chart_json = json.loads(fig.to_json())

    return {
        "task_type": task_type,
        "best_model": best_model_name,
        "accuracy": f"{best_score * 100:.2f}%",
        "chart": chart_json,
        "main_chart": chart_json, # For consistency in AdvancedAnalysis.jsx
        "summary": f"Targeting '{target_col}' using a {best_model_name} {task_type}. Achieved industrial precision of {best_score * 100:.1f}%."
    }

