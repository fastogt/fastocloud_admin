import os

from omdb import OMDBClient

from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
from werkzeug.middleware.proxy_fix import ProxyFix

from app.service.service_manager import ServiceManager


def get_app_folder():
    return os.path.dirname(__file__)


def get_runtime_folder():
    return os.path.join(get_app_folder(), 'runtime_folder')


def get_runtime_stream_folder():
    return os.path.join(get_runtime_folder(), 'stream')


def get_epg_tmp_folder():
    return os.path.join(get_runtime_folder(), 'epg')


def init_project(static_folder, *args):
    runtime_folder = get_runtime_folder()
    if not os.path.exists(runtime_folder):
        os.mkdir(runtime_folder)

    runtime_stream_folder = get_runtime_stream_folder()
    if not os.path.exists(runtime_stream_folder):
        os.mkdir(runtime_stream_folder)

    epg_tmp_folder = get_epg_tmp_folder()
    if not os.path.exists(epg_tmp_folder):
        os.mkdir(epg_tmp_folder)

    app = Flask(__name__, static_folder=static_folder)
    for file in args:
        app.config.from_pyfile(file, silent=False)

    app.wsgi_app = ProxyFix(app.wsgi_app)
    bootstrap = Bootstrap(app)
    db = MongoEngine(app)
    mail = Mail(app)
    socketio = SocketIO(app)
    login_manager = LoginManager(app)

    login_manager.login_view = 'HomeView:signin'

    # socketio
    @socketio.on('connect')
    def connect():
        pass

    @socketio.on('disconnect')
    def disconnect():
        pass

    # defaults flask
    _host = '0.0.0.0'
    _port = 8080
    server_name = app.config.get('SERVER_NAME_FOR_POST')
    sn_host, sn_port = None, None

    if server_name:
        sn_host, _, sn_port = server_name.partition(':')

    host = sn_host or _host
    port = int(sn_port or _port)
    servers_manager = ServiceManager(host, port, socketio)

    omdb_api_key = app.config.get('OMDB_KEY')
    omdb = OMDBClient(apikey=omdb_api_key)

    return app, bootstrap, db, mail, login_manager, servers_manager, omdb


app, bootstrap, db, mail, login_manager, servers_manager, omdb = init_project(
    'static',
    'config/public_config.py',
    'config/config.py',
    'config/db_config.py',
    'config/mail_config.py'
)

from app.home.view import HomeView
from app.provider.view import ProviderView
from app.stream.view import StreamView
from app.service.view import ServiceView
from app.subscriber.view import SubscriberView
from app.autofill.view import M3uParseStreamsView
from app.epg.view import EpgView

HomeView.register(app)
ProviderView.register(app)
StreamView.register(app)
ServiceView.register(app)
SubscriberView.register(app)
M3uParseStreamsView.register(app)
EpgView.register(app)
