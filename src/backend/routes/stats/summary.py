from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from src.backend.db.db import get_db


router = APIRouter()


class SummaryResponse(BaseModel):
    total_users: int = Field(description="Total number of users in the dataset")
    avg_screen_time_hours: float = Field(description="Average daily screen time in hours")
    avg_sleep_hours: float = Field(description="Average sleep hours")
    pct_addicted: float = Field(description="Percentage of users labeled as addicted (0-100)")
    coverage_pct: float = Field(
        description=(
            "Percentage of users with a non-None addiction_level designation "
            "(Mild + Moderate + Severe) / total_users * 100"
        )
    )
    addicted_designation: list[str] = Field(
        description="addiction_level values that classify a user as addicted"
    )


@router.get("/summary", response_model=SummaryResponse)
def get_summary(conn = Depends(get_db)):
    """
    Return headline KPI numbers for the dashboard in one call.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            COUNT(*) AS total_users,
            AVG(daily_screen_time_hours) AS avg_screen_time_hours,
            AVG(sleep_hours) AS avg_sleep_hours,
            AVG(addicted_label) * 100.0 AS pct_addicted,
            SUM(CASE
                    WHEN LOWER(TRIM(addiction_level)) IN ('mild', 'moderate', 'severe')
                    THEN 1 ELSE 0
                END) * 100.0 / NULLIF(COUNT(*), 0) AS coverage_pct
        FROM smartphone_usage
        """
    )
    row = cursor.fetchone()
    return SummaryResponse(
        total_users=row["total_users"] or 0,
        avg_screen_time_hours=float(row["avg_screen_time_hours"] or 0.0),
        avg_sleep_hours=float(row["avg_sleep_hours"] or 0.0),
        pct_addicted=float(row["pct_addicted"] or 0.0),
        coverage_pct=float(row["coverage_pct"] or 0.0),
        addicted_designation=["Moderate", "Severe"],
    )
