"""Главный роутер API v1."""

from fastapi import APIRouter

from api.adapters.http.v1.endpoints import health

router = APIRouter()

router.include_router(health.router, tags=["health"])
