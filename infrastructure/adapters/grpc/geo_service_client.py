import grpc

from core.domain.model.kernel.location import Location
from core.ports.geo_service_client import GeoServiceClientInterface
from infrastructure.adapters.grpc import geo_pb2, geo_pb2_grpc


class GeoServiceClient(GeoServiceClientInterface):
    def __init__(self, host: str) -> None:
        self._host = host

    async def get_location(self, street: str) -> Location:
        async with grpc.aio.insecure_channel(self._host) as channel:
            stub = geo_pb2_grpc.GeoStub(channel)
            request = geo_pb2.GetGeolocationRequest(street=street)  # type: ignore[attr-defined]
            response = await stub.GetGeolocation(request)
            return Location(x=response.location.x, y=response.location.y)
