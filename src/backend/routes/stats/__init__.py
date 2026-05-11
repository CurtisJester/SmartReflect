from fastapi import APIRouter

from .summary import router as _summary_router
from .distributions import router as _distributions_router
from .breakdowns import router as _breakdowns_router
from .sleep import router as _sleep_stats_router


stats_router = APIRouter(prefix="/stats", tags=["stats"])
stats_router.include_router(_summary_router)
stats_router.include_router(_distributions_router)
stats_router.include_router(_breakdowns_router)
stats_router.include_router(_sleep_stats_router)

__all__ = ["stats_router"]
