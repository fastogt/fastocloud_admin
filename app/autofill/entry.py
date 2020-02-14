from mongoengine import Document, StringField, ListField

import pyfastocloud_models.constants as constants


class M3uParse(Document):
    NAME_FIELD = 'name'

    meta = {'allow_inheritance': False, 'collection': 'm3uparse', 'auto_create_index': False}
    name = StringField(unique=True, max_length=constants.MAX_STREAM_NAME_LENGTH,
                       min_length=constants.MIN_STREAM_NAME_LENGTH,
                       required=True)
    tvg_id = ListField(StringField(unique=True), default=[])
    tvg_logo = ListField(StringField(unique=True), default=[])
    group = ListField(StringField(unique=True), default=[])
