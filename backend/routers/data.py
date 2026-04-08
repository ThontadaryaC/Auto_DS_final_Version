from fastapi import APIRouter, HTTPException, Body
from core.store import store
from core.database import get_upload_history, get_upload_by_id, clear_upload_history
from utils.file_parser import parse_file
from services.data_processing import clean_dataframe, get_insights
from services.visualization import generate_insights_chart, generate_dashboard
from services.ai_viz import generate_ai_dashboard, generate_view_report, ai_observe_data
from services.ml import predict_future_trends

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
    store.set_data(cleaned_df, record['filename'])
    
    insights = get_insights(cleaned_df)
    observation = ai_observe_data(cleaned_df)
    
    return {
        "message": f"Successfully loaded {record['filename']} from history",
        "insights": insights,
        "observation": observation
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
    
    # Use native pandas/plotly for charts to avoid Gemini JSON hallucination
    charts = generate_dashboard(df)
    return {"charts": charts}

@router.get("/predict")
async def get_prediction_view(model: str = "linear", periods: int = 10):
    df = store.get_data()
    if df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded")
    
    chart_data = predict_future_trends(df, model_name=model, periods=periods)
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
