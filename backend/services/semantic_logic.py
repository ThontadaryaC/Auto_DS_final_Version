import pandas as pd
import json
from agent.llm_config import get_llm
from langchain_core.messages import HumanMessage

def profile_dataset_with_ai(df: pd.DataFrame, filename: str) -> dict:
    """
    Uses Gemini to analyze the dataset structure and provide semantic insights.
    Returns a dictionary mapping columns to high-level types and suggesting interesting plots.
    """
    llm = get_llm()
    
    # 1. Prepare Metadata for the LLM
    num_rows = len(df)
    sample_data = df.head(5).to_dict(orient='records')
    cols_info = {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    prompt = f"""
    You are a Master Data Science Profiler.
    Dataset Name: {filename}
    Total Rows: {num_rows}
    Schema (raw dtypes): {json.dumps(cols_info)}
    Sample Data: {json.dumps(sample_data)}
    
    TASK: Analyze this dataset in two phases:
    1. RECOGNITION PHASE: Look at the Dataset Name "{filename}". Based JUST on this name, what industry, domain, or use case does this likely belong to?
    2. ANALYSIS PHASE: Examine the Schema and Sample Data. Confirm if they match your recognition of the name. If they differ, explain why.
    
    Identify columns with these semantic types:
    - Date: Datetime, Years, Timestamps.
    - Age: Age of people or items.
    - Currency: Money, Prices, Revenue.
    - Geographic: Cities, Countries, Zip Codes, Coordinates.
    - ID: Primary keys, UUIDs, unique identifiers.
    - Category: Low-cardinality strings.
    - Numeric: Generic numbers.
    - Text: Long descriptions or names.
    
    Return EXACTLY this JSON structure:
    {{
      "filename_assessment": "How you recognized the dataset based on its name.",
      "domain": "Likely domain (e.g. Finance, Healthcare, E-commerce)",
      "summary": "A 1-sentence human-like description of what this data represents.",
      "columns": [
        {{
          "name": "column_name",
          "semantic_type": "Date/Age/Currency/Geographic/ID/Category/Numeric/Text",
          "description": "Short explanation of what this column holds"
        }}
      ],
      "recommended_plots": [
        {{
          "type": "scatter/bar/line/pie/histogram",
          "x": "col1",
          "y": "col2",
          "reason": "Why this plot is insightful"
        }}
      ]
    }}
    NO MARKDOWN. VALID JSON ONLY.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        
        # Cleaning JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        profile = json.loads(content)
        return profile
    except Exception as e:
        print(f"Error profiling dataset: {e}")
        # Default fallback profile
        return {
            "domain": "General Data",
            "summary": "A standard dataset for analysis.",
            "columns": [{"name": col, "semantic_type": "Numeric" if pd.api.types.is_numeric_dtype(df[col]) else "Category", "description": col} for col in df.columns],
            "recommended_plots": []
        }
