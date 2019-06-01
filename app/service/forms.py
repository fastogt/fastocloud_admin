from flask_wtf import FlaskForm
from flask_babel import lazy_gettext
from wtforms.fields import StringField, SubmitField, FileField, SelectField, FormField
from wtforms.validators import InputRequired, Length

from app.common_forms import HostAndPortForm
from app.service.service_entry import ServiceSettings
from app.constants import StreamType


class ServiceSettingsForm(FlaskForm):
    name = StringField(lazy_gettext(u'Name:'), validators=[InputRequired()])
    host = FormField(HostAndPortForm, lazy_gettext(u'Host:'), validators=[])
    http_host = FormField(HostAndPortForm, lazy_gettext(u'Http host:'), validators=[])
    vods_host = FormField(HostAndPortForm, lazy_gettext(u'Vods host:'), validators=[])

    feedback_directory = StringField(lazy_gettext(u'Feedback directory:'), validators=[InputRequired()])
    timeshifts_directory = StringField(lazy_gettext(u'Timeshifts directory:'), validators=[InputRequired()])
    hls_directory = StringField(lazy_gettext(u'Hls directory:'), validators=[InputRequired()])
    playlists_directory = StringField(lazy_gettext(u'Playlist directory:'), validators=[InputRequired()])
    dvb_directory = StringField(lazy_gettext(u'DVB directory:'), validators=[InputRequired()])
    capture_card_directory = StringField(lazy_gettext(u'Capture card directory:'), validators=[InputRequired()])
    vods_in_directory = StringField(lazy_gettext(u'Vods in directory:'), validators=[InputRequired()])
    vods_directory = StringField(lazy_gettext(u'Vods out directory:'), validators=[InputRequired()])
    apply = SubmitField(lazy_gettext(u'Apply'))

    def make_entry(self):
        return self.update_entry(ServiceSettings())

    def update_entry(self, settings: ServiceSettings):
        settings.name = self.name.data
        settings.host = self.host.get_data()
        settings.http_host = self.http_host.get_data()
        settings.vods_host = self.vods_host.get_data()

        settings.feedback_directory = self.feedback_directory.data
        settings.timeshifts_directory = self.timeshifts_directory.data
        settings.hls_directory = self.hls_directory.data
        settings.playlists_directory = self.playlists_directory.data
        settings.dvb_directory = self.dvb_directory.data
        settings.capture_card_directory = self.capture_card_directory.data
        return settings


class ActivateForm(FlaskForm):
    LICENSE_KEY_LENGTH = 64

    license = StringField(lazy_gettext(u'License:'),
                          validators=[InputRequired(), Length(min=LICENSE_KEY_LENGTH, max=LICENSE_KEY_LENGTH)])
    submit = SubmitField(lazy_gettext(u'Activate'))


class UploadM3uForm(FlaskForm):
    AVAILABLE_STREAM_TYPES_FOR_UPLOAD = [(StreamType.RELAY, 'Relay'), (StreamType.ENCODE, 'Encode'),
                                         (StreamType.CATCHUP, 'Catchup'), (StreamType.TEST_LIFE, 'Test life'),
                                         (StreamType.VOD_RELAY, 'Vod relay'), (StreamType.VOD_ENCODE, 'Vod encode')]

    file = FileField()
    type = SelectField(lazy_gettext(u'Type:'), coerce=StreamType.coerce, validators=[InputRequired()],
                       choices=AVAILABLE_STREAM_TYPES_FOR_UPLOAD)
    submit = SubmitField(lazy_gettext(u'Upload'))
