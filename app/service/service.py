from bson.objectid import ObjectId

from app.stream.stream_entry import Stream, EncodeStream, RelayStream, TimeshiftRecorderStream, CatchupStream, \
    TimeshiftPlayerStream, TestLifeStream, make_encode_stream, make_relay_stream, make_timeshift_recorder_stream, \
    make_catchup_stream, make_timeshift_player_stream, make_test_life_stream, make_vod_encode_stream, \
    make_vod_relay_stream
from app.client.client_constants import ClientStatus

from app.service.service_entry import ServiceSettings
from app.service.service_client import ServiceClient
from app.service.stream_handler import IStreamHandler
import app.constants as constants


class ServiceFields:
    ID = 'id'
    CPU = 'cpu'
    GPU = 'gpu'
    LOAD_AVERAGE = 'load_average'
    MEMORY_TOTAL = 'memory_total'
    MEMORY_FREE = 'memory_free'
    MEMORY_AVAILABLE = 'memory_available'
    HDD_TOTAL = 'hdd_total'
    HDD_FREE = 'hdd_free'
    BANDWIDTH_IN = 'bandwidth_in'
    BANDWIDTH_OUT = 'bandwidth_out'
    VERSION = 'version'
    UPTIME = 'uptime'
    TIMESTAMP = 'timestamp'
    STATUS = 'status'


class Service(IStreamHandler):
    STREAM_DATA_CHANGED = 'stream_data_changed'
    SERVICE_DATA_CHANGED = 'service_data_changed'
    CALCULATE_VALUE = None

    # runtime
    _cpu = CALCULATE_VALUE
    _gpu = CALCULATE_VALUE
    _load_average = CALCULATE_VALUE
    _memory_total = CALCULATE_VALUE
    _memory_free = CALCULATE_VALUE
    _memory_available = CALCULATE_VALUE
    _hdd_total = CALCULATE_VALUE
    _hdd_free = CALCULATE_VALUE
    _bandwidth_in = CALCULATE_VALUE
    _bandwidth_out = CALCULATE_VALUE
    _uptime = CALCULATE_VALUE
    _timestamp = CALCULATE_VALUE
    _streams = []

    def __init__(self, host, port, socketio, settings: ServiceSettings):
        self._settings = settings
        self.__reload_from_db()
        # other fields
        self._client = ServiceClient(self, settings)
        self._host = host
        self._port = port
        self._socketio = socketio

    def connect(self):
        return self._client.connect()

    def disconnect(self):
        return self._client.disconnect()

    def stop(self, delay: int):
        return self._client.stop_service(delay)

    def get_log_service(self):
        return self._client.get_log_service(self._host, self._port, self.id)

    def ping(self):
        return self._client.ping_service()

    def activate(self, license_key: str):
        return self._client.activate(license_key)

    def sync(self):
        return self._client.sync_service()

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
    def id(self) -> str:
        return str(self._settings.id)

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
    def memory_available(self):
        return self._memory_available

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
    def version(self):
        return self._client.get_version()

    def get_streams(self):
        return self._streams

    def find_stream_by_id(self, sid: str):
        for stream in self._streams:
            if stream.id == ObjectId(sid):
                return stream

        return None

    def get_user_role_by_id(self, uid: ObjectId) -> constants.Roles:
        for user in self._settings.users:
            if user.user.id == uid:
                return user.role

        return constants.Roles.READ

    def add_stream(self, stream):
        self.__init_stream_runtime_fields(stream)
        stream.fixup_output_urls()
        self._streams.append(stream)
        self._settings.streams.append(stream)
        self._settings.save()

    def update_stream(self, stream):
        stream.fixup_output_urls()
        stream.save()

    def remove_stream(self, sid: str):
        for stream in self._streams:
            if stream.id == ObjectId(sid):
                for set_stream in self._settings.streams:
                    if set_stream.id == stream.id:
                        self._settings.streams.remove(set_stream)
                        break
                self._settings.save()
                self._streams.remove(stream)
                break

    def to_front(self) -> dict:
        return {ServiceFields.ID: self.id, ServiceFields.CPU: self._cpu, ServiceFields.GPU: self._gpu,
                ServiceFields.LOAD_AVERAGE: self._load_average, ServiceFields.MEMORY_TOTAL: self._memory_total,
                ServiceFields.MEMORY_FREE: self._memory_free, ServiceFields.MEMORY_AVAILABLE: self._memory_available,
                ServiceFields.HDD_TOTAL: self._hdd_total, ServiceFields.HDD_FREE: self._hdd_free,
                ServiceFields.BANDWIDTH_IN: self._bandwidth_in, ServiceFields.BANDWIDTH_OUT: self._bandwidth_out,
                ServiceFields.VERSION: self.version, ServiceFields.UPTIME: self._uptime,
                ServiceFields.TIMESTAMP: self._timestamp, ServiceFields.STATUS: self.status}

    def make_relay_stream(self) -> RelayStream:
        return make_relay_stream(self._settings)

    def make_vod_relay_stream(self) -> RelayStream:
        return make_vod_relay_stream(self._settings)

    def make_encode_stream(self) -> EncodeStream:
        return make_encode_stream(self._settings)

    def make_vod_encode_stream(self) -> EncodeStream:
        return make_vod_encode_stream(self._settings)

    def make_timeshift_recorder_stream(self) -> TimeshiftRecorderStream:
        return make_timeshift_recorder_stream(self._settings)

    def make_catchup_stream(self) -> CatchupStream:
        return make_catchup_stream(self._settings)

    def make_timeshift_player_stream(self) -> TimeshiftPlayerStream:
        return make_timeshift_player_stream(self._settings)

    def make_test_life_stream(self) -> TestLifeStream:
        return make_test_life_stream(self._settings)

    # handler
    def on_stream_statistic_received(self, params: dict):
        sid = params['id']
        stream = self.find_stream_by_id(sid)
        if stream:
            stream.update_runtime_fields(params)
            self.__notify_front(Service.STREAM_DATA_CHANGED, stream.to_front())

    def on_stream_sources_changed(self, params: dict):
        pass

    def on_service_statistic_received(self, params: dict):
        # nid = params['id']
        self.__refresh_stats(params)
        self.__notify_front(Service.SERVICE_DATA_CHANGED, self.to_front())

    def on_quit_status_stream(self, params: dict):
        sid = params['id']
        stream = self.find_stream_by_id(sid)
        if stream:
            stream.reset()
            self.__notify_front(Service.STREAM_DATA_CHANGED, stream.to_front())

    def on_client_state_changed(self, status: ClientStatus):
        if status == ClientStatus.ACTIVE:
            pass
        else:
            self.__reset()
            for stream in self._streams:
                stream.reset()

    # private
    def __notify_front(self, channel: str, params: dict):
        self._socketio.emit(channel, params)

    def __reset(self):
        self._cpu = Service.CALCULATE_VALUE
        self._gpu = Service.CALCULATE_VALUE
        self._load_average = Service.CALCULATE_VALUE
        self._memory_total = Service.CALCULATE_VALUE
        self._memory_free = Service.CALCULATE_VALUE
        self._memory_available = Service.CALCULATE_VALUE
        self._hdd_total = Service.CALCULATE_VALUE
        self._hdd_free = Service.CALCULATE_VALUE
        self._bandwidth_in = Service.CALCULATE_VALUE
        self._bandwidth_out = Service.CALCULATE_VALUE
        self._uptime = Service.CALCULATE_VALUE
        self._timestamp = Service.CALCULATE_VALUE

    def __refresh_stats(self, stats: dict):
        self._cpu = stats[ServiceFields.CPU]
        self._gpu = stats[ServiceFields.GPU]
        self._load_average = stats[ServiceFields.LOAD_AVERAGE]
        self._memory_total = stats[ServiceFields.MEMORY_TOTAL]
        self._memory_free = stats[ServiceFields.MEMORY_FREE]
        self._memory_available = stats[ServiceFields.MEMORY_AVAILABLE]
        self._hdd_total = stats[ServiceFields.HDD_TOTAL]
        self._hdd_free = stats[ServiceFields.HDD_FREE]
        self._bandwidth_in = stats[ServiceFields.BANDWIDTH_IN]
        self._bandwidth_out = stats[ServiceFields.BANDWIDTH_OUT]
        self._uptime = stats[ServiceFields.UPTIME]
        self._timestamp = stats[ServiceFields.TIMESTAMP]

    def __init_stream_runtime_fields(self, stream: Stream):
        stream.set_server_settings(self._settings)

    def __reload_from_db(self):
        self._streams = []
        streams = self._settings.streams
        for stream in streams:
            self.__init_stream_runtime_fields(stream)
            self._streams.append(stream)
