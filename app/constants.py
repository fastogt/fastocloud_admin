from enum import IntEnum


class StreamType(IntEnum):
    RELAY = 0
    ENCODE = 1
    TIMESHIFT_PLAYER = 2
    TIMESHIFT_RECORDER = 3
    CATCHUP = 4
    TEST_LIFE = 5,
    VOD_RELAY = 6,
    VOD_ENCODE = 7

    @classmethod
    def choices(cls):
        return [(choice, choice.name) for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls(int(item)) if not isinstance(item, cls) else item

    def __str__(self):
        return str(self.value)


class StreamStatus(IntEnum):
    NEW = 0
    INIT = 1
    STARTED = 2
    READY = 3
    PLAYING = 4
    FROZEN = 5
    WAITING = 6


class StreamLogLevel(IntEnum):
    LOG_LEVEL_EMERG = 0
    LOG_LEVEL_ALERT = 1
    LOG_LEVEL_CRIT = 2
    LOG_LEVEL_ERR = 3
    LOG_LEVEL_WARNING = 4
    LOG_LEVEL_NOTICE = 5
    LOG_LEVEL_INFO = 6
    LOG_LEVEL_DEBUG = 7

    @classmethod
    def choices(cls):
        return [(choice, choice.name) for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls(int(item)) if not isinstance(item, cls) else item

    def __str__(self):
        return str(self.value)


MIN_URL_LENGTH = 3
MAX_URL_LENGTH = 1023
MIN_PATH_LENGTH = 1
MAX_PATH_LENGTH = 255

PRECISION = 2

DATE_JS_FORMAT = '%m/%d/%Y %H:%M:%S'

DEFAULT_HLS_PLAYLIST = 'master.m3u8'
DEFAULT_LOCALE = 'en'
AVAILABLE_LOCALES = DEFAULT_LOCALE, 'ru'
AVAILABLE_LOCALES_PAIRS = [(DEFAULT_LOCALE, 'English'), ('ru', 'Russian')]

AVAILABLE_STREAM_TYPES_PAIRS = [(StreamType.RELAY, 'relay'), (StreamType.ENCODE, 'encode'),
                                (StreamType.TIMESHIFT_PLAYER, 'timeshift_player'),
                                (StreamType.TIMESHIFT_RECORDER, 'timeshift_record'), (StreamType.CATCHUP, 'catchup'),
                                (StreamType.TEST_LIFE, 'test_life'), (StreamType.VOD_RELAY, 'vod_relay'),
                                (StreamType.VOD_ENCODE, 'vod_encode')]
AVAILABLE_LOG_LEVELS_PAIRS = [(StreamLogLevel.LOG_LEVEL_EMERG, 'EVERG'), (StreamLogLevel.LOG_LEVEL_ALERT, 'ALERT'),
                              (StreamLogLevel.LOG_LEVEL_CRIT, 'CRITICAL'),
                              (StreamLogLevel.LOG_LEVEL_ERR, 'ERROR'),
                              (StreamLogLevel.LOG_LEVEL_WARNING, 'WARNING'),
                              (StreamLogLevel.LOG_LEVEL_NOTICE, 'NOTICE'),
                              (StreamLogLevel.LOG_LEVEL_INFO, 'INFO'),
                              (StreamLogLevel.LOG_LEVEL_DEBUG, 'DEBUG')]

INVALID_AUDIO_SELECT = -1
DEFAULT_LOOP = False
DEFAULT_AVFORMAT = False
DEFAULT_HAVE_VIDEO = True
DEFAULT_HAVE_AUDIO = True
DEFAULT_RELAY_VIDEO = False
DEFAULT_RELAY_AUDIO = False
DEFAULT_DEINTERLACE = False
MIN_FRAME_RATE = 1
INVALID_FRAME_RATE = 0
MAX_FRAME_RATE = 100
MIN_VOLUME = 0
DEFAULT_VOLUME = 1
MAX_VOLUME = 10
MIN_AUDIO_CHANNELS_COUNT = 1
INVALID_AUDIO_CHANNELS_COUNT = 0
MAX_AUDIO_CHANNELS_COUNT = 8
INVALID_WIDTH = 0
INVALID_HEIGHT = 0
INVALID_VIDEO_BIT_RATE = 0
INVALID_AUDIO_BIT_RATE = 0
MIN_ALPHA = 0
MAX_ALPHA = 1
DEFAULT_LOGO_ALPHA = MAX_ALPHA
DEFAULT_LOGO_X = 0
DEFAULT_LOGO_Y = 0
INVALID_LOGO_PATH = str()
INVALID_RATIO_NUM = 0
INVALID_RATIO_DEN = 0
DEFAULT_AUTO_EXIT_TIME = 0
DEFAULT_RESTART_ATTEMPTS = 10
MIN_TIMESHIFT_CHUNK_DURATION = 1
DEFAULT_TIMESHIFT_CHUNK_DURATION = 120
DEFAULT_CATCHUP_CHUNK_DURATION = 12
DEFAULT_CATCHUP_EXIT_TIME = 3600
MAX_TIMESHIFT_CHUNK_DURATION = 600
MIN_TIMESHIFT_CHUNK_LIFE_TIME = 1
DEFAULT_TIMESHIFT_CHUNK_LIFE_TIME = 12 * 3600
MAX_TIMESHIFT_CHUNK_LIFE_TIME = 30 * 12 * 3600
MIN_TIMESHIFT_DELAY = MIN_TIMESHIFT_CHUNK_LIFE_TIME
DEFAULT_TIMESHIFT_DELAY = 3600
MAX_TIMESHIFT_DELAY = MAX_TIMESHIFT_CHUNK_LIFE_TIME

TS_VIDEO_PARSER = 'tsparse'
H264_VIDEO_PARSER = 'h264parse'
H265_VIDEO_PARSER = 'h265parse'
DEFAULT_VIDEO_PARSER = H264_VIDEO_PARSER

AAC_AUDIO_PARSER = 'aacparse'
AC3_AUDIO_PARSER = 'ac3parse'
MPEG_AUDIO_PARSER = 'mpegaudioparse'
DEFAULT_AUDIO_PARSER = AAC_AUDIO_PARSER

AVAILABLE_VIDEO_PARSERS = [(TS_VIDEO_PARSER, 'ts'), (H264_VIDEO_PARSER, 'h264'), (H265_VIDEO_PARSER, 'h265')]
AVAILABLE_AUDIO_PARSERS = [(MPEG_AUDIO_PARSER, 'mpeg'), (AAC_AUDIO_PARSER, 'aac'), (AC3_AUDIO_PARSER, 'ac3')]

EAVC_ENC = 'eavcenc'
OPEN_H264_ENC = 'openh264enc'
X264_ENC = 'x264enc'
NV_H264_ENC = 'nvh264enc'
VAAPI_H264_ENC = 'vaapih264enc'
VAAPI_MPEG2_ENC = 'vaapimpeg2enc'
MFX_H264_ENC = 'mfxh264enc'
X265_ENC = 'x265enc'
MSDK_H264_ENC = 'msdkh264enc'
DEFAULT_VIDEO_CODEC = X264_ENC

LAME_MP3_ENC = 'lamemp3enc'
FAAC = 'faac'
VOAAC_ENC = 'voaacenc'
DEFAULT_AUDIO_CODEC = FAAC

AVAILABLE_VIDEO_CODECS = [(EAVC_ENC, 'eav'), (OPEN_H264_ENC, 'openh264'), (X264_ENC, 'x264'), (NV_H264_ENC, 'nvh264'),
                          (VAAPI_H264_ENC, 'vaapih264'), (VAAPI_MPEG2_ENC, 'vaapimpeg2'), (MFX_H264_ENC, 'mfxh264'),
                          (X265_ENC, 'x265'), (MSDK_H264_ENC, 'msdkh264')]
AVAILABLE_AUDIO_CODECS = [(LAME_MP3_ENC, 'mpe'), (FAAC, 'aac'), (VOAAC_ENC, 'voaac')]

DEFAULT_SERVICE_ROOT_DIR_PATH = '~/streamer'
DEFAULT_SERVICE_LOG_PATH_TEMPLATE_3SIS = 'http://{0}:{1}/service/log/{2}'
DEFAULT_STREAM_LOG_PATH_TEMPLATE_3SIS = 'http://{0}:{1}/stream/log/{2}'
DEFAULT_STREAM_PIPELINE_PATH_TEMPLATE_3SIS = 'http://{0}:{1}/stream/pipeline/{2}'

DEFAULT_TEST_URL = 'test'

DEFAULT_STREAM_NAME = 'Stream'
DEFAULT_STREAM_ICON_URL = 'https://fastocloud.com/static/images/unknown_channel.png'
DEFAULT_STREAM_GROUP_TITLE = 'FastoTV'
MIN_STREAM_NAME_LENGTH = 1
MAX_STREAM_NAME_LENGTH = 64
MIN_STREAM_GROUP_TITLE = 1
MAX_STREAM_GROUP_TITLE = 64


def round_value(value: float):
    return round(value, PRECISION)


class Roles(IntEnum):
    READ = 0
    WRITE = 1
    ADMIN = 2
    SUPPORT = 3

    @classmethod
    def choices(cls):
        return [(choice, choice.name) for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls(int(item)) if not isinstance(item, cls) else item

    def __str__(self):
        return str(self.value)


class UserAgent(IntEnum):
    GSTREAMER = 0
    VLC = 1

    @classmethod
    def choices(cls):
        return [(choice, choice.name) for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls(int(item)) if not isinstance(item, cls) else item

    def __str__(self):
        return str(self.value)


AVAILABLE_USER_AGENTS = [(UserAgent.GSTREAMER, 'GStreamer'), (UserAgent.VLC, 'VLC'), ]
