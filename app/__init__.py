import os

from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_babel import Babel
from flask_socketio import SocketIO

from app.service.service_manager import ServiceManager


def get_app_folder():
    return os.path.dirname(__file__)


def get_runtime_folder():
    return os.path.join(get_app_folder(), 'runtime_folder')


def get_runtime_stream_folder():
    return os.path.join(get_runtime_folder(), 'stream')


def init_project(static_folder, *args):
    runtime_folder = get_runtime_folder()
    if not os.path.exists(runtime_folder):
        os.mkdir(runtime_folder)

    runtime_stream_folder = get_runtime_stream_folder()
    if not os.path.exists(runtime_stream_folder):
        os.mkdir(runtime_stream_folder)

    app = Flask(__name__, static_folder=static_folder)
    for file in args:
        app.config.from_pyfile(file, silent=False)

    bootstrap = Bootstrap(app)
    babel = Babel(app)
    db = MongoEngine(app)
    mail = Mail(app)
    socketio = SocketIO(app)
    login_manager = LoginManager(app)

    login_manager.login_view = "HomeView:signin"

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

    return app, bootstrap, babel, db, mail, login_manager, servers_manager


app, bootstrap, babel, db, mail, login_manager, servers_manager = init_project(
    'static',
    'config/public_config.py',
    'config/config.py',
    'config/db_config.py',
    'config/mail_config.py'
)

from app.home.view import HomeView
from app.user.view import UserView
from app.stream.view import StreamView
from app.service.view import ServiceView

HomeView.register(app)
UserView.register(app)
StreamView.register(app)
ServiceView.register(app)
