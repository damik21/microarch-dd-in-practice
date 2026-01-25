"""Dependency Injection для FastAPI."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db


def get_database_session() -> Depends:
    """
    Возвращает dependency для получения сессии БД.

    Returns:
        FastAPI Depends для инъекции AsyncSession.
    """
    return Depends(get_db)
