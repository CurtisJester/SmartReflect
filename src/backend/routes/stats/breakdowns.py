from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.backend.db.db import get_db


router = APIRouter()


# Canonical ordering for addiction_level shown in the breakdown chart.
# "None" is intentionally excluded - users with no addiction level designation
# are still counted in total_users but not displayed as a chart bar.
_ADDICTION_ORDER = ["Mild", "Moderate", "Severe"]

# Levels that classify a user as "addicted" per the dataset designation.
_ADDICTED_LEVELS = {"moderate", "severe"}


class BreakdownItem(BaseModel):
    level: str
    count: int
    pct_of_total: float
    is_addicted_designation: bool


class BreakdownResponse(BaseModel):
    items: list[BreakdownItem]
    total_users: int
    coverage_pct: float
    addicted_designation: list[str]


@router.get("/addiction_breakdown", response_model=BreakdownResponse)
def get_addiction_breakdown(conn = Depends(get_db)):
    """
    Return COUNT(*) grouped by addiction_level, ordered Mild -> Moderate -> Severe.
    The "None" level is excluded from items but still counted in total_users.

    Each item's pct_of_total is its share of the *total* user base (not the
    filtered subset), so the bars together represent the chart's coverage of
    the dataset (coverage_pct).
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT addiction_level AS level, COUNT(*) AS c
        FROM smartphone_usage
        GROUP BY addiction_level
        """
    )
    raw = {str(r["level"]): int(r["c"]) for r in cursor.fetchall()}
    total_users = sum(raw.values())

    lower_map = {k.lower(): k for k in raw.keys()}
    ordered: list[BreakdownItem] = []
    used: set[str] = set()
    for canonical in _ADDICTION_ORDER:
        key = lower_map.get(canonical.lower())
        if key is not None:
            count = raw[key]
            pct = (count / total_users * 100.0) if total_users else 0.0
            ordered.append(
                BreakdownItem(
                    level=canonical,
                    count=count,
                    pct_of_total=pct,
                    is_addicted_designation=canonical.lower() in _ADDICTED_LEVELS,
                )
            )
            used.add(key)

    # Append any unrecognized non-"None" labels in alphabetical order.
    for key in sorted(raw.keys()):
        if key in used or key.lower() == "none":
            continue
        count = raw[key]
        pct = (count / total_users * 100.0) if total_users else 0.0
        ordered.append(
            BreakdownItem(
                level=key,
                count=count,
                pct_of_total=pct,
                is_addicted_designation=key.lower() in _ADDICTED_LEVELS,
            )
        )

    coverage_pct = sum(item.pct_of_total for item in ordered)

    return BreakdownResponse(
        items=ordered,
        total_users=total_users,
        coverage_pct=coverage_pct,
        addicted_designation=[
            lvl for lvl in _ADDICTION_ORDER if lvl.lower() in _ADDICTED_LEVELS
        ],
    )
