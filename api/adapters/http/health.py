"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """
    Проверка здоровья сервиса.

    Returns:
        Словарь со статусом "Healthy".
    """
    return {"status": "Healthy"}
