from flask_wtf import FlaskForm
from flask_babel import lazy_gettext

from wtforms.fields import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import InputRequired, Length, Email

from app.subscriber.subscriber_entry import Subscriber


class SubscriberForm(FlaskForm):
    AVAILABLE_COUNTRIES = [('UK', 'United kingdom'), ('RU', 'Russian'), ('BY', 'Belarus')]
    email = StringField(lazy_gettext(u'Email:'),
                        validators=[InputRequired(), Email(message=lazy_gettext(u'Invalid email')), Length(max=30)])
    password = PasswordField(lazy_gettext(u'Password:'), validators=[InputRequired(), Length(min=4, max=80)])
    country = SelectField(lazy_gettext(u'Locale:'), coerce=str, validators=[InputRequired()],
                          choices=AVAILABLE_COUNTRIES)
    apply = SubmitField(lazy_gettext(u'Apply'))

    def make_entry(self):
        return self.update_entry(Subscriber())

    def update_entry(self, subscriber: Subscriber):
        subscriber.email = self.email.data
        subscriber.password = Subscriber.make_md5_hash_from_password(self.password.data)
        subscriber.country = self.country.data
        return subscriber
