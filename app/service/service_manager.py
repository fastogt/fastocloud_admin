from app.service.service_entry import ServiceSettings
from app.service.service import Service


class ServiceManager(object):
    def __init__(self, host: str, port: int, socketio):
        self._host = host
        self._port = port
        self._socketio = socketio
        self._servers_pool = []

    def find_or_create_server(self, settings: ServiceSettings) -> Service:
        for server in self._servers_pool:
            if server.id == str(settings.id):
                return server

        server = Service(self._host, self._port, self._socketio, settings)
        self.__add_server(server)
        return server

    # private
    def __add_server(self, server: Service):
        self._servers_pool.append(server)
