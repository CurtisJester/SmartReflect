from fastapi import APIRouter, Depends
from src.backend.db.db import get_db


router = APIRouter()


@router.get("/")
async def root():
    """
    Root endpoint for the API.
    
    Returns:
        A simple greeting message
    """
    return {"message": "Hello World"}


@router.get("/get_random")
async def get_random(conn = Depends(get_db)):
    """
    Get a random record from the smartphone_usage table.
    
    Returns:
        A random record from the smartphone_usage table
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM smartphone_usage ORDER BY RANDOM() LIMIT 1")
    user = cursor.fetchone()
    return user


@router.get("/get_one")
async def get_one(conn = Depends(get_db)):
    """
    Get one record from the smartphone_usage table.
    
    Returns:
        A single record from the smartphone_usage table
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM smartphone_usage LIMIT 1")
    user = cursor.fetchone()
    return user


@router.get("/get_100")
async def get_100(conn = Depends(get_db)):
    """
    Get 100 records from the smartphone_usage table.
    
    Returns:
        100 records from the smartphone_usage table
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM smartphone_usage LIMIT 100")
    users = cursor.fetchall()
    return users
