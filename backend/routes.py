from fastapi import APIRouter, UploadFile, File
import pandas as pd
import os

router = APIRouter()

DATA_PATH = os.path.join("data", "students.csv")


# =========================
# HEALTH CHECK
# =========================
@router.get("/health")
def health():
    return {"status": "running"}


# =========================
# PRICING
# =========================
@router.get("/subscription/plans")
def plans():
    return {
        "starter": "₹4999/month",
        "pro": "₹14999/month",
        "enterprise": "custom pricing"
    }


# =========================
# CSV UPLOAD
# =========================
@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)

        os.makedirs("data", exist_ok=True)
        df.to_csv(DATA_PATH, index=False)

        return {
            "status": "success",
            "message": "CSV uploaded successfully"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# =========================
# STUDENTS DATA
# =========================
@router.get("/students")
def get_students():
    if not os.path.exists(DATA_PATH):
        return []

    df = pd.read_csv(DATA_PATH)

    # Ensure TOTAL_SCORE exists
    if "TOTAL_SCORE" not in df.columns:
        numeric_cols = df.select_dtypes(include="number").columns
        df["TOTAL_SCORE"] = df[numeric_cols].sum(axis=1)

    # Risk conversion
    def get_risk(val):
        if val >= 0.7:
            return "High"
        elif val >= 0.4:
            return "Medium"
        return "Low"

    if "AI_DROPOUT_RISK" in df.columns:
        df["risk"] = df["AI_DROPOUT_RISK"].apply(get_risk)
    else:
        df["risk"] = "Low"

    students = df[["STUDENT_NAME", "TOTAL_SCORE", "risk"]].rename(columns={
        "STUDENT_NAME": "name",
        "TOTAL_SCORE": "score"
    })

    return students.to_dict(orient="records")


# =========================
# KPI (REAL DATA)
# =========================
@router.get("/analytics/kpis")
def get_kpis():
    if not os.path.exists(DATA_PATH):
        return {
            "total_students": 0,
            "avg_score": 0,
            "top_score": 0,
            "at_risk": 0
        }

    df = pd.read_csv(DATA_PATH)

    # Ensure TOTAL_SCORE exists
    if "TOTAL_SCORE" not in df.columns:
        numeric_cols = df.select_dtypes(include="number").columns
        df["TOTAL_SCORE"] = df[numeric_cols].sum(axis=1)

    total_students = len(df)
    avg_score = round(df["TOTAL_SCORE"].mean(), 2)
    top_score = round(df["TOTAL_SCORE"].max(), 2)

    if "AI_DROPOUT_RISK" in df.columns:
        at_risk = len(df[df["AI_DROPOUT_RISK"] > 0.7])
    else:
        at_risk = 0

    return {
        "total_students": total_students,
        "avg_score": avg_score,
        "top_score": top_score,
        "at_risk": at_risk
    }
