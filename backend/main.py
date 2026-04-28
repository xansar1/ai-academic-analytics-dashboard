from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import router

app = FastAPI(
    title="AI Coaching SaaS API",
    version="1.0.0",
    description="AI-powered student analytics backend"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(router, prefix="/api")

# Root
@app.get("/")
def home():
    return {
        "status": "running",
        "message": "AI Coaching SaaS API 🚀"
    }
