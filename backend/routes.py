from fastapi import APIRouter, UploadFile, File
import pandas as pd
import os

router = APIRouter()

DATA_PATH = os.path.join("data", "students.csv")


# =========================
# HELPER: SAFE SCORE CALCULATION
# =========================
def calculate_total_score(df):
    # ✅ Only numeric columns
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    # ❌ Remove unwanted columns
    exclude_cols = [
        "PARENT_PHONE",
        "PHONE",
        "MOBILE",
        "CONTACT",
        "ADMISSION_NO"
    ]

    score_cols = [col for col in numeric_cols if col not in exclude_cols]

    if not score_cols:
        df["TOTAL_SCORE"] = 0
    else:
        df["TOTAL_SCORE"] = df[score_cols].sum(axis=1)

    return df


# =========================
# HEALTH
# =========================
@router.get("/health")
def health():
    return {"status": "ok"}


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
# KPI
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
    df = calculate_total_score(df)

    total_students = len(df)
    avg_score = round(df["TOTAL_SCORE"].mean(), 2)
    top_score = round(df["TOTAL_SCORE"].max(), 2)

    if "AI_DROPOUT_RISK" in df.columns:
        at_risk = len(df[df["AI_DROPOUT_RISK"] >= 0.7])
    else:
        at_risk = 0

    return {
        "total_students": total_students,
        "avg_score": avg_score,
        "top_score": top_score,
        "at_risk": at_risk
    }


# =========================
# STUDENTS
# =========================
@router.get("/students")
def get_students():
    if not os.path.exists(DATA_PATH):
        return []

    df = pd.read_csv(DATA_PATH)
    df = calculate_total_score(df)

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

    # ✅ Safe fallback if column missing
    if "STUDENT_NAME" not in df.columns:
        df["STUDENT_NAME"] = "Student"

    students = df[["STUDENT_NAME", "TOTAL_SCORE", "risk"]].rename(columns={
        "STUDENT_NAME": "name",
        "TOTAL_SCORE": "score"
    })

    return students.to_dict(orient="records")
