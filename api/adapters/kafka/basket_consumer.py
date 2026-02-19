from __future__ import annotations

import logging
from uuid import UUID

from core.application.use_cases.commands.create_order import CreateOrderCommand, CreateOrderHandler
from infrastructure.adapters.grpc.geo_service_client import GeoServiceClient
from infrastructure.adapters.kafka import basket_events_pb2
from infrastructure.adapters.kafka.base_consumer import BaseKafkaConsumer
from infrastructure.adapters.postgres.repositories.base import RepositoryTracker
from infrastructure.adapters.postgres.repositories.order_repository import OrderRepository
from infrastructure.db import async_session_maker

logger = logging.getLogger(__name__)


class BasketConfirmedConsumer(BaseKafkaConsumer):
    def __init__(
        self,
        kafka_host: str,
        topic: str,
        consumer_group: str,
        geo_service_host: str,
    ) -> None:
        super().__init__(kafka_host=kafka_host, topic=topic, consumer_group=consumer_group)
        self._geo_service_host = geo_service_host

    async def _process_message(self, data: bytes) -> None:
        event = basket_events_pb2.BasketConfirmedIntegrationEvent()  # type: ignore[attr-defined]
        event.ParseFromString(data)

        command = CreateOrderCommand(
            order_id=UUID(event.basket_id),
            street=event.address.street,
            volume=event.volume,
        )

        async with async_session_maker() as session:
            tracker = RepositoryTracker(session)
            handler = CreateOrderHandler(
                order_repository=OrderRepository(tracker),
                tracker=tracker,
                geo_service_client=GeoServiceClient(self._geo_service_host),
            )
            await handler.handle(command)

        logger.info(
            "Order created from basket event: order_id=%s, street=%s, volume=%s",
            command.order_id,
            command.street,
            command.volume,
        )
