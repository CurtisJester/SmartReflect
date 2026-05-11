from typing import Annotated
from fastapi import Query, APIRouter, Depends
from src.backend.db.db import get_db
from pydantic import BaseModel, Field


router = APIRouter(prefix="/sleep", tags=["sleep"])


class SleepFilter(BaseModel):
    min_sleep: Annotated[int, Query(ge=0, le=24)] = Field(default=4, description="Minimum sleep duration")
    max_sleep: Annotated[int, Query(ge=0, le=24)] = Field(default=8, description="Maximum sleep duration")


@router.get("/between")
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
    cursor.execute(
        "SELECT * FROM smartphone_usage WHERE sleep_hours BETWEEN ? AND ?",
        (filter_query.min_sleep, filter_query.max_sleep),
    )
    return cursor.fetchall()


@router.get("/{sleep_hours}")
def get_sleep(sleep_hours: int, conn = Depends(get_db)):
    """
    Get the smartphone usage data for users with the specified sleep hours.

    Args:
        sleep_hours: Sleep hours of the user

    Returns:
        List of smartphone usage records for users with the specified sleep hours
    """
    return get_sleep_between(SleepFilter(min_sleep=sleep_hours, max_sleep=sleep_hours + 1), conn)