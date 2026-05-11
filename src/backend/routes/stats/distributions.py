from typing import Annotated
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from src.backend.db.db import get_db


router = APIRouter()


class HistogramBin(BaseModel):
    bin_start: float
    bin_end: float
    count: int


class HistogramResponse(BaseModel):
    column: str
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
    bins: Annotated[int, Query(ge=2, le=50)] = 10,
    conn = Depends(get_db),
):
    """
    Return a histogram of daily_screen_time_hours with the requested number of bins.
    """
    column = "daily_screen_time_hours"
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT MIN({column}) AS min_v, MAX({column}) AS max_v FROM smartphone_usage"
    )
    row = cursor.fetchone()
    min_v = float(row["min_v"] or 0.0)
    max_v = float(row["max_v"] or 0.0)

    if max_v <= min_v:
        # Degenerate case: single bucket
        cursor.execute("SELECT COUNT(*) AS c FROM smartphone_usage")
        c = cursor.fetchone()["c"] or 0
        return HistogramResponse(
            column=column,
            bins=[HistogramBin(bin_start=min_v, bin_end=max_v, count=c)],
        )

    width = (max_v - min_v) / bins

    # Compute bucket index server-side; clamp the max value into the last bucket.
    cursor.execute(
        f"""
        SELECT
            MIN(CAST((({column} - ?) / ?) AS INT), ?) AS bucket,
            COUNT(*) AS c
        FROM smartphone_usage
        GROUP BY bucket
        ORDER BY bucket
        """,
        (min_v, width, bins - 1),
    )
    counts_by_bucket = {int(r["bucket"]): int(r["c"]) for r in cursor.fetchall()}

    out_bins: list[HistogramBin] = []
    for i in range(bins):
        out_bins.append(
            HistogramBin(
                bin_start=min_v + i * width,
                bin_end=min_v + (i + 1) * width,
                count=counts_by_bucket.get(i, 0),
            )
        )
    return HistogramResponse(column=column, bins=out_bins)


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
        LIMIT ?
        """,
        (n,),
    )
    points = [ScatterPoint(x=float(r["x"]), y=float(r["y"])) for r in cursor.fetchall()]
    return ScatterResponse(
        x_label="daily_screen_time_hours",
        y_label="sleep_hours",
        points=points,
    )
