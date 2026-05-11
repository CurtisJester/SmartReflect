from fastapi import APIRouter

from .routes import router as _routes_router
from .filters import filters_router as _filters_router
from .stats import stats_router as _stats_router


router = APIRouter()
router.include_router(_routes_router)
router.include_router(_filters_router)
router.include_router(_stats_router)

__all__ = ["router"]