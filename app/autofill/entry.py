from pymodm import MongoModel, fields

import pyfastocloud_models.constants as constants


class M3uParseStreams(MongoModel):
    class Meta:
        collection_name = 'm3uparse_streams'

    name = fields.CharField(max_length=constants.MAX_STREAM_NAME_LENGTH,
                            min_length=constants.MIN_STREAM_NAME_LENGTH,
                            required=True)
    tvg_id = fields.ListField(fields.CharField(), default=[])
    tvg_logo = fields.ListField(fields.CharField(), default=[])
    group = fields.ListField(fields.CharField(), default=[])


class M3uParseVods(MongoModel):
    class Meta:
        collection_name = 'm3uparse_vods'

    name = fields.CharField(max_length=constants.MAX_STREAM_NAME_LENGTH,
                            min_length=constants.MIN_STREAM_NAME_LENGTH,
                            required=True)
    tvg_logo = fields.ListField(fields.CharField(), default=[])
    group = fields.ListField(fields.CharField(), default=[])
