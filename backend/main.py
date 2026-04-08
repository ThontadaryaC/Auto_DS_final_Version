from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload, data, chat
from dotenv import load_dotenv

# Load env variables (like OPENROUTER_API_KEY)
load_dotenv()

app = FastAPI(title="AutoDS AI", description="AI-powered Data Scientist Backend")

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(data.router, prefix="/api", tags=["Data & Visuals"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])

@app.get("/")
def root():
    return {"message": "Welcome to AutoDS AI API"}
