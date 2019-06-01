from flask_wtf import FlaskForm
from flask_babel import lazy_gettext

from wtforms.fields import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Length, Email

import app.constants as constants
from app.home.settings import Settings


class SettingsForm(FlaskForm):
    locale = SelectField(lazy_gettext(u'Locale:'), coerce=str, validators=[InputRequired()],
                         choices=constants.AVAILABLE_LOCALES_PAIRS)
    submit = SubmitField(lazy_gettext(u'Apply'))

    def make_settings(self):
        return self.update_settings(Settings())

    def update_settings(self, settings: Settings):
        settings.locale = self.locale.data
        return settings


class SignupForm(FlaskForm):
    email = StringField(lazy_gettext(u'Email:'),
                        validators=[InputRequired(), Email(message=lazy_gettext(u'Invalid email')), Length(max=30)])
    password = PasswordField(lazy_gettext(u'Password:'), validators=[InputRequired(), Length(min=6, max=80)])
    submit = SubmitField(lazy_gettext(u'Sign Up'))


class SigninForm(FlaskForm):
    email = StringField(lazy_gettext(u'Email:'),
                        validators=[InputRequired(), Email(message=lazy_gettext(u'Invalid email')), Length(max=30)])
    password = PasswordField(lazy_gettext(u'Password:'), validators=[InputRequired(), Length(min=6, max=80)])
    submit = SubmitField(lazy_gettext(u'Sign In'))


class ContactForm(FlaskForm):
    email = StringField(lazy_gettext(u'Email:'),
                        validators=[InputRequired(), Email(message=lazy_gettext(u'Please enter your email address.')),
                                    Length(max=30)])
    subject = StringField(lazy_gettext(u'Subject:'),
                          validators=[InputRequired('Please enter a subject.'), Length(min=1, max=80)])
    message = TextAreaField(lazy_gettext(u'Message:'), validators=[InputRequired(message=lazy_gettext(
        u'Please enter a message.')), Length(min=1, max=500)])
    submit = SubmitField(lazy_gettext(u'Send'))
