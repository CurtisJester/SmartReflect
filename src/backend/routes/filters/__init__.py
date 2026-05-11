from fastapi import APIRouter

from .age import router as _age_router
from .sleep import router as _sleep_router
from .notifications import router as _notifications_router


filters_router = APIRouter(tags=["filters"])
filters_router.include_router(_age_router)
filters_router.include_router(_sleep_router)
filters_router.include_router(_notifications_router)

__all__ = ["filters_router"]