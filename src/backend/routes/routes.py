from fastapi import APIRouter, Depends, Query
from src.backend.db.db import get_db


router = APIRouter()


_EXPLORE_COLUMNS = [
    "transaction_id",
    "user_id",
    "age",
    "gender",
    "daily_screen_time_hours",
    "social_media_hours",
    "gaming_hours",
    "work_study_hours",
    "sleep_hours",
    "notifications_per_day",
    "app_opens_per_day",
    "weekend_screen_time",
    "stress_level",
    "academic_work_impact",
    "addiction_level",
    "addicted_label",
]


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


def _build_explore_query(
    gender, stress_level, academic_work_impact, addiction_level, addicted_label, sort_by, sort_dir
):
    filters = []
    values = []
    for column, value in [
        ("gender", gender),
        ("stress_level", stress_level),
        ("academic_work_impact", academic_work_impact),
        ("addiction_level", addiction_level),
        ("addicted_label", addicted_label),
    ]:
        if value is not None and value != "":
            filters.append(f"{column} = ?")
            values.append(value)
    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    order_col = sort_by if sort_by in _EXPLORE_COLUMNS else "transaction_id"
    order_dir = "DESC" if sort_dir == "desc" else "ASC"
    return where_clause, values, order_col, order_dir


@router.get("/explore/export")
async def explore_export(
    gender: str | None = None,
    stress_level: str | None = None,
    academic_work_impact: str | None = None,
    addiction_level: str | None = None,
    addicted_label: int | None = Query(default=None, ge=0, le=1),
    sort_by: str | None = None,
    sort_dir: str | None = None,
    conn = Depends(get_db),
):
    where_clause, values, order_col, order_dir = _build_explore_query(
        gender, stress_level, academic_work_impact, addiction_level, addicted_label, sort_by, sort_dir
    )
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT * FROM smartphone_usage {where_clause} ORDER BY {order_col} {order_dir}",
        values,
    )
    return {"rows": [dict(row) for row in cursor.fetchall()]}


@router.get("/explore")
async def explore(
    gender: str | None = None,
    stress_level: str | None = None,
    academic_work_impact: str | None = None,
    addiction_level: str | None = None,
    addicted_label: int | None = Query(default=None, ge=0, le=1),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    sort_by: str | None = None,
    sort_dir: str | None = None,
    conn = Depends(get_db),
):
    where_clause, values, order_col, order_dir = _build_explore_query(
        gender, stress_level, academic_work_impact, addiction_level, addicted_label, sort_by, sort_dir
    )
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT * FROM smartphone_usage {where_clause} ORDER BY {order_col} {order_dir} LIMIT ? OFFSET ?",
        (*values, limit, offset),
    )
    rows = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"SELECT COUNT(*) AS c FROM smartphone_usage {where_clause}", values)
    total = int(cursor.fetchone()["c"] or 0)

    return {
        "columns": _EXPLORE_COLUMNS,
        "rows": rows,
        "total": total,
        "limit": limit,
    }
