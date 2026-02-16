from fastapi import APIRouter

from api.adapters.http import health
from api.adapters.http.v1 import couriers, orders

router = APIRouter()

router.include_router(health.router, tags=["health"])
router.include_router(orders.router)
router.include_router(couriers.router)
