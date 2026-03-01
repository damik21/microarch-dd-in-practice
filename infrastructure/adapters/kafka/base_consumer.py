from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod

from aiokafka import AIOKafkaConsumer

logger = logging.getLogger(__name__)


class BaseKafkaConsumer(ABC):
    def __init__(
        self,
        kafka_host: str,
        topic: str,
        consumer_group: str,
    ) -> None:
        self._topic = topic
        self._consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=kafka_host,
            group_id=consumer_group,
        )
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        await self._consumer.start()
        self._task = asyncio.create_task(self._consume())
        logger.info(
            "%s started (topic=%s)",
            self.__class__.__name__,
            self._topic,
        )

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
        await self._consumer.stop()
        logger.info("%s stopped", self.__class__.__name__)

    async def _consume(self) -> None:
        async for msg in self._consumer:
            try:
                await self._process_message(msg.value)
            except Exception:
                logger.exception(
                    "%s: error processing message from topic %s",
                    self.__class__.__name__,
                    self._topic,
                )

    @abstractmethod
    async def _process_message(self, data: bytes) -> None: ...
