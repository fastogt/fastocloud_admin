import logging

from app.service.service_manager import ServiceManager

from app.service.subscriber_client import SubscriberConnection
from app.common.subscriber.entry import Subscriber, Device
from app.common.constants import PlayerMessage
from pyfastocloud.subscriber_client import Commands
from pyfastocloud.client import make_utc_timestamp_seconds
from pyfastocloud.client_handler import IClientHandler, Request, Response, ClientStatus
import pyfastocloud.socket.gevent as gsocket


def check_is_auth_client(client) -> bool:
    if not client:
        return False
    return client.is_active()


class SubscribersServiceManager(ServiceManager, IClientHandler):
    SUBSCRIBER_PORT = 6000
    BANDWIDTH_PORT = 5000
    PING_SUBSCRIBERS_SEC = 60

    def __init__(self, host: str, port: int, socketio):
        super(SubscribersServiceManager, self).__init__(host, port, socketio)
        serversock = gsocket.create_tcp_socket()
        serversock.bind((host, SubscribersServiceManager.SUBSCRIBER_PORT))
        serversock.listen(10)
        self._subscribers_server_socket = serversock
        self._subscribers = []

    def stop(self):
        super(SubscribersServiceManager, self).stop()
        self._subscribers_server_socket.close()

    def refresh(self):
        while not self._stop_listen:
            rsockets = []
            rsockets.append(self._subscribers_server_socket)
            for client in self._subscribers:
                rsockets.append(client.socket())
            for server in self._servers_pool:
                if server.is_connected():
                    rsockets.append(server.socket())

            readable, writeable, _ = gsocket.Select(rsockets, [], [], 1)
            for read in readable:
                # income subscriber connection
                if self._subscribers_server_socket == read:
                    csock, addr = read.accept()
                    subs = SubscriberConnection(csock, addr, self)
                    self.__add_maybe_subscriber(subs)
                    continue

                # subscriber read
                for client in self._subscribers:
                    if client.socket() == read:
                        res = client.recv_data()
                        if not res:
                            self.__close_subscriber(client)
                        break

                for server in self._servers_pool:
                    if server.socket() == read:
                        server.recv_data()
                        break

            ts_sec = make_utc_timestamp_seconds()
            copy_subsc = list(self._subscribers)
            for client in copy_subsc:
                if ts_sec - client.last_ping_ts > SubscribersServiceManager.PING_SUBSCRIBERS_SEC:
                    if client.is_active():
                        result = client.ping(client.gen_request_id())
                        if result:
                            client.last_ping_ts = ts_sec
                        else:
                            self.__close_subscriber(client)

    def process_response(self, client, req: Request, resp: Response):
        if not req or not resp:
            return

        if req.method == Commands.SERVER_PING:
            self._handle_server_ping_command(client, resp)
        elif req.method == Commands.SERVER_GET_CLIENT_INFO:
            self._handle_server_get_client_info(client, resp)

    def process_request(self, client, req: Request):
        if not req:
            return

        result = False
        if req.method == Commands.CLIENT_ACTIVATE_DEVICE:
            result = self._handle_activate_device(client, req.id, req.params)
        elif req.method == Commands.CLIENT_LOGIN:
            result = self._handle_login(client, req.id, req.params)
        elif req.method == Commands.CLIENT_GET_SERVER_INFO:
            result = self._handle_get_server_info(client, req.id, req.params)
        elif req.method == Commands.CLIENT_PING:
            result = self._handle_client_ping(client, req.id, req.params)
        elif req.method == Commands.CLIENT_GET_CHANNELS:
            result = self._handle_get_channels(client, req.id, req.params)
        elif req.method == Commands.CLIENT_GET_RUNTIME_CHANNEL_INFO:
            result = self._handle_get_runtime_channel_info(client, req.id, req.params)
        else:
            pass

        if not result:
            self.__close_subscriber(client)

    def get_watchers_by_stream_id(self, sid: str):
        total = 0
        for user in self._subscribers:
            if user.current_stream_id == sid:
                total += 1

        return total

    def get_user_connections_by_email(self, email) -> list:
        connections = []
        for user in self._subscribers:
            if user.info and user.info.email == email:
                connections.append(user)

        return connections

    def send_message(self, email: str, message: PlayerMessage):
        for user in self._subscribers:
            if user.info and user.info.email == email:
                user.send_message(user.gen_request_id(), message.message, message.type, message.ttl * 1000)

    # protected

    def on_client_state_changed(self, client, status: ClientStatus):
        pass

    def _handle_server_ping_command(self, client, resp: Response):
        pass

    def _handle_server_get_client_info(self, client, resp: Response):
        if resp.is_message():
            client.client_info = resp.result
            logging.info('Client info: {0}'.format(resp.result))

    def _handle_activate_device(self, client, cid: str, params: dict) -> bool:
        login = params[Subscriber.EMAIL_FIELD]
        password_hash = params[Subscriber.PASSWORD_FIELD]

        check_user = Subscriber.objects(email=login, class_check=False).first()
        if not check_user:
            client.activate_device_fail(cid, 'User not found')
            return False

        if check_user.status == Subscriber.Status.NOT_ACTIVE:
            client.activate_device_fail(cid, 'User not active')
            return False

        if check_user.status == Subscriber.Status.BANNED:
            client.activate_device_fail(cid, 'Banned user')
            return False

        if check_user[Subscriber.PASSWORD_FIELD] != password_hash:
            client.activate_device_fail(cid, 'User invalid password')
            return False

        result = client.activate_device_success(cid, check_user.get_not_active_devices())
        if not result:
            return False

        client.info = check_user
        self.__activate_subscriber(client)
        return True

    def _handle_login(self, client, cid: str, params: dict) -> bool:
        login = params[Subscriber.EMAIL_FIELD]
        password_hash = params[Subscriber.PASSWORD_FIELD]
        device_id = params['device_id']

        check_user = Subscriber.objects(email=login, class_check=False).first()
        if not check_user:
            client.login_fail(cid, 'User not found')
            return False

        if check_user.status == Subscriber.Status.NOT_ACTIVE:
            client.login_fail(cid, 'User not active')
            return False

        if check_user.status == Subscriber.Status.BANNED:
            client.login_fail(cid, 'Banned user')
            return False

        if check_user[Subscriber.PASSWORD_FIELD] != password_hash:
            client.login_fail(cid, 'User invalid password')
            return False

        found_device = check_user.find_device(device_id)
        if not found_device:
            client.login_fail(cid, 'Device not found')
            return False

        if found_device.status == Device.Status.BANNED:
            client.login_fail(cid, 'Device banned')
            return False

        if found_device.status == Device.Status.NOT_ACTIVE:
            found_device.status = Device.Status.ACTIVE
            check_user.save()

        user_connections = self.get_user_connections_by_email(login)
        for conn in user_connections:
            if conn.device == found_device:
                client.login_fail(cid, 'Device in use')
                return False

        result = client.login_success(cid)
        if not result:
            return False
        client.info = check_user
        client.device = found_device
        self.__login_subscriber(client)
        return True

    def _handle_get_server_info(self, client, cid: str, params: dict) -> bool:
        if not check_is_auth_client(client):
            client.check_login_fail(cid, 'User not active')
            return False

        return client.get_server_info_success(cid,
                                              '{0}:{1}'.format(self._host, SubscribersServiceManager.BANDWIDTH_PORT))

    def _handle_client_ping(self, client, cid: str, params: dict) -> bool:
        if not check_is_auth_client(client):
            client.check_login_fail(cid, 'User not active')
            return False

        return client.pong(cid)

    def _handle_get_channels(self, client, cid: str, params: dict) -> bool:
        if not check_is_auth_client(client):
            client.check_login_fail(cid, 'User not active')
            return False

        channels, vods = client.info.get_streams()
        return client.get_channels_success(cid, channels, vods)

    def _handle_get_runtime_channel_info(self, client, cid: str, params: dict) -> bool:
        if not check_is_auth_client(client):
            client.check_login_fail(cid, 'User not active')
            return False

        sid = params['id']
        watchers = self.get_watchers_by_stream_id(sid)
        client.current_stream_id = sid
        return client.get_runtime_channel_info_success(cid, sid, watchers)

    # private
    def __close_subscriber(self, subs: SubscriberConnection):
        self.__remove_subscriber(subs)
        subs.disconnect()

    def __add_maybe_subscriber(self, subs: SubscriberConnection):
        self._subscribers.append(subs)
        logging.info('New connection address: {0}, connections: {1}'.format(subs.address(), len(self._subscribers)))

    def __activate_subscriber(self, subs: SubscriberConnection):
        logging.info('Active registered user: {0}, connections: {1}'.format(subs.info.email, len(self._subscribers)))

    def __login_subscriber(self, subs: SubscriberConnection):
        logging.info('Welcome registered user: {0}, connections: {1}'.format(subs.info.email, len(self._subscribers)))

    def __remove_subscriber(self, subs: SubscriberConnection):
        self._subscribers.remove(subs)
        if subs.info:
            logging.info('Bye registered user: {0}, connections: {1}'.format(subs.info.email, len(self._subscribers)))
        else:
            logging.info(
                'Closed connection address: {0}, connections: {1}'.format(subs.address(), len(self._subscribers)))
