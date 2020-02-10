from datetime import datetime
from bson.objectid import ObjectId

from pyfastocloud_models.stream.entry import IStream, ProxyStream, EncodeStream, RelayStream, TimeshiftRecorderStream, \
    CatchupStream, TimeshiftPlayerStream, TestLifeStream, VodRelayStream, VodEncodeStream, ProxyVodStream, \
    CodRelayStream, CodEncodeStream, EventStream
from pyfastocloud.client_constants import ClientStatus

from pyfastocloud_models.series.entry import Serial
import pyfastocloud_models.constants as constants
from pyfastocloud_models.service.entry import ServiceSettings, ProviderPair, safe_delete_stream
from app.service.service_client import ServiceClient, OperationSystem
from app.service.stream_handler import IStreamHandler


class OnlineUsers(object):
    __slots__ = ['daemon', 'http', 'vods', 'cods', 'subscribers']

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__slots__:
                setattr(self, key, value)

    def __str__(self):
        if hasattr(self, 'subscribers'):
            return 'daemon:{0} http:{1} vods:{2} cods:{3} subscribers:{4}'.format(self.daemon, self.http, self.vods,
                                                                                  self.cods, self.subscribers)

        return 'daemon:{0} http:{1} vods:{2} cods:{3}'.format(self.daemon, self.http, self.vods, self.cods)


class ServiceFields:
    ID = 'id'
    CPU = 'cpu'
    GPU = 'gpu'
    LOAD_AVERAGE = 'load_average'
    MEMORY_TOTAL = 'memory_total'
    MEMORY_FREE = 'memory_free'
    HDD_TOTAL = 'hdd_total'
    HDD_FREE = 'hdd_free'
    BANDWIDTH_IN = 'bandwidth_in'
    BANDWIDTH_OUT = 'bandwidth_out'
    VERSION = 'version'
    UPTIME = 'uptime'
    TIMESTAMP = 'timestamp'
    STATUS = 'status'
    ONLINE_USERS = 'online_users'
    OS = 'os'


class Service(IStreamHandler):
    SERVER_ID = 'server_id'
    STREAM_DATA_CHANGED = 'stream_data_changed'
    SERVICE_DATA_CHANGED = 'service_data_changed'
    INIT_VALUE = 0
    CALCULATE_VALUE = None

    # runtime
    _cpu = INIT_VALUE
    _gpu = INIT_VALUE
    _load_average = CALCULATE_VALUE
    _memory_total = INIT_VALUE
    _memory_free = INIT_VALUE
    _hdd_total = INIT_VALUE
    _hdd_free = INIT_VALUE
    _bandwidth_in = INIT_VALUE
    _bandwidth_out = INIT_VALUE
    _uptime = CALCULATE_VALUE
    _timestamp = CALCULATE_VALUE
    _streams = []
    _online_users = None
    _os = OperationSystem()

    def __init__(self, host, port, socketio, settings: ServiceSettings):
        self._settings = settings
        self.__reload_from_db()
        # other fields
        self._client = ServiceClient(settings.id, settings.host.host, settings.host.port, self)
        self._host = host
        self._port = port
        self._socketio = socketio

    def connect(self):
        return self._client.connect()

    def is_connected(self):
        return self._client.is_connected()

    def disconnect(self):
        return self._client.disconnect()

    def socket(self):
        return self._client.socket()

    def recv_data(self):
        return self._client.recv_data()

    def stop(self, delay: int):
        return self._client.stop_service(delay)

    def get_log_service(self):
        return self._client.get_log_service(self._host, self._port)

    def ping(self):
        return self._client.ping_service()

    def activate(self, license_key: str):
        return self._client.activate(license_key)

    def sync(self, prepare=False):
        settings = self._settings
        if prepare:
            self._client.prepare_service(settings)
        res = self._client.sync_service(settings)
        self.__refresh_catchups()
        return res

    def get_log_stream(self, sid: str):
        stream = self.find_stream_by_id(sid)
        if stream:
            self._client.get_log_stream(self._host, self._port, sid, stream.generate_feedback_dir())

    def get_pipeline_stream(self, sid):
        stream = self.find_stream_by_id(sid)
        if stream:
            self._client.get_pipeline_stream(self._host, self._port, sid, stream.generate_feedback_dir())

    def start_stream(self, sid: str):
        stream = self.find_stream_by_id(sid)
        if stream:
            self._client.start_stream(stream.config())

    def stop_stream(self, sid: str):
        stream = self.find_stream_by_id(sid)
        if stream:
            self._client.stop_stream(sid)

    def restart_stream(self, sid: str):
        stream = self.find_stream_by_id(sid)
        if stream:
            self._client.restart_stream(sid)

    def get_vods_in(self) -> list:
        return self._client.get_vods_in()

    @property
    def host(self) -> str:
        return self._host

    @property
    def id(self) -> ObjectId:
        return self._settings.id

    @property
    def status(self) -> ClientStatus:
        return self._client.status()

    @property
    def cpu(self):
        return self._cpu

    @property
    def gpu(self):
        return self._gpu

    @property
    def load_average(self):
        return self._load_average

    @property
    def memory_total(self):
        return self._memory_total

    @property
    def memory_free(self):
        return self._memory_free

    @property
    def hdd_total(self):
        return self._hdd_total

    @property
    def hdd_free(self):
        return self._hdd_free

    @property
    def bandwidth_in(self):
        return self._bandwidth_in

    @property
    def bandwidth_out(self):
        return self._bandwidth_out

    @property
    def uptime(self):
        return self._uptime

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def version(self) -> str:
        return self._client.get_version()

    @property
    def os(self) -> OperationSystem:
        return self._client.get_os()

    @property
    def online_users(self) -> OnlineUsers:
        return self._online_users

    def get_streams(self):
        return self._streams

    def find_stream_by_id(self, sid: str):
        for stream in self._streams:
            if stream.id == ObjectId(sid):
                return stream

        return None

    def get_user_role_by_id(self, uid: ObjectId) -> ProviderPair.Roles:
        for user in self._settings.providers:
            if user.user.id == uid:
                return user.role

        return ProviderPair.Roles.READ

    def add_serial(self, serial):
        self._settings.series.append(serial)
        self._settings.save()

    def remove_serial(self, sid: str):
        for ser in self._settings.series:
            if ser.id == ObjectId(sid):
                ser.delete()

    def add_stream(self, stream: IStream):
        self.__init_stream_runtime_fields(stream)
        self._streams.append(stream)
        self._settings.add_stream(stream)  #

    def add_streams(self, streams: [IStream]):
        for stream in streams:
            self.__init_stream_runtime_fields(stream)
            self._streams.append(stream)
        self._settings.add_streams(streams)  #

    def update_stream(self, stream):
        stream.save()

    def remove_stream(self, sid: str):
        for stream in self._streams:
            if stream.id == ObjectId(sid):
                self._client.stop_stream(sid)
                self._streams.remove(stream)
                safe_delete_stream(stream)
                self._settings.remove_stream(stream)  #

    def remove_all_streams(self):
        for stream in self._streams:
            self._client.stop_stream(stream.get_id())
            safe_delete_stream(stream)
        self._streams = []
        self._settings.remove_all_streams()  #

    def stop_all_streams(self):
        for stream in self._streams:
            self._client.stop_stream(stream.get_id())

    def start_all_streams(self):
        for stream in self._streams:
            self._client.start_stream(stream.config())

    def to_dict(self) -> dict:
        return {ServiceFields.ID: str(self.id), ServiceFields.CPU: self._cpu, ServiceFields.GPU: self._gpu,
                ServiceFields.LOAD_AVERAGE: self._load_average, ServiceFields.MEMORY_TOTAL: self._memory_total,
                ServiceFields.MEMORY_FREE: self._memory_free, ServiceFields.HDD_TOTAL: self._hdd_total,
                ServiceFields.HDD_FREE: self._hdd_free, ServiceFields.BANDWIDTH_IN: self._bandwidth_in,
                ServiceFields.BANDWIDTH_OUT: self._bandwidth_out, ServiceFields.VERSION: self.version,
                ServiceFields.UPTIME: self._uptime, ServiceFields.TIMESTAMP: self._timestamp,
                ServiceFields.STATUS: self.status, ServiceFields.ONLINE_USERS: str(self.online_users),
                ServiceFields.OS: str(self.os)}

    def make_serial(self) -> Serial:
        return Serial()

    def make_proxy_stream(self) -> ProxyStream:
        return ProxyStream.make_stream(self._settings)

    def make_proxy_vod(self) -> ProxyStream:
        return ProxyVodStream.make_stream(self._settings)

    def make_relay_stream(self) -> RelayStream:
        return RelayStream.make_stream(self._settings)

    def make_vod_relay_stream(self) -> VodRelayStream:
        return VodRelayStream.make_stream(self._settings)

    def make_cod_relay_stream(self) -> CodRelayStream:
        return CodRelayStream.make_stream(self._settings)

    def make_encode_stream(self) -> EncodeStream:
        return EncodeStream.make_stream(self._settings)

    def make_vod_encode_stream(self) -> VodEncodeStream:
        return VodEncodeStream.make_stream(self._settings)

    def make_event_stream(self) -> VodEncodeStream:
        return EventStream.make_stream(self._settings)

    def make_cod_encode_stream(self) -> CodEncodeStream:
        return CodEncodeStream.make_stream(self._settings)

    def make_timeshift_recorder_stream(self) -> TimeshiftRecorderStream:
        return TimeshiftRecorderStream.make_stream(self._settings)

    def make_catchup_stream(self) -> CatchupStream:
        return CatchupStream.make_stream(self._settings)

    def make_timeshift_player_stream(self) -> TimeshiftPlayerStream:
        return TimeshiftPlayerStream.make_stream(self._settings)

    def make_test_life_stream(self) -> TestLifeStream:
        return TestLifeStream.make_stream(self._settings)

    # handler
    def on_stream_statistic_received(self, params: dict):
        sid = params['id']
        stream = self.find_stream_by_id(sid)
        if stream:
            stream.update_runtime_fields(params)
            self.__notify_front(Service.STREAM_DATA_CHANGED, stream.to_dict())

    def on_stream_sources_changed(self, params: dict):
        pass

    def on_stream_ml_notification(self, params: dict):
        pass

    def on_service_statistic_received(self, params: dict):
        # nid = params['id']
        self.__refresh_stats(params)
        self.__notify_front(Service.SERVICE_DATA_CHANGED, self.to_dict())

    def on_quit_status_stream(self, params: dict):
        sid = params['id']
        stream = self.find_stream_by_id(sid)
        if stream:
            stream.reset()
            self.__notify_front(Service.STREAM_DATA_CHANGED, stream.to_dict())

    def on_client_state_changed(self, status: ClientStatus):
        if status == ClientStatus.ACTIVE:
            self.sync(True)
        else:
            self.__reset()
            for stream in self._streams:
                stream.reset()

    def on_ping_received(self, params: dict):
        self.sync()

    # private
    def __notify_front(self, channel: str, params: dict):
        unique_channel = channel + '_' + str(self.id)
        self._socketio.emit(unique_channel, params)

    def __reset(self):
        self._cpu = Service.INIT_VALUE
        self._gpu = Service.INIT_VALUE
        self._load_average = Service.CALCULATE_VALUE
        self._memory_total = Service.INIT_VALUE
        self._memory_free = Service.INIT_VALUE
        self._hdd_total = Service.INIT_VALUE
        self._hdd_free = Service.INIT_VALUE
        self._bandwidth_in = Service.INIT_VALUE
        self._bandwidth_out = Service.INIT_VALUE
        self._uptime = Service.CALCULATE_VALUE
        self._timestamp = Service.CALCULATE_VALUE
        self._online_users = None

    def __refresh_stats(self, stats: dict):
        self._cpu = stats[ServiceFields.CPU]
        self._gpu = stats[ServiceFields.GPU]
        self._load_average = stats[ServiceFields.LOAD_AVERAGE]
        self._memory_total = stats[ServiceFields.MEMORY_TOTAL]
        self._memory_free = stats[ServiceFields.MEMORY_FREE]
        self._hdd_total = stats[ServiceFields.HDD_TOTAL]
        self._hdd_free = stats[ServiceFields.HDD_FREE]
        self._bandwidth_in = stats[ServiceFields.BANDWIDTH_IN]
        self._bandwidth_out = stats[ServiceFields.BANDWIDTH_OUT]
        self._uptime = stats[ServiceFields.UPTIME]
        self._timestamp = stats[ServiceFields.TIMESTAMP]
        self._online_users = OnlineUsers(**stats[ServiceFields.ONLINE_USERS])

    def __init_stream_runtime_fields(self, stream: IStream):
        stream.set_server_settings(self._settings)

    def __reload_from_db(self):
        self._streams = []
        streams = self._settings.streams
        for stream in streams:
            self.__init_stream_runtime_fields(stream)
            self._streams.append(stream)

    def __refresh_catchups(self):
        for stream in self._streams:
            if stream.get_type() == constants.StreamType.CATCHUP:
                now = datetime.now()
                if stream.start > now and now < stream.stop and not stream.is_started():
                    self._client.start_stream(stream.config())
