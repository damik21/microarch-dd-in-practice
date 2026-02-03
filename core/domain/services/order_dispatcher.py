from __future__ import annotations

from core.domain.model.courier.courier import Courier
from core.domain.model.order.order import Order
from core.ports.order_dispatcher import OrderDispatcherInterface


class OrderDispatcher(OrderDispatcherInterface):
    def dispatch(self, order: Order, couriers: list[Courier]) -> Courier | None:
        # Фильтруем курьеров, которые могут взять заказ
        eligible_couriers = [
            courier
            for courier in couriers
            if courier.can_take_order(order.volume)
        ]

        if not eligible_couriers:
            return None

        # Находим курьера с минимальным временем доставки
        best_courier = min(
            eligible_couriers,
            key=lambda c: c.calculate_steps_to_location(order.location),
        )

        # Назначаем заказ на курьера
        order.assign(best_courier.id)

        # Курьер берёт заказ (занимает место хранения)
        best_courier.take_order(order_id=order.id, volume=order.volume)

        return best_courier
