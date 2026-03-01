from __future__ import annotations

from api.adapters.kafka.basket_consumer import BasketConfirmedConsumer
from config.config import Settings
from infrastructure.adapters.kafka.base_consumer import BaseKafkaConsumer


def build_consumers(settings: Settings) -> list[BaseKafkaConsumer]:
    return [
        BasketConfirmedConsumer(
            kafka_host=settings.kafka_host,
            topic=settings.kafka_basket_confirmed_topic,
            consumer_group=settings.kafka_consumer_group,
            geo_service_host=settings.geo_service_grpc_host,
        ),
    ]
