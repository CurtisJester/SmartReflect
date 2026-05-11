from typing import Annotated
from fastapi import Query, APIRouter, Depends
from src.backend.db.db import get_db
from pydantic import BaseModel, Field


router = APIRouter()


class SleepFilter(BaseModel):
    min_sleep: Annotated[int, Query(ge=0, le=24)] = Field(default=4, description="Minimum sleep duration")
    max_sleep: Annotated[int, Query(ge=0, le=24)] = Field(default=8, description="Maximum sleep duration")


class StatisticsResponse(BaseModel):
    """
    Response model for statistics endpoints that return single float values.
    """
    statistic_name: str
    statistic_value: float


class StatisticsListResponse(BaseModel):
    """
    Response model for statistics endpoints that return a list of float values.
    """
    statistic_name: str
    statistic_values: list[float]


@router.get("/sleep_between")
def get_sleep_between(filter_query: Annotated[SleepFilter, Query()], conn = Depends(get_db)):
    """
    Get the smartphone usage data for users within the specified sleep range.
    
    Args:
        min_sleep: Minimum sleep duration (inclusive)
        max_sleep: Maximum sleep duration (inclusive)
        
    Returns:
        List of smartphone usage records for users within the specified sleep range
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM smartphone_usage WHERE sleep_hours BETWEEN ? AND ?", (filter_query.min_sleep, filter_query.max_sleep))
    return cursor.fetchall()


@router.get("/sleep/{sleep_hours}")
def get_sleep(sleep_hours: int, conn = Depends(get_db)):
    """
    Get the smartphone usage data for users with the specified sleep hours.
    
    Args:
        sleep_hours: Sleep hours of the user
        
    Returns:
        List of smartphone usage records for users with the specified sleep hours
    """
    return get_sleep_between(SleepFilter(min_sleep=sleep_hours, max_sleep=sleep_hours+1), conn)


@router.get("/sleep_average", response_model=StatisticsResponse)
def get_sleep_average(conn = Depends(get_db)):
    """
    Get the average sleep hours of all users.
    
    Returns:
        Dictionary containing the average sleep hours of all users
    """
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(sleep_hours) FROM smartphone_usage")
    return StatisticsResponse(statistic_name="average_sleep_hours", statistic_value=cursor.fetchone()[0])


@router.get("/sleep_max_three", response_model=StatisticsListResponse)
def get_sleep_max_three(conn = Depends(get_db)):
    """
    Get the max three values for the sleep_hours column.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT sleep_hours FROM smartphone_usage ORDER BY sleep_hours DESC LIMIT 3")
    return StatisticsListResponse(statistic_name="sleep_hours", statistic_values=[row[0] for row in cursor.fetchall()])


@router.get("/sleep_min_three", response_model=StatisticsListResponse)
def get_sleep_min_three(conn = Depends(get_db)):
    """
    Get the min three values for the sleep_hours column.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT sleep_hours FROM smartphone_usage ORDER BY sleep_hours ASC LIMIT 3")
    return StatisticsListResponse(statistic_name="sleep_hours", statistic_values=[row[0] for row in cursor.fetchall()])