from core.domain.services import OrderDispatcher
from core.ports import OrderDispatcherInterface


def get_order_dispatcher() -> OrderDispatcherInterface:
    return OrderDispatcher()
