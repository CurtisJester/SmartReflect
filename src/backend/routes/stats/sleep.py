from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.backend.db.db import get_db


router = APIRouter(prefix="/sleep", tags=["stats:sleep"])


class StatisticsResponse(BaseModel):
    """
    Response model for statistics endpoints that return a single float value.
    """
    statistic_name: str
    statistic_value: float


class StatisticsListResponse(BaseModel):
    """
    Response model for statistics endpoints that return a list of float values.
    """
    statistic_name: str
    statistic_values: list[float]


@router.get("/average", response_model=StatisticsResponse)
def get_sleep_average(conn = Depends(get_db)):
    """
    Get the average sleep hours of all users.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(sleep_hours) AS avg_sleep FROM smartphone_usage")
    return StatisticsResponse(
        statistic_name="average_sleep_hours",
        statistic_value=cursor.fetchone()["avg_sleep"],
    )


@router.get("/max_three", response_model=StatisticsListResponse)
def get_sleep_max_three(conn = Depends(get_db)):
    """
    Get the three highest sleep_hours values.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT sleep_hours FROM smartphone_usage ORDER BY sleep_hours DESC LIMIT 3")
    return StatisticsListResponse(
        statistic_name="sleep_hours",
        statistic_values=[row["sleep_hours"] for row in cursor.fetchall()],
    )


@router.get("/min_three", response_model=StatisticsListResponse)
def get_sleep_min_three(conn = Depends(get_db)):
    """
    Get the three lowest sleep_hours values.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT sleep_hours FROM smartphone_usage ORDER BY sleep_hours ASC LIMIT 3")
    return StatisticsListResponse(
        statistic_name="sleep_hours",
        statistic_values=[row["sleep_hours"] for row in cursor.fetchall()],
    )
