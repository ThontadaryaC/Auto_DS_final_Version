from fastapi import APIRouter, HTTPException, Body
from core.store import store
from core.database import get_upload_history, get_upload_by_id, clear_upload_history
from utils.file_parser import parse_file
from services.data_processing import clean_dataframe, get_insights
from services.visualization import generate_insights_chart, generate_dashboard, generate_strategy_chart
from services.ai_viz import generate_ai_dashboard, generate_view_report, ai_observe_data
from services.ml import predict_future_trends
from services.ml_advanced import perform_clustering, detect_anomalies
from services.automl_pro import run_advanced_automl
from agent.orchestrator_pro import generate_strategic_plan

router = APIRouter()

@router.get("/history")
async def get_history():
    return get_upload_history()

@router.delete("/history")
async def clear_history():
    clear_upload_history()
    return {"message": "Upload history cleared successfully"}

@router.post("/load/{file_id}")
async def load_file_from_history(file_id: int):
    record = get_upload_by_id(file_id)
    if not record:
        raise HTTPException(status_code=404, detail="File record not found")
    
    df = await parse_file(record['file_path'])
    if df is None:
        raise HTTPException(status_code=400, detail="Failed to load file from disk")
        
    cleaned_df = clean_dataframe(df)
    
    # NEW: AI Semantic Profiling
    from services.semantic_logic import profile_dataset_with_ai
    semantic_profile = profile_dataset_with_ai(cleaned_df, record['filename'])
    
    store.set_data(cleaned_df, record['filename'])
    store.set_semantic_profile(semantic_profile)
    
    insights = get_insights(cleaned_df)
    observation = ai_observe_data(cleaned_df, record['filename'], semantic_profile)
    
    return {
        "message": f"Successfully loaded {record['filename']} from history",
        "insights": insights,
        "observation": observation,
        "semantic_profile": semantic_profile
    }

@router.get("/insights")
async def get_insights_view():
    df = store.get_data()
    if df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded")
    
    chart = generate_insights_chart(df)
    return {"chart": chart}

@router.get("/dashboard")
async def get_dashboard_view():
    df = store.get_data()
    if df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded")
    
    # Use semantic profile for smarter dashboard
    profile = store.get_semantic_profile()
    charts = generate_dashboard(df, profile)
    return {"charts": charts}

@router.get("/predict")
async def get_prediction_view(model: str = "linear", periods: int = 10):
    df = store.get_data()
    if df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded")
    
    profile = store.get_semantic_profile()
    chart_data = predict_future_trends(df, model_name=model, periods=periods, semantic_profile=profile)
    if "error" in chart_data:
        raise HTTPException(status_code=400, detail=chart_data["error"])
        
    return {
        "chart": chart_data["chart"],
        "model_name": chart_data.get("model_name", "AutoDS Model")
    }

@router.post("/report")
async def get_view_report(view_type: str = Body(..., embed=True), additional_context: str = Body("", embed=True)):
    df = store.get_data()
    if df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded")
        
    report = generate_view_report(df, view_type, additional_context)
    return {"report": report}

@router.get("/analyze/strategy")
async def get_ml_strategy():
    df = store.get_data()
    if df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded")
    
    filename = store.get_filename() or "Unknown"
    profile = store.get_semantic_profile()
    strategy = generate_strategic_plan(df, filename, profile)
    
    # NEW: Generate a strategic map visualization
    strategy_chart = generate_strategy_chart(df, strategy)
    strategy["strategy_chart"] = strategy_chart
    
    return strategy

@router.post("/analyze/clustering")
async def run_clustering_analysis(n_clusters: int = None, features: list = None):
    df = store.get_data()
    if df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded")
    
    result = perform_clustering(df, n_clusters=n_clusters, features=features)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/analyze/anomaly")
async def run_anomaly_analysis(contamination: float = 0.05):
    df = store.get_data()
    if df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded")
    
    result = detect_anomalies(df, contamination=contamination)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/analyze/automl")
async def run_pro_automl(target_col: str, task_type: str = "auto"):
    df = store.get_data()
    if df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded")
    
    profile = store.get_semantic_profile()
    result = run_advanced_automl(df, target_col=target_col, task_type=task_type, semantic_profile=profile)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
