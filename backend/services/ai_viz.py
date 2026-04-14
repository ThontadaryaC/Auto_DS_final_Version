import pandas as pd
import json
from agent.llm_config import get_llm
from langchain_core.messages import HumanMessage
import numpy as np

def generate_ai_dashboard(df: pd.DataFrame, filename: str = "Unknown Dataset", semantic_profile: dict = None) -> dict:
    """Uses Gemini to analyze data and generate diverse Plotly visualizations and a report based on semantic profile."""
    llm = get_llm()
    
    # Prepare data summary for the LLM
    # Use to_json to handle Timestamps/NaT properly
    sample_data_json = df.head(5).to_json(orient='records', date_format='iso')
    cols_info = {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    prompt = f"""
    You are a Senior Data Scientist.
    Dataset Name: {filename}
    Semantic Profile: {json.dumps(semantic_profile) if semantic_profile else "Not available"}
    
    Raw Schema: {json.dumps(cols_info)} 
    Sample Data (5 rows): {sample_data_json}
    
    TASK: Generate 4 interactive Plotly charts and a professional analysis summary.
    - RECOGNITION: Ensure you acknowledge the dataset "{filename}" domain.
    - ACCURACY: Use the Semantic Profile to pick the right column types (e.g. use Dates for X-axis Trend lines).
    - COLORS: Use professional Seaborn palettes. 
    - REPORT: Provide a professional analysis based on the recognized context.
    
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

def ai_observe_data(df: pd.DataFrame, filename: str = "Unknown Dataset", semantic_profile: dict = None) -> str:
    """Uses Gemini to provide a natural language summary/observation of the dataset."""
    llm = get_llm()
    
    # Prepare data summary for the LLM
    # Use to_json to handle Timestamps/NaT properly
    sample_data_json = df.head(3).to_json(orient='records', date_format='iso')
    cols_info = {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    prompt = f"""
    You are an AI Data Science Strategist.
    Dataset Name: {filename}
    
    Initial AI Recognition:
    {semantic_profile.get('filename_assessment', 'Assessing based on file name...') if semantic_profile else "No initial assessment available."}
    
    Detected Semantic Profile:
    {json.dumps(semantic_profile, indent=2) if semantic_profile else "No semantic profile available."}
    
    Raw Schema: {json.dumps(cols_info)}
    Sample Records: {sample_data_json}
    
    TASK:
    Provide a professional, "human-like" understanding of this dataset.
    - START by explicitly acknowledging your recognition of the dataset name "{filename}" and what it tells you about the context.
    - Then, connect this to the actual content you see in the columns and sample records.
    - Explain what the content represents in business terms.
    - Highlight 1-2 key patterns or relationships that are immediately visible.
    - Keep it concise (3-5 sentences).
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
        print(f"Error observing data with AI: {e}")
        return f"Successfully processed {filename}. Ready for analysis."
