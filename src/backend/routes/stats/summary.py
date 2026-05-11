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


class MostAddictedBreakdownItem(BaseModel):
    label: str
    count: int
    pct_of_cohort: float


class MostAddictedResponse(BaseModel):
    total_users: int
    cohort_users: int
    cohort_percentile: int
    screen_time_threshold_hours: float
    avg_screen_time_hours: float
    min_screen_time_hours: float
    max_screen_time_hours: float
    avg_sleep_hours: float
    avg_notifications_per_day: float
    pct_addicted: float
    addiction_breakdown: list[MostAddictedBreakdownItem]
    age_breakdown: list[MostAddictedBreakdownItem]


def _get_screen_time_cohort(conn, order_direction: str, comparison_operator: str, percentile: int):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS c FROM smartphone_usage")
    total_users = int(cursor.fetchone()["c"] or 0)
    cohort_limit = max(1, int(total_users * 0.1))

    cursor.execute(
        f"""
        SELECT {"MIN" if comparison_operator == ">=" else "MAX"}(daily_screen_time_hours) AS threshold
        FROM (
            SELECT daily_screen_time_hours
            FROM smartphone_usage
            WHERE daily_screen_time_hours IS NOT NULL
            ORDER BY daily_screen_time_hours {order_direction}
            LIMIT ?
        )
        """,
        (cohort_limit,),
    )
    threshold = float(cursor.fetchone()["threshold"] or 0.0)

    cursor.execute(
        f"""
        SELECT
            COUNT(*) AS cohort_users,
            AVG(daily_screen_time_hours) AS avg_screen_time_hours,
            MIN(daily_screen_time_hours) AS min_screen_time_hours,
            MAX(daily_screen_time_hours) AS max_screen_time_hours,
            AVG(sleep_hours) AS avg_sleep_hours,
            AVG(notifications_per_day) AS avg_notifications_per_day,
            AVG(addicted_label) * 100.0 AS pct_addicted
        FROM smartphone_usage
        WHERE daily_screen_time_hours {comparison_operator} ?
        """,
        (threshold,),
    )
    row = cursor.fetchone()
    cohort_users = int(row["cohort_users"] or 0)

    cursor.execute(
        f"""
        SELECT addiction_level AS label, COUNT(*) AS c
        FROM smartphone_usage
        WHERE daily_screen_time_hours {comparison_operator} ?
          AND addiction_level IS NOT NULL
          AND LOWER(TRIM(addiction_level)) != 'none'
        GROUP BY addiction_level
        ORDER BY c DESC
        """,
        (threshold,),
    )
    addiction_breakdown = [
        MostAddictedBreakdownItem(
            label=str(item["label"]),
            count=int(item["c"]),
            pct_of_cohort=(int(item["c"]) / cohort_users * 100.0) if cohort_users else 0.0,
        )
        for item in cursor.fetchall()
    ]

    cursor.execute(
        f"""
        SELECT
            CASE
                WHEN age BETWEEN 0 AND 19 THEN '0-19'
                ELSE CAST((age / 10) * 10 AS INT) || '-' || CAST(((age / 10) * 10 + 9) AS INT)
            END AS label,
            CASE
                WHEN age BETWEEN 0 AND 19 THEN 0
                ELSE CAST(age / 10 AS INT)
            END AS sort_key,
            COUNT(*) AS c
        FROM smartphone_usage
        WHERE daily_screen_time_hours {comparison_operator} ? AND age IS NOT NULL
        GROUP BY label, sort_key
        ORDER BY sort_key
        """,
        (threshold,),
    )
    age_breakdown = [
        MostAddictedBreakdownItem(
            label=str(item["label"]),
            count=int(item["c"]),
            pct_of_cohort=(int(item["c"]) / cohort_users * 100.0) if cohort_users else 0.0,
        )
        for item in cursor.fetchall()
    ]

    return MostAddictedResponse(
        total_users=total_users,
        cohort_users=cohort_users,
        cohort_percentile=percentile,
        screen_time_threshold_hours=threshold,
        avg_screen_time_hours=float(row["avg_screen_time_hours"] or 0.0),
        min_screen_time_hours=float(row["min_screen_time_hours"] or 0.0),
        max_screen_time_hours=float(row["max_screen_time_hours"] or 0.0),
        avg_sleep_hours=float(row["avg_sleep_hours"] or 0.0),
        avg_notifications_per_day=float(row["avg_notifications_per_day"] or 0.0),
        pct_addicted=float(row["pct_addicted"] or 0.0),
        addiction_breakdown=addiction_breakdown,
        age_breakdown=age_breakdown,
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


@router.get("/most_addicted", response_model=MostAddictedResponse)
def get_most_addicted(conn = Depends(get_db)):
    return _get_screen_time_cohort(conn, "DESC", ">=", 90)


@router.get("/least_addicted", response_model=MostAddictedResponse)
def get_least_addicted(conn = Depends(get_db)):
    return _get_screen_time_cohort(conn, "ASC", "<=", 10)
