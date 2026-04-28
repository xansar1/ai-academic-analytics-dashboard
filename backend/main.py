from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ✅ IMPORTANT: correct import (based on your structure)
from backend.routes import router

app = FastAPI(
    title="AI Coaching SaaS API",
    version="1.0.0",
    description="AI-powered student analytics backend"
)

# =========================
# CORS (Frontend connect)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ production il restrict cheyyanam
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ROUTES
# =========================
app.include_router(router, prefix="/api")


# =========================
# ROOT
# =========================
@app.get("/")
def home():
    return {
        "status": "running",
        "message": "AI Coaching SaaS API 🚀"
    }


# =========================
# HEALTH CHECK
# =========================
@app.get("/health")
def health():
    return {"status": "ok"}
