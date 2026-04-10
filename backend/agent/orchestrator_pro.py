import pandas as pd
import json
from agent.llm_config import get_llm
from langchain_core.messages import HumanMessage

def generate_strategic_plan(df: pd.DataFrame) -> dict:
    """
    Uses LLM to analyze dataset and decide the best ML strategy.
    Returns instructions for Clustering, Anomaly Detection, or AutoML.
    """
    llm = get_llm()
    
    # 1. Prepare Metadata for the LLM
    num_rows = len(df)
    sample_data = df.head(5).to_dict(orient='records')
    cols_info = {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    prompt = f"""
    You are a Master AI Data Scientist.
    Dataset Metadata: {num_rows} rows.
    Schema: {json.dumps(cols_info)}
    Sample Data (5 rows): {json.dumps(sample_data)}
    
    TASK: Analyze the dataset structure and domain. Decide on a 3-part strategic ML plan.
    
    STRATEGY OPTIONS:
    1. CLUSTERING: Groups similar records. Recommendation: Which features to use?
    2. ANOMALY: Detects outliers. Recommendation: Contamination rate (0.01 to 0.1)?
    3. AUTOML: Predicts a column. Recommendation: Best 'Target' column and Task Type?
    
    Return EXACTLY this JSON structure:
    {{
      "domain": "Domain of data (e.g. Finance, Retail, Health)",
      "thinking": "Professional reasoning for the plan (2 sentences max)",
      "clustering": {{
        "recommended_features": ["col1", "col2"],
        "suggested_k": 3
      }},
      "anomaly": {{
        "contamination": 0.05,
        "features": ["col1", "col2"]
      }},
      "automl": {{
        "target_col": "most_important_variable",
        "task_type": "regression/classification"
      }}
    }}
    NO MARKDOWN. VALID JSON ONLY.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        
        # Robust JSON cleaning
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        plan = json.loads(content)
        return plan
    except Exception as e:
        print(f"Error in Thinking Phase: {e}")
        # Default strategy if AI fails
        num_cols = df.select_dtypes(include='number').columns.tolist()
        return {
            "domain": "General Data",
            "thinking": "Automated fallback strategy initiated due to AI timeout.",
            "clustering": {"recommended_features": num_cols[:2], "suggested_k": 3},
            "anomaly": {"contamination": 0.05, "features": num_cols},
            "automl": {"target_col": num_cols[-1] if num_cols else "target", "task_type": "auto"}
        }
