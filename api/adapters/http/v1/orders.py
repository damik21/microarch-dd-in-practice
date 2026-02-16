from uuid import uuid4

from fastapi import APIRouter, Depends
from starlette import status

from api.adapters.http.v1.schemas import (
    CreateOrderResponse,
    ErrorSchema,
    LocationSchema,
    OrderSchema,
)
from api.dependencies import get_create_order_handler, get_get_active_orders_handler
from core.application.use_cases.commands.create_order import (
    CreateOrderCommand,
    CreateOrderHandler,
)
from core.application.use_cases.queries.get_active_orders import GetActiveOrdersHandler

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "",
    response_model=CreateOrderResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorSchema},
        409: {"model": ErrorSchema},
        500: {"model": ErrorSchema},
    },
)
async def create_order(
    handler: CreateOrderHandler = Depends(get_create_order_handler),
) -> CreateOrderResponse:
    order_id = uuid4()
    command = CreateOrderCommand(
        order_id=order_id,
        street="Несуществующая",
        volume=5,
    )
    await handler.handle(command)
    return CreateOrderResponse(orderId=order_id)


@router.get(
    "/active",
    response_model=list[OrderSchema],
    responses={"default": {"model": ErrorSchema}},
)
async def get_active_orders(
    handler: GetActiveOrdersHandler = Depends(get_get_active_orders_handler),
) -> list[OrderSchema]:
    orders = await handler.handle()
    return [
        OrderSchema(
            id=o.id,
            location=LocationSchema(x=o.location.x, y=o.location.y),
        )
        for o in orders
    ]
