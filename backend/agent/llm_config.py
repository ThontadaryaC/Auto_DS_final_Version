import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    """Initializes and returns the LangChain LLM instance configured for Google Gemini API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Instead of raising ValueError here which crashes bootstrap, 
        # we can raise a clear exception that routers can catch
        raise KeyError("GEMINI_API_KEY_MISSING")
        
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.1,
            max_output_tokens=2048,
        )
        return llm
    except Exception as e:
        print(f"Failed to initialize Gemini LLM: {e}")
        raise ConnectionError("GEMINI_INITIALIZATION_FAILED")
