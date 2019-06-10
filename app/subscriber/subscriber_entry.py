from datetime import datetime
from hashlib import md5
from bson.objectid import ObjectId
from enum import IntEnum

from mongoengine import Document, EmbeddedDocument, StringField, DateTimeField, IntField, ListField, ReferenceField, \
    PULL, ObjectIdField

from app.service.service_entry import ServiceSettings
from app.stream.stream_entry import Stream


class Device(EmbeddedDocument):
    DEFAULT_DEVICE_NAME = 'Device'
    MIN_DEVICE_NAME_LENGTH = 3
    MAX_DEVICE_NAME_LENGTH = 32

    meta = {'allow_inheritance': False, 'auto_create_index': True}
    id = ObjectIdField(required=True, default=ObjectId, unique=True, primary_key=True)
    created_date = DateTimeField(default=datetime.now)
    name = StringField(default=DEFAULT_DEVICE_NAME, min_length=MIN_DEVICE_NAME_LENGTH,
                       max_length=MAX_DEVICE_NAME_LENGTH,
                       required=True)


class Subscriber(Document):
    ID_FIELD = "id"
    EMAIL_FIELD = "login"
    PASSWORD_FIELD = "password"
    STATUS_FIELD = "status"
    DEVICES_FIELD = "devices"
    STREAMS_FIELD = "streams"

    class Status(IntEnum):
        NO_ACTIVE = 0
        ACTIVE = 1
        BANNED = 2

    class Type(IntEnum):
        USER = 0,
        SUPPORT = 1

    SUBSCRIBER_HASH_LENGHT = 32

    meta = {'collection': 'subscribers', 'auto_create_index': False}

    email = StringField(max_length=30, required=True)
    password = StringField(min_length=SUBSCRIBER_HASH_LENGHT, max_length=SUBSCRIBER_HASH_LENGHT, required=True)
    created_date = DateTimeField(default=datetime.now)
    status = IntField(default=Status.ACTIVE)
    type = IntField(default=Type.USER)
    country = StringField(min_length=2, max_length=3, required=True)
    servers = ListField(ReferenceField(ServiceSettings, reverse_delete_rule=PULL), default=[])
    devices = ListField(Device, default=[])
    streams = ListField(ReferenceField(Stream, reverse_delete_rule=PULL), default=[])

    def add_server(self, server: ServiceSettings):
        self.servers.append(server)
        self.save()

    def add_stream(self, sid):
        self.streams.append(sid)
        self.save()

    def remove_stream(self, sid):
        for stream in self.streams:
            if stream == sid:
                self.streams.remove(stream)
                break
        self.save()

    def to_service(self) -> dict:
        devices = []
        for dev in self.devices:
            devices.append(str(dev.id))

        streams = []
        for stream in self.streams:
            streams.append(str(stream))

        conf = {
            Subscriber.ID_FIELD: str(self.id), Subscriber.EMAIL_FIELD: self.email,
            Subscriber.PASSWORD_FIELD: self.password, Subscriber.STATUS_FIELD: self.status,
            Subscriber.DEVICES_FIELD: devices, Subscriber.STREAMS_FIELD: streams}
        return conf

    @staticmethod
    def make_md5_hash_from_password(password: str) -> str:
        m = md5()
        m.update(password.encode())
        return m.hexdigest()

    @classmethod
    def md5_user(cls, email: str, password: str, country: str):
        return cls(email=email, password=Subscriber.make_md5_hash_from_password(password), country=country)


Subscriber.register_delete_rule(ServiceSettings, "subscribers", PULL)
