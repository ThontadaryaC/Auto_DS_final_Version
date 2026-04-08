import pandas as pd
import json
from agent.llm_config import get_llm
from langchain_core.messages import HumanMessage
import numpy as np

def generate_ai_dashboard(df: pd.DataFrame) -> dict:
    """Uses Gemini to analyze data and generate diverse Plotly visualizations and a report."""
    llm = get_llm()
    
    # Prepare data summary for the LLM
    sample_data = df.head(5).to_dict(orient='records')
    cols_info = {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    prompt = f"""
    You are a Senior Data Scientist.
    Dataset: {json.dumps(cols_info)} 
    Sample Data (5 rows): {json.dumps(sample_data)}
    
    TASK: Generate 4 interactive Plotly charts and a professional analysis summary.
    
    REQUIREMENTS:
    - 4 Charts with unique IDs.
    - Provide 'data' and 'layout' for each chart in Plotly JSON format.
    - COLORS: Use professional, high-contrast Seaborn-inspired color palettes (e.g., "Rocket", "Mako", "Viridis").
    - LAYOUT: Ensure charts have titles, gridlines, "plotly_white" template, and clean fonts (Inter or Sans-serif).
    - Analysis must be concise but deeply insightful (3 sentences).
    
    Return ONLY a JSON object:
    {{
      "charts": {{ "id1": {{ "data": [...], "layout": {{...}} }}, ... }},
      "report": "Analysis text"
    }}
    NO MARKDOWN. NO COMMENTS. VALID JSON ONLY.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        
        # Robust JSON cleaning
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        return json.loads(content)
    except Exception as e:
        print(f"Error generating AI dashboard: {e}")
        return {"charts": {}, "report": "Failed to generate AI Analysis for this dashboard."}

def generate_view_report(df: pd.DataFrame, view_type: str, additional_context: str = "") -> str:
    """Generates a contextual AI report for specific views like Insights or Prediction."""
    llm = get_llm()
    
    sample_data = df.head(5).to_dict(orient='records')
    cols_info = {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    context_prompts = {
        "insights": "Analyze the basic statistical insights of this data. Provide a professional context-aware summary of the bar chart findings emphasizing key distributions and outliers.",
        "prediction": f"Explain the future trends based on the machine learning forecast provided for {additional_context} steps. Focus on confidence levels and proactive business advice.",
        "dashboard": "Provide a high-level summary of the key performance indicators and patterns observed in the interactive dashboard."
    }
    
    task_prompt = context_prompts.get(view_type.lower(), "Provide a holistic data analysis report.")
    
    prompt = f"""
    You are a Lead Data Science Consultant for a Fortune 500 company.
    Data Sample: {json.dumps(sample_data)}
    Dataset Architecture: {json.dumps(cols_info)}
    
    GOAL: {task_prompt}
    
    Deliver a professional, insightful, and proactive report (3-4 sentences). 
    Focus on business value and strategic observations.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
        print(f"Error generating AI report for {view_type}: {e}")
        return "AI was unable to generate a report for this view."

def ai_observe_data(df: pd.DataFrame) -> str:
    """Uses Gemini to provide a natural language summary/observation of the dataset."""
    llm = get_llm()
    
    # Prepare data summary for the LLM
    sample_data = df.head(3).to_dict(orient='records')
    cols_info = {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    prompt = f"""
    You are an AI Data Science Strategist.
    Metadata Catalog: {json.dumps(cols_info)}
    Sample Records: {json.dumps(sample_data)}
    
    TASK:
    Analyze the structure and initial rows. Provide a concise (2-3 sentences) observation about the dataset's domain, potential use cases, and immediately visible patterns.
    Avoid stating the obvious; provide depth.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
        print(f"Error observing data with AI: {e}")
        return "Dataset successfully uploaded and processed. Ready for analysis."
