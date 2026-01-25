"""Процессор outbox для обработки доменных событий."""

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.infrastructure.outbox.message import OutboxMessage
from app.infrastructure.outbox.registry import EventRegistry

logger = logging.getLogger(__name__)


async def process_outbox_messages(
    session: AsyncSession,
    event_registry: EventRegistry,
    batch_size: int = 100,
) -> None:
    """
    Обрабатывает необработанные сообщения из outbox.

    Args:
        session: Сессия базы данных.
        event_registry: Реестр событий для декодирования.
        batch_size: Размер батча для обработки.
    """
    # Получаем необработанные сообщения
    stmt = (
        select(OutboxMessage)
        .where(OutboxMessage.processed_at_utc.is_(None))
        .order_by(OutboxMessage.occurred_at_utc)
        .limit(batch_size)
    )

    result = await session.execute(stmt)
    messages = result.scalars().all()

    if not messages:
        logger.debug("No unprocessed messages in outbox")
        return

    logger.info(f"Processing {len(messages)} messages from outbox")

    for message in messages:
        try:
            # Декодируем событие
            event = event_registry.decode_domain_event(message)

            # TODO: Публикуем событие через медиатор или отправляем в Kafka
            logger.info(f"Processing event: {event.get_name()}, id: {event.id}")

            # Помечаем сообщение как обработанное
            message.processed_at_utc = datetime.now(timezone.utc)
            await session.commit()

            logger.info(f"Successfully processed message: {message.id}")

        except Exception as e:
            logger.error(f"Error processing message {message.id}: {e}")
            await session.rollback()
            # Можно добавить retry логику или dead letter queue


async def run_outbox_processor(interval_seconds: int = 5) -> None:
    """
    Запускает процессор outbox с периодической обработкой.

    Args:
        interval_seconds: Интервал между проверками outbox (в секундах).
    """
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.core.database import Base, engine

    # Используем существующий engine или создаём новый
    # Для outbox processor создаём отдельный engine, чтобы не зависеть от основного
    processor_engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(processor_engine, expire_on_commit=False)

    # Создаём таблицы (если их нет)
    async with processor_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Создаём реестр событий
    event_registry = EventRegistry()
    # TODO: Зарегистрировать все доменные события
    # event_registry.register_domain_event(SomeDomainEvent)

    logger.info(f"Starting outbox processor with interval: {interval_seconds}s")

    try:
        while True:
            async with async_session() as session:
                await process_outbox_messages(session, event_registry)

            await asyncio.sleep(interval_seconds)

    except KeyboardInterrupt:
        logger.info("Outbox processor stopped by user")
    except Exception as e:
        logger.error(f"Outbox processor error: {e}")
    finally:
        await processor_engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(run_outbox_processor())
