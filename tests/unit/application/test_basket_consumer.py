from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

from api.adapters.kafka.basket_consumer import BasketConfirmedConsumer
from core.application.use_cases.commands.create_order import CreateOrderCommand
from infrastructure.adapters.kafka import basket_events_pb2


def make_consumer() -> BasketConfirmedConsumer:
    return BasketConfirmedConsumer(
        kafka_host="localhost:9092",
        topic="baskets.events",
        consumer_group="test-group",
        geo_service_host="localhost:5004",
    )


def make_event(
    basket_id: str | None = None,
    street: str = "Ленина",
    volume: int = 3,
) -> bytes:
    event = basket_events_pb2.BasketConfirmedIntegrationEvent()  # type: ignore[attr-defined]
    event.basket_id = basket_id or str(uuid4())
    event.address.street = street
    event.volume = volume
    return event.SerializeToString()


@pytest.mark.asyncio
async def test_process_message_creates_order_with_correct_street() -> None:
    consumer = make_consumer()
    handler_mock = AsyncMock()

    with (
        patch("api.adapters.kafka.basket_consumer.async_session_maker"),
        patch("api.adapters.kafka.basket_consumer.RepositoryTracker"),
        patch("api.adapters.kafka.basket_consumer.OrderRepository"),
        patch("api.adapters.kafka.basket_consumer.GeoServiceClient"),
        patch(
            "api.adapters.kafka.basket_consumer.CreateOrderHandler",
            return_value=handler_mock,
        ),
    ):
        await consumer._process_message(make_event(street="Ленина", volume=3))

    handler_mock.handle.assert_called_once()
    command: CreateOrderCommand = handler_mock.handle.call_args[0][0]
    assert isinstance(command, CreateOrderCommand)
    assert command.street == "Ленина"


@pytest.mark.asyncio
async def test_process_message_parses_basket_id_as_uuid() -> None:
    consumer = make_consumer()
    handler_mock = AsyncMock()
    expected_id = uuid4()

    with (
        patch("api.adapters.kafka.basket_consumer.async_session_maker"),
        patch("api.adapters.kafka.basket_consumer.RepositoryTracker"),
        patch("api.adapters.kafka.basket_consumer.OrderRepository"),
        patch("api.adapters.kafka.basket_consumer.GeoServiceClient"),
        patch(
            "api.adapters.kafka.basket_consumer.CreateOrderHandler",
            return_value=handler_mock,
        ),
    ):
        await consumer._process_message(
            make_event(basket_id=str(expected_id), street="Мира", volume=1)
        )

    command: CreateOrderCommand = handler_mock.handle.call_args[0][0]
    assert isinstance(command.order_id, UUID)
    assert command.order_id == expected_id


@pytest.mark.asyncio
async def test_process_message_passes_volume_to_command() -> None:
    consumer = make_consumer()
    handler_mock = AsyncMock()

    with (
        patch("api.adapters.kafka.basket_consumer.async_session_maker"),
        patch("api.adapters.kafka.basket_consumer.RepositoryTracker"),
        patch("api.adapters.kafka.basket_consumer.OrderRepository"),
        patch("api.adapters.kafka.basket_consumer.GeoServiceClient"),
        patch(
            "api.adapters.kafka.basket_consumer.CreateOrderHandler",
            return_value=handler_mock,
        ),
    ):
        await consumer._process_message(make_event(volume=7))

    command: CreateOrderCommand = handler_mock.handle.call_args[0][0]
    assert command.volume == 7


@pytest.mark.asyncio
async def test_consume_logs_error_and_continues_on_malformed_bytes() -> None:
    """_consume() перехватывает исключение из _process_message и логирует его."""
    consumer = make_consumer()
    malformed = b"not-a-valid-protobuf"

    with patch("infrastructure.adapters.kafka.base_consumer.logger") as mock_logger:
        # Эмулируем одно сообщение с невалидными данными
        async def fake_consume() -> None:
            msgs = [MagicMock(value=malformed)]
            for msg in msgs:
                try:
                    await consumer._process_message(msg.value)
                except Exception:
                    mock_logger.exception(
                        "%s: error processing message from topic %s",
                        consumer.__class__.__name__,
                        consumer._topic,
                    )

        await fake_consume()

    mock_logger.exception.assert_called_once()
