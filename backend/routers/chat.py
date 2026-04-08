from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.store import store
from agent.orchestrator import query_agent

router = APIRouter()

class ChatRequest(BaseModel):
    query: str

@router.post("/chat")
async def chat_with_agent(request: ChatRequest):
    df = store.get_data()
    if df is None:
        return {"response": "Please upload a dataset first."}
        
    try:
        response = query_agent(df, request.query)
        return {"response": response}
    except Exception as e:
        return {"response": f"Error communicating with AI agent: {str(e)}"}
