import pandas as pd
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from agent.llm_config import get_llm
import io

def query_agent(df: pd.DataFrame, query: str, filename: str = "Unknown", semantic_profile: dict = None) -> str:
    """Uses Langchain to answer user query over the given dataframe with semantic awareness."""
    llm = get_llm()
    
    # Prepare semantic context for the agent
    profile_summary = ""
    if semantic_profile:
        profile_summary = f"Dataset Name: {filename}. Domain: {semantic_profile.get('domain', 'Unknown')}. Description: {semantic_profile.get('summary', '')}"
    
    try:
        agent_executor = create_pandas_dataframe_agent(
            llm, 
            df,
            verbose=False,
            agent_type="tool-calling",
            allow_dangerous_code=True,
            prefix=f"You are a world-class Senior Data Scientist. {profile_summary}. Answer questions about this dataset with precision. Always prioritize detected semantic types like 'Date' or 'Currency' if the user asks about trends or money. "
        )
        
        response = agent_executor.invoke({"input": query})
        output = response.get("output", "I could not formulate an answer.")
        if isinstance(output, list):
            text_parts = []
            for item in output:
                if isinstance(item, dict) and "text" in item:
                    text_parts.append(item["text"])
                elif isinstance(item, str):
                    text_parts.append(item)
            output = "".join(text_parts)
        return str(output)
    except Exception as e:
        print(f"Error evaluating agent: {e}")
        return f"AI Agent Error: {str(e)}"
