from datetime import datetime
from hashlib import md5
from bson.objectid import ObjectId
from enum import IntEnum

from mongoengine import Document, EmbeddedDocument, StringField, DateTimeField, IntField, ListField, ReferenceField, \
    PULL, ObjectIdField, EmbeddedDocumentField

from app.service.service_entry import ServiceSettings


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
    STREAMS_FIELD = "channels"

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
    devices = ListField(EmbeddedDocumentField(Device), default=[])
    streams = ListField(ObjectIdField(), default=[])

    def add_server(self, server: ServiceSettings):
        self.servers.append(server)
        self.save()

    def add_stream(self, stream):
        self.streams.append(stream.id)
        self.save()

    def remove_stream(self, sid: ObjectId):
        for stream in self.streams:
            if stream == sid:
                self.streams.remove(stream)
                break
        self.save()

    def to_service(self, sid: ObjectId) -> dict:
        for serv in self.servers:
            if serv.id == sid:
                devices = []
                for dev in self.devices:
                    devices.append(str(dev.id))

                streams = []
                for stream in self.streams:
                    founded_stream = serv.find_stream_settings_by_id(stream)
                    if founded_stream:
                        channels = founded_stream.to_channel_info()
                        for ch in channels:
                            streams.append(ch.to_dict())

                conf = {
                    Subscriber.ID_FIELD: str(self.id), Subscriber.EMAIL_FIELD: self.email,
                    Subscriber.PASSWORD_FIELD: self.password, Subscriber.STATUS_FIELD: self.status,
                    Subscriber.DEVICES_FIELD: devices, Subscriber.STREAMS_FIELD: streams}
                return conf

        return {}

    @staticmethod
    def make_md5_hash_from_password(password: str) -> str:
        m = md5()
        m.update(password.encode())
        return m.hexdigest()

    @classmethod
    def md5_user(cls, email: str, password: str, country: str):
        return cls(email=email, password=Subscriber.make_md5_hash_from_password(password), country=country)


Subscriber.register_delete_rule(ServiceSettings, "subscribers", PULL)
