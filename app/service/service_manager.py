from pyfastocloud_models.service.entry import ServiceSettings
from app.service.service import Service

from gevent import select


class ServiceManager(object):
    def __init__(self, host: str, port: int, socketio):
        self._host = host
        self._port = port
        self._socketio = socketio
        self._stop_listen = False
        self._servers_pool = []

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    def stop(self):
        self._stop_listen = True

    def find_or_create_server(self, settings: ServiceSettings) -> Service:
        for server in self._servers_pool:
            if server.id == settings.id:
                return server

        server = Service(self._host, self._port, self._socketio, settings)
        self.__add_server(server)
        return server

    def refresh(self):
        while not self._stop_listen:
            rsockets = []
            for server in self._servers_pool:
                if server.is_connected():
                    rsockets.append(server.socket())

            readable, writeable, _ = select.select(rsockets, [], [], 1)
            for read in readable:
                for server in self._servers_pool:
                    if server.socket() == read:
                        server.recv_data()
                        break

    # private
    def __add_server(self, server: Service):
        self._servers_pool.append(server)
