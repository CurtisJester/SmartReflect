from typing import Annotated
from fastapi import Query, APIRouter, Depends
from src.backend.db.db import get_db
from pydantic import BaseModel, Field


router = APIRouter(prefix="/notifications", tags=["notifications"])

class NotificationsFilter(BaseModel):
    min_notifications: Annotated[int, Query(ge=0, le=10000)] = Field(default=0, description="Minimum number of notifications")
    max_notifications: Annotated[int, Query(ge=0, le=10000)] = Field(default=10000, description="Maximum number of notifications")

@router.get("/between")
def get_notifications_between(filter_query: Annotated[NotificationsFilter, Query()], conn = Depends(get_db)):
    """
    Get the smartphone usage data for users within the specified notification range.
    
    Args:
        min_notifications: Minimum number of notifications (inclusive)
        max_notifications: Maximum number of notifications (inclusive)
        
    Returns:
        List of smartphone usage records for users within the specified notification range
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM smartphone_usage WHERE notifications_per_day BETWEEN ? AND ?", (filter_query.min_notifications, filter_query.max_notifications))
    return cursor.fetchall()