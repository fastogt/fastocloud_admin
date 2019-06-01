from mongoengine import EmbeddedDocument, StringField
from app.constants import DEFAULT_LOCALE


class Settings(EmbeddedDocument):
    locale = StringField(default=DEFAULT_LOCALE)
