from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from infrastructure.adapters.kafka.order_events_producer import KafkaOrderEventsProducer


def make_producer_mock() -> AsyncMock:
    return AsyncMock()


@pytest.fixture(autouse=True)
async def clear_shared_producers() -> None:
    await KafkaOrderEventsProducer.close_all()
    yield
    await KafkaOrderEventsProducer.close_all()


@pytest.mark.asyncio
async def test_send_success_from_first_attempt() -> None:
    payload = b"payload"
    kafka_producer = make_producer_mock()
    producer = KafkaOrderEventsProducer(
        kafka_host="localhost:9092", topic="orders.events"
    )

    with patch(
        "infrastructure.adapters.kafka.order_events_producer.AIOKafkaProducer",
        return_value=kafka_producer,
    ) as producer_class:
        await producer._send(payload)

    producer_class.assert_called_once_with(bootstrap_servers="localhost:9092")
    kafka_producer.start.assert_awaited_once()
    kafka_producer.send_and_wait.assert_awaited_once_with("orders.events", payload)


@pytest.mark.asyncio
async def test_send_raises_when_kafka_unavailable() -> None:
    payload = b"payload"
    kafka_producer = make_producer_mock()
    kafka_producer.send_and_wait.side_effect = RuntimeError("kafka unavailable")
    producer = KafkaOrderEventsProducer(
        kafka_host="localhost:9092", topic="orders.events"
    )

    with (
        patch(
            "infrastructure.adapters.kafka.order_events_producer.AIOKafkaProducer",
            return_value=kafka_producer,
        ) as producer_class,
        pytest.raises(RuntimeError, match="kafka unavailable"),
    ):
        await producer._send(payload)

    producer_class.assert_called_once_with(bootstrap_servers="localhost:9092")
    kafka_producer.start.assert_awaited_once()
    kafka_producer.send_and_wait.assert_awaited_once_with("orders.events", payload)
