from __future__ import annotations

import asyncio
import logging
from typing import ClassVar
from uuid import UUID

from aiokafka import AIOKafkaProducer

from core.ports.order_events_publisher import OrderEventsPublisherInterface
from infrastructure.adapters.kafka import order_events_pb2

logger = logging.getLogger(__name__)

MAX_SEND_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 0.2


class KafkaOrderEventsProducer(OrderEventsPublisherInterface):
    _producers: ClassVar[dict[str, AIOKafkaProducer]] = {}
    _locks: ClassVar[dict[str, asyncio.Lock]] = {}

    def __init__(self, kafka_host: str, topic: str) -> None:
        self._kafka_host = kafka_host
        self._topic = topic

    async def publish_order_created(self, order_id: UUID) -> None:
        event = order_events_pb2.OrderCreatedIntegrationEvent()  # type: ignore[attr-defined]
        event.order_id = str(order_id)
        await self._send(event.SerializeToString())
        logger.info("Published OrderCreatedIntegrationEvent: order_id=%s", order_id)

    async def publish_order_completed(self, order_id: UUID, courier_id: UUID) -> None:
        event = order_events_pb2.OrderCompletedIntegrationEvent()  # type: ignore[attr-defined]
        event.order_id = str(order_id)
        event.courier_id = str(courier_id)
        await self._send(event.SerializeToString())
        logger.info(
            "Published OrderCompletedIntegrationEvent: order_id=%s, courier_id=%s",
            order_id,
            courier_id,
        )

    async def _send(self, payload: bytes) -> None:
        for attempt in range(1, MAX_SEND_ATTEMPTS + 1):
            try:
                await self._send_once(payload)
                return
            except Exception:
                if attempt == MAX_SEND_ATTEMPTS:
                    logger.exception(
                        "Failed to publish event to Kafka after %s attempts: topic=%s",
                        MAX_SEND_ATTEMPTS,
                        self._topic,
                    )
                    raise
                logger.warning(
                    "Failed to publish event to Kafka, retry %s/%s: topic=%s",
                    attempt,
                    MAX_SEND_ATTEMPTS,
                    self._topic,
                )
                await asyncio.sleep(RETRY_DELAY_SECONDS)

    @classmethod
    async def close_all(cls) -> None:
        hosts = list(cls._producers.keys())
        for host in hosts:
            producer = cls._producers.pop(host)
            try:
                await producer.stop()
            except Exception:
                logger.exception("Failed to stop Kafka producer: host=%s", host)

    @classmethod
    def _get_lock(cls, kafka_host: str) -> asyncio.Lock:
        lock = cls._locks.get(kafka_host)
        if lock is None:
            lock = asyncio.Lock()
            cls._locks[kafka_host] = lock
        return lock

    async def _get_producer(self) -> AIOKafkaProducer:
        lock = self._get_lock(self._kafka_host)
        async with lock:
            producer = self._producers.get(self._kafka_host)
            if producer is None:
                producer = AIOKafkaProducer(bootstrap_servers=self._kafka_host)
                await producer.start()
                self._producers[self._kafka_host] = producer
            return producer

    async def _send_once(self, payload: bytes) -> None:
        producer = await self._get_producer()
        await producer.send_and_wait(self._topic, payload)
