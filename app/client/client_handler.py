from abc import ABC, abstractmethod

from app.client.json_rpc import Request, Response
from app.client.client_constants import ClientStatus


# handler for client
class IClientHandler(ABC):
    @abstractmethod
    def process_response(self, req: Request, resp: Response):
        pass

    @abstractmethod
    def process_request(self, req: Request):
        pass

    @abstractmethod
    def on_client_state_changed(self, status: ClientStatus):
        pass
