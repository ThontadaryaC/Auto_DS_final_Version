import pandas as pd
import json
from agent.llm_config import get_llm
from langchain_core.messages import HumanMessage


def generate_ai_dashboard(df: pd.DataFrame, filename: str = "Unknown Dataset", semantic_profile: dict = None) -> dict:
    """Uses Gemini to analyze data and generate diverse Plotly visualizations and a report based on semantic profile."""
    llm = get_llm()
    
    # Prepare data summary for the LLM
    sample_data_json = df.head(3).to_json(orient='records', date_format='iso')
    cols_info = json.dumps({col: str(dtype) for col, dtype in df.dtypes.items()}, separators=(',', ':'))
    
    prompt = f"""
    You are a Lead Data Science Consultant.
    Dataset: {filename}
    Semantic Profile: {json.dumps(semantic_profile, separators=(',', ':')) if semantic_profile else "N/A"}
    Schema: {cols_info} 
    Sample: {sample_data_json}
    
    TASK: Generate 4 interactive Plotly charts and a professional analysis report.
    - RECOGNITION: Link semantic types to business entities.
    - ACCURACY: Use the Semantic Profile to pick the right column types.
    
    REPORT STRUCTURE (Concise 500-word executive summary):
    1. EXECUTIVE SUMMARY: High-level strategic value.
    2. ARCHITECTURE: Schema and quality.
    3. INSIGHTS: Distributions and correlations.
    4. ANOMALIES: Key deviations.
    5. RECOMMENDATIONS: Proactive advice.
    
    Return ONLY a JSON object:
    {{
      "charts": {{ "id1": {{ "data": [...], "layout": {{...}} }}, ... }},
      "report": "PROFESSIONAL ANALYSIS TEXT (Markdown formatted, approx 500 words)"
    }}
    NO MARKDOWN WRAPPING. NO COMMENTS. VALID JSON ONLY.
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
    cols_info = {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    context_prompts = {
        "insights": "Analyze the basic statistical insights of this data. Provide a professional context-aware summary of the bar chart findings emphasizing key distributions and outliers.",
        "prediction": f"Explain the future trends based on the machine learning forecast provided for {additional_context} steps. Focus on confidence levels and proactive business advice.",
        "dashboard": "Provide a high-level summary of the key performance indicators and patterns observed in the interactive dashboard."
    }

    task_prompt = context_prompts.get(view_type.lower(), "Provide a holistic data analysis report.")
    
    # Use to_json with head(3) and compact formatting
    sample_data_json = df.head(3).to_json(orient='records', date_format='iso')
    
    prompt = f"""
    You are a Principal Data Scientist.
    Sample: {sample_data_json}
    Architecture: {json.dumps(cols_info, separators=(',', ':'))}
    
    GOAL: {task_prompt}
    
    Deliver a professional, proactive report (approx 400 words).
    
    SECTIONS:
    - CONTEXT: Scope and scale.
    - BREAKDOWN: Variables and interactions.
    - PATTERNS: Synergy and influence.
    - FORECAST: Future outcomes.
    - ROADMAP: Priority actions.
    """
    
    try:
        llm = get_llm()
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except KeyError:
        return "AI Report Generation Failed: GEMINI_API_KEY is missing. Please configure it in your backend environment."
    except ConnectionError:
        return "AI Report Generation Failed: Could not connect to Gemini API. Please check your internet or API limits."
    except Exception as e:
        print(f"Error generating AI report for {view_type}: {e}")
        return f"AI was unable to generate a report for this view. (Error: {str(e)})"

def ai_observe_data(df: pd.DataFrame, filename: str = "Unknown Dataset", semantic_profile: dict = None) -> str:
    """Uses Gemini to provide a natural language summary/observation of the dataset."""
    llm = get_llm()
    
    # Use to_json with head(3) and compact formatting
    sample_data_json = df.head(3).to_json(orient='records', date_format='iso')
    cols_info = json.dumps({col: str(dtype) for col, dtype in df.dtypes.items()}, separators=(',', ':'))
    
    prompt = f"""
    You are an AI Strategist.
    Dataset: {filename}
    Profile: {json.dumps(semantic_profile, separators=(',', ':')) if semantic_profile else "N/A"}
    Schema: {cols_info}
    Sample: {sample_data_json}
    
    TASK: Provide a 2-sentence professional observation acknowledging the dataset.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
        print(f"Error observing data with AI: {e}")
        return f"Successfully processed {filename}. Ready for analysis."
