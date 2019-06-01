from mongoengine import StringField, IntField, EmbeddedDocumentField

import app.constants as constants
from app.common_entries import HostAndPort


class ServerSettings:
    DEFAULT_SERVICE_NAME = 'Service'
    MIN_SERVICE_NAME_LENGTH = 3
    MAX_SERVICE_NAME_LENGTH = 30

    DEFAULT_FEEDBACK_DIR_PATH = constants.DEFAULT_SERVICE_ROOT_DIR_PATH + '/feedback'
    DEFAULT_TIMESHIFTS_DIR_PATH = constants.DEFAULT_SERVICE_ROOT_DIR_PATH + '/timeshifts'
    DEFAULT_HLS_DIR_PATH = constants.DEFAULT_SERVICE_ROOT_DIR_PATH + '/hls'
    DEFAULT_PLAYLISTS_DIR_PATH = constants.DEFAULT_SERVICE_ROOT_DIR_PATH + '/playlists'
    DEFAULT_DVB_DIR_PATH = constants.DEFAULT_SERVICE_ROOT_DIR_PATH + '/dvb'
    DEFAULT_CAPTURE_DIR_PATH = constants.DEFAULT_SERVICE_ROOT_DIR_PATH + '/capture_card'
    DEFAULT_VODS_IN_DIR_PATH = constants.DEFAULT_SERVICE_ROOT_DIR_PATH + '/vods_in'
    DEFAULT_VODS_DIR_PATH = constants.DEFAULT_SERVICE_ROOT_DIR_PATH + '/vods'

    DEFAULT_SERVICE_HOST = 'localhost'
    DEFAULT_SERVICE_PORT = 6317
    DEFAULT_SERVICE_HTTP_HOST = 'localhost'
    DEFAULT_SERVICE_HTTP_PORT = 8000
    DEFAULT_SERVICE_VODS_HOST = 'localhost'
    DEFAULT_SERVICE_VODS_PORT = 7000

    name = StringField(unique=True, default=DEFAULT_SERVICE_NAME, max_length=MAX_SERVICE_NAME_LENGTH,
                       min_length=MIN_SERVICE_NAME_LENGTH)
    host = EmbeddedDocumentField(HostAndPort, default=HostAndPort(host=DEFAULT_SERVICE_HOST, port=DEFAULT_SERVICE_PORT))
    http_host = EmbeddedDocumentField(HostAndPort, default=HostAndPort(host=DEFAULT_SERVICE_HTTP_HOST,
                                                                       port=DEFAULT_SERVICE_HTTP_PORT))
    vods_host = EmbeddedDocumentField(HostAndPort, default=HostAndPort(host=DEFAULT_SERVICE_VODS_HOST,
                                                                       port=DEFAULT_SERVICE_VODS_PORT))

    feedback_directory = StringField(default=DEFAULT_FEEDBACK_DIR_PATH)
    timeshifts_directory = StringField(default=DEFAULT_TIMESHIFTS_DIR_PATH)
    hls_directory = StringField(default=DEFAULT_HLS_DIR_PATH)
    playlists_directory = StringField(default=DEFAULT_PLAYLISTS_DIR_PATH)
    dvb_directory = StringField(default=DEFAULT_DVB_DIR_PATH)
    capture_card_directory = StringField(default=DEFAULT_CAPTURE_DIR_PATH)
    vods_in_directory = StringField(default=DEFAULT_VODS_IN_DIR_PATH)
    vods_directory = StringField(default=DEFAULT_VODS_DIR_PATH)

    def get_host(self) -> str:
        return str(self.host)

    def get_http_host(self) -> str:
        return 'http://{0}'.format(str(self.http_host))

    def get_vods_host(self) -> str:
        return 'http://{0}'.format(str(self.vods_host))

    def generate_http_link(self, url: str) -> str:
        return url.replace(self.hls_directory, self.get_http_host())

    def generate_vods_link(self, url: str) -> str:
        return url.replace(self.vods_directory, self.get_vods_host())
