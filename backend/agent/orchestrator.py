import pandas as pd
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from agent.llm_config import get_llm
import io

def query_agent(df: pd.DataFrame, query: str) -> str:
    """Uses Langchain to answer user query over the given dataframe."""
    llm = get_llm()
    # The experimental Pandas agent creates python code to answer the query
    try:
        agent_executor = create_pandas_dataframe_agent(
            llm, 
            df,
            verbose=False,
            agent_type="tool-calling",
            allow_dangerous_code=True,
            prefix="You are a world-class Senior Data Scientist. Answer questions about the provided dataframe with precision. If you use code to find an answer, summarize the findings professionally. "
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
