from abc import ABC, abstractmethod

from app.client.client_constants import ClientStatus


# handler for iptv
class IStreamHandler(ABC):
    @abstractmethod
    def on_stream_statistic_received(self, params: dict):
        pass

    @abstractmethod
    def on_stream_sources_changed(self, params: dict):
        pass

    @abstractmethod
    def on_service_statistic_received(self, params: dict):
        pass

    @abstractmethod
    def on_quit_status_stream(self, params: dict):
        pass

    @abstractmethod
    def on_client_state_changed(self, status: ClientStatus):
        pass
