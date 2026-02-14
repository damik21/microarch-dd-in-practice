import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.adapters.http.router import router as v1_router
from api.tasks import assign_orders, move_couriers, run_periodic
from config.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting periodic tasks...")
    assign_task = asyncio.create_task(
        run_periodic(assign_orders, interval=1, name="assign_orders")
    )
    move_task = asyncio.create_task(
        run_periodic(move_couriers, interval=1, name="move_couriers")
    )
    logger.info("Periodic tasks started (assign_orders, move_couriers)")
    yield
    logger.info("Stopping periodic tasks...")
    assign_task.cancel()
    move_task.cancel()


app = FastAPI(
    title="Delivery Service",
    description="Сервис доставки на основе DDD и Clean Architecture",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(v1_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=int(settings.http_port),
        reload=True,
    )
