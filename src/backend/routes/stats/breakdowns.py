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
    age_counts: dict[str, int]


class BreakdownResponse(BaseModel):
    items: list[BreakdownItem]
    total_users: int
    coverage_pct: float
    addicted_designation: list[str]
    age_ranges: list[str]


class AgeBreakdownItem(BaseModel):
    age_range: str
    count: int
    pct_of_total: float


class AgeBreakdownResponse(BaseModel):
    items: list[AgeBreakdownItem]
    total_users: int


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

    cursor.execute("SELECT MAX(age) AS max_age FROM smartphone_usage")
    max_age = int(cursor.fetchone()["max_age"] or 0)
    age_upper_bound = max(19, ((max_age // 10) * 10) + 9)
    age_ranges = [
        f"{start}-{19 if start == 0 else start + 9}"
        for start in [0, *range(20, age_upper_bound + 1, 10)]
    ]

    cursor.execute(
        """
        SELECT
            addiction_level AS level,
            CASE
                WHEN age BETWEEN 0 AND 19 THEN '0-19'
                ELSE CAST((age / 10) * 10 AS INT) || '-' || CAST(((age / 10) * 10 + 9) AS INT)
            END AS age_range,
            COUNT(*) AS c
        FROM smartphone_usage
        WHERE addiction_level IS NOT NULL AND age IS NOT NULL
        GROUP BY addiction_level, age_range
        """
    )
    age_counts_by_level: dict[str, dict[str, int]] = {}
    for row in cursor.fetchall():
        level = str(row["level"])
        age_range = str(row["age_range"])
        age_counts_by_level.setdefault(level, {})[age_range] = int(row["c"])

    lower_map = {k.lower(): k for k in raw.keys()}
    ordered: list[BreakdownItem] = []
    used: set[str] = set()
    for canonical in _ADDICTION_ORDER:
        key = lower_map.get(canonical.lower())
        if key is not None:
            count = raw[key]
            pct = (count / total_users * 100.0) if total_users else 0.0
            age_counts = {
                age_range: age_counts_by_level.get(key, {}).get(age_range, 0)
                for age_range in age_ranges
            }
            ordered.append(
                BreakdownItem(
                    level=canonical,
                    count=count,
                    pct_of_total=pct,
                    is_addicted_designation=canonical.lower() in _ADDICTED_LEVELS,
                    age_counts=age_counts,
                )
            )
            used.add(key)

    # Append any unrecognized non-"None" labels in alphabetical order.
    for key in sorted(raw.keys()):
        if key in used or key.lower() == "none":
            continue
        count = raw[key]
        pct = (count / total_users * 100.0) if total_users else 0.0
        age_counts = {
            age_range: age_counts_by_level.get(key, {}).get(age_range, 0)
            for age_range in age_ranges
        }
        ordered.append(
            BreakdownItem(
                level=key,
                count=count,
                pct_of_total=pct,
                is_addicted_designation=key.lower() in _ADDICTED_LEVELS,
                age_counts=age_counts,
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
        age_ranges=age_ranges,
    )


@router.get("/age_breakdown", response_model=AgeBreakdownResponse)
def get_age_breakdown(conn = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS c, MAX(age) AS max_age FROM smartphone_usage")
    summary = cursor.fetchone()
    total_users = int(summary["c"] or 0)
    max_age = int(summary["max_age"] or 0)
    upper_bound = max(19, ((max_age // 10) * 10) + 9)

    cursor.execute(
        """
        SELECT
            CASE
                WHEN age BETWEEN 0 AND 19 THEN '0-19'
                ELSE CAST((age / 10) * 10 AS INT) || '-' || CAST(((age / 10) * 10 + 9) AS INT)
            END AS age_range,
            CASE
                WHEN age BETWEEN 0 AND 19 THEN 0
                ELSE CAST(age / 10 AS INT)
            END AS sort_key,
            COUNT(*) AS c
        FROM smartphone_usage
        WHERE age IS NOT NULL
        GROUP BY age_range, sort_key
        ORDER BY sort_key
        """
    )
    counts_by_range = {str(r["age_range"]): int(r["c"]) for r in cursor.fetchall()}

    items: list[AgeBreakdownItem] = []
    for start in [0, *range(20, upper_bound + 1, 10)]:
        end = 19 if start == 0 else start + 9
        label = f"{start}-{end}"
        count = counts_by_range.get(label, 0)
        pct = (count / total_users * 100.0) if total_users else 0.0
        items.append(AgeBreakdownItem(age_range=label, count=count, pct_of_total=pct))

    return AgeBreakdownResponse(items=items, total_users=total_users)
