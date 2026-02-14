from fastapi import APIRouter, Depends
from starlette import status

from api.adapters.http.v1.schemas import (
    CourierSchema,
    CreateCourierResponse,
    ErrorSchema,
    LocationSchema,
    NewCourierSchema,
)
from api.dependencies import get_create_courier_handler, get_get_couriers_handler
from core.application.use_cases.commands.create_courier import (
    CreateCourierCommand,
    CreateCourierHandler,
)
from core.application.use_cases.queries.get_couriers import GetCouriersHandler

router = APIRouter(prefix="/couriers", tags=["couriers"])


@router.post(
    "",
    response_model=CreateCourierResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorSchema},
        409: {"model": ErrorSchema},
        500: {"model": ErrorSchema},
    },
)
async def create_courier(
    body: NewCourierSchema,
    handler: CreateCourierHandler = Depends(get_create_courier_handler),
) -> CreateCourierResponse:
    command = CreateCourierCommand(name=body.name, speed=body.speed)
    courier_id = await handler.handle(command)
    return CreateCourierResponse(courierId=courier_id)


@router.get(
    "",
    response_model=list[CourierSchema],
    responses={"default": {"model": ErrorSchema}},
)
async def get_couriers(
    handler: GetCouriersHandler = Depends(get_get_couriers_handler),
) -> list[CourierSchema]:
    couriers = await handler.handle()
    return [
        CourierSchema(
            id=c.id,
            name=c.name,
            location=LocationSchema(x=c.location.x, y=c.location.y),
        )
        for c in couriers
    ]
