MONGO_DBNAME = 'iptv'
MONGO_URI = 'mongodb://mongodb:27017/' + MONGO_DBNAME

MONGODB_SETTINGS = {
    'db': MONGO_DBNAME,
    'host': MONGO_URI
}

SECRET_KEY = '1d4bb560a7644fa48852a92ce52d6e08'
SERVER_NAME_FOR_POST = '0.0.0.0:8080'
PREFERRED_URL_SCHEME = 'http'

BOOTSTRAP_SERVE_LOCAL = True
