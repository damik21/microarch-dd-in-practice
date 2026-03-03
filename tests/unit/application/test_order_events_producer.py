from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from infrastructure.adapters.kafka.order_events_producer import (
    MAX_SEND_ATTEMPTS,
    RETRY_DELAY_SECONDS,
    KafkaOrderEventsProducer,
)


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
    producer = KafkaOrderEventsProducer(kafka_host="localhost:9092", topic="orders.events")

    with (
        patch(
            "infrastructure.adapters.kafka.order_events_producer.AIOKafkaProducer",
            return_value=kafka_producer,
        ) as producer_class,
        patch(
            "infrastructure.adapters.kafka.order_events_producer.asyncio.sleep",
            new_callable=AsyncMock,
        ) as sleep_mock,
    ):
        await producer._send(payload)

    producer_class.assert_called_once_with(bootstrap_servers="localhost:9092")
    kafka_producer.start.assert_awaited_once()
    kafka_producer.send_and_wait.assert_awaited_once_with("orders.events", payload)
    sleep_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_send_retries_after_temporary_error() -> None:
    payload = b"payload"
    kafka_producer = make_producer_mock()
    kafka_producer.send_and_wait.side_effect = [
        RuntimeError("temporary error"),
        None,
    ]
    producer = KafkaOrderEventsProducer(kafka_host="localhost:9092", topic="orders.events")

    with (
        patch(
            "infrastructure.adapters.kafka.order_events_producer.AIOKafkaProducer",
            return_value=kafka_producer,
        ) as producer_class,
        patch(
            "infrastructure.adapters.kafka.order_events_producer.asyncio.sleep",
            new_callable=AsyncMock,
        ) as sleep_mock,
    ):
        await producer._send(payload)

    producer_class.assert_called_once_with(bootstrap_servers="localhost:9092")
    kafka_producer.start.assert_awaited_once()
    assert kafka_producer.send_and_wait.await_count == 2
    sleep_mock.assert_awaited_once_with(RETRY_DELAY_SECONDS)


@pytest.mark.asyncio
async def test_send_raises_after_exhausted_retries() -> None:
    payload = b"payload"
    kafka_producer = make_producer_mock()
    kafka_producer.send_and_wait.side_effect = RuntimeError("kafka unavailable")
    producer = KafkaOrderEventsProducer(kafka_host="localhost:9092", topic="orders.events")

    with (
        patch(
            "infrastructure.adapters.kafka.order_events_producer.AIOKafkaProducer",
            return_value=kafka_producer,
        ) as producer_class,
        patch(
            "infrastructure.adapters.kafka.order_events_producer.asyncio.sleep",
            new_callable=AsyncMock,
        ) as sleep_mock,
        pytest.raises(RuntimeError, match="kafka unavailable"),
    ):
        await producer._send(payload)

    producer_class.assert_called_once_with(bootstrap_servers="localhost:9092")
    kafka_producer.start.assert_awaited_once()
    assert kafka_producer.send_and_wait.await_count == MAX_SEND_ATTEMPTS
    assert sleep_mock.await_count == MAX_SEND_ATTEMPTS - 1
