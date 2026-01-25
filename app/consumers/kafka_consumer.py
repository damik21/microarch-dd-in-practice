"""Kafka consumer для обработки внешних событий."""

import asyncio
import logging

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError

from app.core.config import settings

logger = logging.getLogger(__name__)


async def consume_basket_confirmed() -> None:
    """
    Consumer для обработки событий подтверждения корзины.

    Запускается как отдельный процесс.
    """
    consumer = AIOKafkaConsumer(
        settings.kafka_basket_confirmed_topic,
        bootstrap_servers=settings.kafka_host,
        group_id=settings.kafka_consumer_group,
        auto_offset_reset="earliest",
    )

    try:
        await consumer.start()
        logger.info(
            f"Started consuming from topic: {settings.kafka_basket_confirmed_topic}"
        )

        async for message in consumer:
            logger.info(
                f"Received message: topic={message.topic}, "
                f"partition={message.partition}, offset={message.offset}"
            )
            # TODO: Обработка сообщения
            # Здесь будет логика обработки события basket.confirmed

    except KafkaError as e:
        logger.error(f"Kafka error: {e}")
    finally:
        await consumer.stop()
        logger.info("Kafka consumer stopped")


async def consume_order_status_changed() -> None:
    """
    Consumer для обработки событий изменения статуса заказа.

    Запускается как отдельный процесс.
    """
    consumer = AIOKafkaConsumer(
        settings.kafka_order_changed_topic,
        bootstrap_servers=settings.kafka_host,
        group_id=settings.kafka_consumer_group,
        auto_offset_reset="earliest",
    )

    try:
        await consumer.start()
        logger.info(
            f"Started consuming from topic: {settings.kafka_order_changed_topic}"
        )

        async for message in consumer:
            logger.info(
                f"Received message: topic={message.topic}, "
                f"partition={message.partition}, offset={message.offset}"
            )
            # TODO: Обработка сообщения
            # Здесь будет логика обработки события order.status.changed

    except KafkaError as e:
        logger.error(f"Kafka error: {e}")
    finally:
        await consumer.stop()
        logger.info("Kafka consumer stopped")


async def main() -> None:
    """Главная функция для запуска всех consumers."""
    logger.info("Starting Kafka consumers...")

    # Запускаем consumers параллельно
    await asyncio.gather(
        consume_basket_confirmed(),
        consume_order_status_changed(),
        return_exceptions=True,
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(main())
