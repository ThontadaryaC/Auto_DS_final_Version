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
    # Use to_json with head(3) and compact formatting to save tokens
    sample_data_json = df.head(3).to_json(orient='records', date_format='iso')
    cols_info = json.dumps({col: str(dtype) for col, dtype in df.dtypes.items()}, separators=(',', ':'))
    
    prompt = f"""
    You are a Master Data Science Profiler.
    Dataset Name: {filename}
    Total Rows: {num_rows}
    Schema: {cols_info}
    Sample Data: {sample_data_json}
    
    TASK: Analyze this dataset in two phases:
    1. RECOGNITION PHASE: Look at the Dataset Name "{filename}". Based JUST on this name, what industry, domain, or use case does this likely belong to?
    2. ANALYSIS PHASE: Examine the Schema and Sample Data. Confirm if they match your recognition of the name. If they differ, explain why.
    
    Identify columns with these specific semantic types:
    - Date: Datetime, Years, Timestamps, Birthdays.
    - Age: Age of people, animals, or items.
    - Currency: Money, Prices, Revenue, Costs, Salaries.
    - Geographic: Cities, Countries, Zip Codes, Coordinates, Addresses.
    - ID: Primary keys, UUIDs, unique identifiers, serial numbers (Crucial: usually non-numeric or sequential integers that shouldn't be averaged).
    - Email: Electronic mail addresses.
    - URL: Website links or social media profiles.
    - Phone: Telephone numbers.
    - Status: State variables like 'Active', 'Pending', 'Success', 'Failure'.
    - Category: Low-cardinality strings or categorical labels.
    - Numeric: Generic measurement numbers, counts, or scores.
    - Text: Long descriptions, comments, or unstructured prose.
    
    Return EXACTLY this JSON structure:
    {{
      "filename_assessment": "How you recognized the dataset based on its name.",
      "domain": "Likely domain (e.g. Finance, Healthcare, E-commerce, Logistics)",
      "summary": "A 1-sentence human-like description of what this data represents.",
      "columns": [
        {{
          "name": "column_name",
          "semantic_type": "Date/Age/Currency/Geographic/ID/Email/URL/Phone/Status/Category/Numeric/Text",
          "description": "Short explanation of what this column holds and why it belongs to this type"
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
