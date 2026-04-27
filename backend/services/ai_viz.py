import pandas as pd
import json
from agent.llm_config import get_llm
from langchain_core.messages import HumanMessage


def generate_ai_dashboard(df: pd.DataFrame, filename: str = "Unknown Dataset", semantic_profile: dict = None) -> dict:
    """Uses Gemini to analyze data and generate diverse Plotly visualizations and a report based on semantic profile."""
    llm = get_llm()
    
    # Prepare data summary for the LLM
    # Use to_json to handle Timestamps/NaT properly
    sample_data_json = df.head(5).to_json(orient='records', date_format='iso')
    cols_info = {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    prompt = f"""
    You are a Lead Data Science Consultant and Strategist.
    Dataset Name: {filename}
    Semantic Profile: {json.dumps(semantic_profile) if semantic_profile else "Not available"}
    
    Raw Schema: {json.dumps(cols_info)} 
    Sample Data (5 rows): {sample_data_json}
    
    TASK: Generate 4 interactive Plotly charts and a comprehensive, multi-page professional analysis report.
    - RECOGNITION: Deeply analyze the "{filename}" domain. Connect semantic types to real-world business entities.
    - ACCURACY: Use the Semantic Profile to pick the right column types for high-fidelity visualizations.
    - COLORS: Use professional Seaborn palettes (e.g., mako, flare).
    
    REPORT STRUCTURE (Minimum 1500 words for depth):
    1. EXECUTIVE SUMMARY: A high-level overview of the dataset's strategic value.
    2. DATA ARCHITECTURE ANALYSIS: Detailed breakdown of the schema, quality, and semantic relationships.
    3. DESCRIPTIVE INSIGHTS: Deep dive into distributions, correlations, and composition.
    4. ANOMALY & OUTLIER DETECTION: Identifying patterns that deviate from the norm and their implications.
    5. STRATEGIC RECOMMENDATIONS: Proactive business advice based on the data findings.
    
    Return ONLY a JSON object:
    {{
      "charts": {{ "id1": {{ "data": [...], "layout": {{...}} }}, ... }},
      "report": "EXTREMELY DETAILED ANALYSIS TEXT (Multi-paragraph, formatted for a 2-page printout)"
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
    
    # FIX: Use to_json to handle Timestamps properly
    sample_data_json = df.head(5).to_json(orient='records', date_format='iso')
    
    prompt = f"""
    You are a Principal Data Scientist and Industry Specialist.
    
    Data Sample (JSON): {sample_data_json}
    Dataset Architecture: {json.dumps(cols_info)}
    
    GOAL: {task_prompt}
    
    Deliver an exhaustive, sophisticated, and proactive report designed to be at least 2 pages in length when printed.
    
    REQUIRED SECTIONS:
    - DETAILED CONTEXTUAL OVERVIEW: Scope and scale of the data.
    - GRANULAR STATISTICAL BREAKDOWN: Deep analysis of variables and their interactions.
    - PATTERN RECOGNITION & SYNERGY: How different data segments influence each other.
    - FORECASTING & RISK ASSESSMENT: Potential future outcomes and mitigation strategies.
    - STRATEGIC ROADMAP: Priority actions based on the insights discovered.
    
    Tone: Highly professional, Data-driven, and Strategic.
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
    
    # Prepare data summary for the LLM
    # Use to_json to handle Timestamps/NaT properly
    sample_data_json = df.head(3).to_json(orient='records', date_format='iso')
    cols_info = {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    prompt = f"""
    You are a Global AI Data Science Strategist.
    Dataset Name: {filename}
    
    Initial AI Recognition:
    {semantic_profile.get('filename_assessment', 'Assessing based on file name...') if semantic_profile else "No initial assessment available."}
    
    Detected Semantic Profile:
    {json.dumps(semantic_profile, indent=2) if semantic_profile else "No semantic profile available."}
    
    Raw Schema: {json.dumps(cols_info)}
    Sample Records: {sample_data_json}
    
    TASK:
    Provide a human-like strategic observation of this dataset.
    - Your response MUST be exactly two sentences (approx. 2 lines of text) long.
    - START by acknowledging your recognition of the dataset "{filename}".
    - Focus on the most critical business insight or pattern discovered.
    - Keep it brilliant, concise, and professional.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
        print(f"Error observing data with AI: {e}")
        return f"Successfully processed {filename}. Ready for analysis."
