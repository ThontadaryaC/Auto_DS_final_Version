import pandas as pd
import json
from agent.llm_config import get_llm
from langchain_core.messages import HumanMessage

def generate_strategic_plan(df: pd.DataFrame, filename: str = "Unknown", semantic_profile: dict = None) -> dict:
    """
    Uses LLM to analyze dataset and decide the best ML strategy with semantic awareness.
    Returns instructions for Clustering, Anomaly Detection, or AutoML.
    """
    llm = get_llm()
    
    # 1. Prepare Enriched Metadata for the LLM
    num_rows = len(df)
    sample_data_json = df.head(3).to_json(orient='records', date_format='iso')
    
    # Create a consolidated view of columns: Name (Dtype) -> Semantic Type
    semantic_map = {col["name"]: col["semantic_type"] for col in semantic_profile.get("columns", [])} if semantic_profile else {}
    enriched_schema = json.dumps({col: f"{str(dtype)} [{semantic_map.get(col, 'Unknown')}]" for col, dtype in df.dtypes.items()}, separators=(',', ':'))
    
    prompt = f"""
    You are a Strategic AI Data Scientist.
    Dataset: {filename} ({num_rows} rows)
    Domain: {semantic_profile.get('domain', 'Unknown') if semantic_profile else "N/A"}
    
    SCHEMA: {enriched_schema}
    SAMPLE: {sample_data_json}
    
    TASK: Analyze the dataset structure and domain. Decide on a 3-part strategic ML plan.
    
    CRITICAL RULES:
    1. EXCLUSION: Never use columns marked as 'ID', 'Text', 'Email', 'URL', 'Phone', or 'Geographic' (Address) as features for Clustering or Anomaly detection.
    2. TIME-SERIES: If a 'Date' semantic type is present, and you pick a 'Numeric' or 'Currency' target, prioritize 'timeseries' as the AutoML task_type.
    3. TARGET SELECTION: Pick the most business-critical column as the AutoML target (e.g., Sales, Price, Churn, Status).
    
    STRATEGY OPTIONS:
    1. CLUSTERING: Recommended features (Exclude IDs/Text). Suggested K.
    2. ANOMALY: Detect outliers. Recommendation: Contamination rate (0.01 to 0.1)?
    3. AUTOML: Target selection and task type (regression/classification/timeseries).
    
    Return EXACTLY this JSON structure:
    {{
      "domain": "Detailed business domain name",
      "thinking": "Professional reasoning (2 sentences max) explaining how semantic types influenced your choice of target and features.",
      "clustering": {{
        "recommended_features": ["col1", "col2"],
        "suggested_k": 3
      }},
      "anomaly": {{
        "contamination": 0.05,
        "features": ["col1", "col2"]
      }},
      "automl": {{
        "target_col": "column_to_predict",
        "task_type": "regression/classification/timeseries"
      }},
      "strategy_viz": {{
        "type": "radar/bar/scatter",
        "data_focus": "e.g. Volume vs Complexity",
        "reason": "Why this visualization matters for strategy"
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
            "automl": {"target_col": num_cols[-1] if num_cols else "target", "task_type": "auto"},
            "strategy_viz": {"type": "bar", "data_focus": "Dataset Cardinality", "reason": "Fallback visualization"}
        }
