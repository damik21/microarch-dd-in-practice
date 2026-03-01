from abc import ABC, abstractmethod

from core.domain.model.kernel.location import Location


class GeoServiceClientInterface(ABC):
    @abstractmethod
    async def get_location(self, street: str) -> Location:
        raise NotImplementedError
