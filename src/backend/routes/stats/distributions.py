from typing import Annotated
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from src.backend.db.db import get_db


router = APIRouter()


class HistogramBin(BaseModel):
    bin_start: float
    bin_end: float
    count: int
    age_counts: dict[str, int]


class HistogramResponse(BaseModel):
    column: str
    age_ranges: list[str]
    bins: list[HistogramBin]


class ScatterPoint(BaseModel):
    x: float
    y: float


class ScatterResponse(BaseModel):
    x_label: str
    y_label: str
    points: list[ScatterPoint]


@router.get("/screen_time_histogram", response_model=HistogramResponse)
def get_screen_time_histogram(
    conn = Depends(get_db),
):
    """
    Return a histogram of daily_screen_time_hours in 2-hour buckets.
    """
    column = "daily_screen_time_hours"
    bucket_width = 2
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT MAX({column}) AS max_v, MAX(age) AS max_age FROM smartphone_usage"
    )
    row = cursor.fetchone()
    max_v = float(row["max_v"] or 0.0)
    max_age = int(row["max_age"] or 0)
    bucket_count = max(1, int(max_v // bucket_width) + 1)
    age_upper_bound = max(19, ((max_age // 10) * 10) + 9)
    age_ranges = [
        f"{start}-{19 if start == 0 else start + 9}"
        for start in [0, *range(20, age_upper_bound + 1, 10)]
    ]

    cursor.execute(
        f"""
        SELECT
            CAST({column} / %s AS INT) AS bucket,
            CASE
                WHEN age BETWEEN 0 AND 19 THEN '0-19'
                ELSE CAST((age / 10) * 10 AS TEXT) || '-' || CAST(((age / 10) * 10 + 9) AS TEXT)
            END AS age_range,
            COUNT(*) AS c
        FROM smartphone_usage
        WHERE {column} IS NOT NULL AND age IS NOT NULL
        GROUP BY bucket, age_range
        ORDER BY bucket, age_range
        """,
        (bucket_width,),
    )
    counts_by_bucket: dict[int, dict[str, int]] = {}
    for row in cursor.fetchall():
        bucket = int(row["bucket"])
        age_range = str(row["age_range"])
        counts_by_bucket.setdefault(bucket, {})[age_range] = int(row["c"])

    out_bins: list[HistogramBin] = []
    for i in range(bucket_count):
        age_counts = {
            age_range: counts_by_bucket.get(i, {}).get(age_range, 0)
            for age_range in age_ranges
        }
        out_bins.append(
            HistogramBin(
                bin_start=i * bucket_width,
                bin_end=(i + 1) * bucket_width,
                count=sum(age_counts.values()),
                age_counts=age_counts,
            )
        )
    return HistogramResponse(column=column, age_ranges=age_ranges, bins=out_bins)


@router.get("/scatter_sample", response_model=ScatterResponse)
def get_scatter_sample(
    n: Annotated[int, Query(ge=10, le=5000)] = 500,
    conn = Depends(get_db),
):
    """
    Return a random sample of (screen_time, sleep_hours) pairs for a scatter plot.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT daily_screen_time_hours AS x, sleep_hours AS y
        FROM smartphone_usage
        ORDER BY RANDOM()
        LIMIT %s
        """,
        (n,),
    )
    points = [ScatterPoint(x=float(r["x"]), y=float(r["y"])) for r in cursor.fetchall()]
    return ScatterResponse(
        x_label="daily_screen_time_hours",
        y_label="sleep_hours",
        points=points,
    )
