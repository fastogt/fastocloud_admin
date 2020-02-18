from pymodm import MongoModel, fields

import pyfastocloud_models.constants as constants


class M3uParseStreams(MongoModel):
    class Meta:
        collection_name = 'm3uparse_streams'

    def to_dict(self) -> dict:
        return {'id': str(self.id), 'name': self.name, 'epgid': self.tvg_id, 'logo': self.tvg_logo, 'group': self.group}

    @property
    def id(self):
        return self.pk

    name = fields.CharField(max_length=constants.MAX_STREAM_NAME_LENGTH,
                            min_length=constants.MIN_STREAM_NAME_LENGTH,
                            required=True)
    tvg_id = fields.ListField(fields.CharField(), default=[])
    tvg_logo = fields.ListField(fields.CharField(), default=[])
    group = fields.ListField(fields.CharField(), default=[])


class M3uParseVods(MongoModel):
    class Meta:
        collection_name = 'm3uparse_vods'

    def to_dict(self) -> dict:
        return {'id': str(self.id), 'name': self.name, 'logo': self.tvg_logo, 'group': self.group}

    @property
    def id(self):
        return self.pk

    name = fields.CharField(max_length=constants.MAX_STREAM_NAME_LENGTH,
                            min_length=constants.MIN_STREAM_NAME_LENGTH,
                            required=True)
    tvg_logo = fields.ListField(fields.CharField(), default=[])
    group = fields.ListField(fields.CharField(), default=[])
