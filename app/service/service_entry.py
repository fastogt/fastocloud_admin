from mongoengine import Document, ListField, EmbeddedDocumentField, ReferenceField, EmbeddedDocument, IntField

import app.constants as constants

from app.service.server_entry import ServerSettings
from app.stream.stream_entry import Stream


# #EXTM3U
# #EXTINF:-1 tvg-id="" tvg-name="" tvg-logo="https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/Amptv.png/330px-Amptv.png" group-title="Armenia(Հայաստան)",1TV
# http://amtv1.livestreamingcdn.com/am2abr/tracks-v1a1/index.m3u8

class UserPair(EmbeddedDocument):
    user = ReferenceField('User')
    role = IntField(min_value=constants.Roles.READ, max_value=constants.Roles.SUPPORT)


class ServiceSettings(Document, ServerSettings):
    meta = {'collection': 'services', 'auto_create_index': False}

    streams = ListField(EmbeddedDocumentField(Stream), default=[])
    users = ListField(EmbeddedDocumentField(UserPair), default=[])

    def generate_playlist(self) -> str:
        result = '#EXTM3U\n'
        for stream in self.streams:
            type = stream.get_type()
            if type == constants.StreamType.RELAY or type == constants.StreamType.ENCODE \
                    or type == constants.StreamType.TIMESHIFT_PLAYER or type == constants.StreamType.VOD_ENCODE \
                    or type == constants.StreamType.VOD_RELAY:
                for idx, out in enumerate(stream.output.urls):
                    result += '#EXTINF:{0} tvg-id="{1}" tvg-name="" tvg-logo="{3}" group-title="{4}",{2}\n{5}\n'.format(
                        idx,
                        stream.id,
                        stream.name,
                        stream.icon,
                        stream.group,
                        out.uri)

        return result

    def add_user(self, user: UserPair):
        self.users.append(user)
        self.save()

    def remove_user(self, uid):
        for user in self.users:
            if user.id == uid:
                self.users.remove(user)
        self.save()
