from fastapi import APIRouter, UploadFile, File
import pandas as pd
import os

router = APIRouter()

DATA_PATH = os.path.join("data", "students.csv")


# =========================
# HELPER: SAFE SCORE CALCULATION
# =========================
def calculate_total_score(df):
    try:
        score_cols = [
            col for col in df.columns
            if any(x in col.upper() for x in ["MARK", "TEST"])
        ]

        if not score_cols:
            df["TOTAL_SCORE"] = 0
            return df

        # 🔥 convert safely to numeric
        for col in score_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df["TOTAL_SCORE"] = df[score_cols].sum(axis=1, skipna=True)

        return df

    except Exception as e:
        print("ERROR IN SCORE CALC:", e)
        df["TOTAL_SCORE"] = 0
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
    try:
        if not os.path.exists(DATA_PATH):
            return {
                "total_students": 0,
                "avg_score": 0,
                "top_score": 0,
                "at_risk": 0
            }

        # 🔥 safer read
        df = pd.read_csv(DATA_PATH, dtype=str)

        if df.empty:
            return {
                "total_students": 0,
                "avg_score": 0,
                "top_score": 0,
                "at_risk": 0
            }

        # 🔥 convert all numeric-like values
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        df = calculate_total_score(df)

        # 🔥 ensure numeric safety
        df["TOTAL_SCORE"] = pd.to_numeric(
            df["TOTAL_SCORE"], errors="coerce"
        ).fillna(0)

        total_students = int(len(df))
        avg_score = float(df["TOTAL_SCORE"].mean() or 0)
        top_score = float(df["TOTAL_SCORE"].max() or 0)

        return {
            "total_students": total_students,
            "avg_score": round(avg_score, 2),
            "top_score": round(top_score, 2),
            "at_risk": 0
        }

    except Exception as e:
        print("🔥 KPI ERROR:", e)
        return {
            "total_students": 0,
            "avg_score": 0,
            "top_score": 0,
            "at_risk": 0,
            "error": str(e)
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
