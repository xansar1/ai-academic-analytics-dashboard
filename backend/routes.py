from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "running"}


@router.get("/subscription/plans")
def plans():
    return {
        "starter": "₹4999/month",
        "pro": "₹14999/month",
        "enterprise": "custom pricing"
    }


@router.get("/analytics/kpis")
def get_kpis():
    return {
        "total_students": 1200,
        "avg_score": 78.5,
        "top_score": 99,
        "at_risk": 86
    }

@router.get("/students")
def get_students():
    import pandas as pd
    import os

    file_path = os.path.join("data", "students.csv")

    if not os.path.exists(file_path):
        return []

    df = pd.read_csv(file_path)

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
        df["RISK_LABEL"] = df["AI_DROPOUT_RISK"].apply(get_risk)
    else:
        df["RISK_LABEL"] = "Low"

    students = df[["STUDENT_NAME", "TOTAL_SCORE", "RISK_LABEL"]].rename(columns={
        "STUDENT_NAME": "name",
        "TOTAL_SCORE": "score",
        "RISK_LABEL": "risk"
    })

    return students.to_dict(orient="records")
