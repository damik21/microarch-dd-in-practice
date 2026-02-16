from uuid import UUID

from pydantic import BaseModel, Field


class LocationSchema(BaseModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)


class OrderSchema(BaseModel):
    id: UUID
    location: LocationSchema


class NewCourierSchema(BaseModel):
    name: str = Field(min_length=1)
    speed: int = Field(ge=1)


class CourierSchema(BaseModel):
    id: UUID
    name: str
    location: LocationSchema


class CreateOrderResponse(BaseModel):
    order_id: UUID = Field(alias="orderId")

    model_config = {"populate_by_name": True}


class CreateCourierResponse(BaseModel):
    courier_id: UUID = Field(alias="courierId")

    model_config = {"populate_by_name": True}


class ErrorSchema(BaseModel):
    code: int
    message: str
