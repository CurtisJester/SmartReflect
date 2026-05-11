from typing import Annotated
from fastapi import Query, APIRouter, Depends
from src.backend.db.db import get_db
from pydantic import BaseModel, Field


router = APIRouter()

class AgeFilter(BaseModel):
    min_age: Annotated[int, Query(ge=0, le=120)] = Field(default=0, description="Minimum age")
    max_age: Annotated[int, Query(ge=0, le=120)] = Field(default=120, description="Maximum age")

@router.get("/age_between")
def get_age_between(filter_query: Annotated[AgeFilter, Query()], conn = Depends(get_db)):
    """
    Get the smartphone usage data for users within the specified age range.
    
    Args:
        min_age: Minimum age (inclusive)
        max_age: Maximum age (inclusive)
        
    Returns:
        List of smartphone usage records for users within the specified age range
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM smartphone_usage WHERE age BETWEEN ? AND ?", (filter_query.min_age, filter_query.max_age))
    return cursor.fetchall()

@router.get("/age/{age}")
def get_age(age: int, conn = Depends(get_db)):
    """
    Get the smartphone usage data for users with the specified age.
    
    Args:
        age: Age of the user
        
    Returns:
        List of smartphone usage records for users with the specified age
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM smartphone_usage WHERE age = ?", (age,))
    return cursor.fetchall()