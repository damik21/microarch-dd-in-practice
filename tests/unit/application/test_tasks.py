from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api.tasks import assign_orders, move_couriers, run_periodic


class TestRunPeriodic:
    async def test_calls_task_multiple_times(self) -> None:
        task = AsyncMock()
        periodic = asyncio.create_task(
            run_periodic(task, interval=0, name="test")
        )
        await asyncio.sleep(0.05)
        periodic.cancel()

        assert task.await_count >= 2

    async def test_continues_after_task_error(self) -> None:
        call_count = 0

        async def failing_task() -> None:
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise RuntimeError("boom")

        periodic = asyncio.create_task(
            run_periodic(failing_task, interval=0, name="test")
        )
        await asyncio.sleep(0.05)
        periodic.cancel()

        assert call_count >= 3

    async def test_stops_on_cancel(self) -> None:
        task = AsyncMock()
        periodic = asyncio.create_task(
            run_periodic(task, interval=10, name="test")
        )
        await asyncio.sleep(0.01)
        periodic.cancel()

        with pytest.raises(asyncio.CancelledError):
            await periodic

    async def test_logs_exception(self) -> None:
        task = AsyncMock(side_effect=ValueError("test error"))

        with patch("api.tasks.logger") as mock_logger:
            periodic = asyncio.create_task(
                run_periodic(task, interval=0, name="my_task")
            )
            await asyncio.sleep(0.01)
            periodic.cancel()

            mock_logger.exception.assert_called()
            args = mock_logger.exception.call_args
            assert "my_task" in str(args)


class TestAssignOrders:
    async def test_creates_handler_and_calls_handle(self) -> None:
        mock_session = AsyncMock()
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        mock_session_maker.return_value.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("api.tasks.async_session_maker", mock_session_maker),
            patch("api.tasks.AssignOrderHandler") as MockHandler,
        ):
            mock_handler_instance = AsyncMock()
            MockHandler.return_value = mock_handler_instance

            await assign_orders()

            MockHandler.assert_called_once()
            mock_handler_instance.handle.assert_called_once()

    async def test_uses_correct_dependencies(self) -> None:
        mock_session = AsyncMock()
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        mock_session_maker.return_value.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("api.tasks.async_session_maker", mock_session_maker),
            patch("api.tasks.AssignOrderHandler") as MockHandler,
            patch("api.tasks.RepositoryTracker") as MockTracker,
            patch("api.tasks.OrderRepository") as MockOrderRepo,
            patch("api.tasks.CourierRepository") as MockCourierRepo,
            patch("api.tasks.OrderDispatcher") as MockDispatcher,
        ):
            MockHandler.return_value = AsyncMock()

            await assign_orders()

            MockTracker.assert_called_once_with(mock_session)
            tracker = MockTracker.return_value
            MockOrderRepo.assert_called_once_with(tracker)
            MockCourierRepo.assert_called_once_with(tracker)
            MockDispatcher.assert_called_once()
            MockHandler.assert_called_once_with(
                order_repository=MockOrderRepo.return_value,
                courier_repository=MockCourierRepo.return_value,
                dispatcher=MockDispatcher.return_value,
                tracker=tracker,
            )


class TestMoveCouriers:
    async def test_creates_handler_and_calls_handle(self) -> None:
        mock_session = AsyncMock()
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        mock_session_maker.return_value.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("api.tasks.async_session_maker", mock_session_maker),
            patch("api.tasks.MoveCouriersHandler") as MockHandler,
        ):
            mock_handler_instance = AsyncMock()
            MockHandler.return_value = mock_handler_instance

            await move_couriers()

            MockHandler.assert_called_once()
            mock_handler_instance.handle.assert_called_once()

    async def test_uses_correct_dependencies(self) -> None:
        mock_session = AsyncMock()
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        mock_session_maker.return_value.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("api.tasks.async_session_maker", mock_session_maker),
            patch("api.tasks.MoveCouriersHandler") as MockHandler,
            patch("api.tasks.RepositoryTracker") as MockTracker,
            patch("api.tasks.OrderRepository") as MockOrderRepo,
            patch("api.tasks.CourierRepository") as MockCourierRepo,
        ):
            MockHandler.return_value = AsyncMock()

            await move_couriers()

            MockTracker.assert_called_once_with(mock_session)
            tracker = MockTracker.return_value
            MockOrderRepo.assert_called_once_with(tracker)
            MockCourierRepo.assert_called_once_with(tracker)
            MockHandler.assert_called_once_with(
                order_repository=MockOrderRepo.return_value,
                courier_repository=MockCourierRepo.return_value,
                tracker=tracker,
            )
