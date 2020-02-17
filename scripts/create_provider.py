#!/usr/bin/env python3
import argparse
import os
import sys
from pymodm import connect

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.home.entry import ProviderAdminUser

PROJECT_NAME = 'create_provider'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=PROJECT_NAME, usage='%(prog)s [options]')
    parser.add_argument('--mongo_uri', help='MongoDB credentials', default='mongodb://localhost:27017/iptv')
    parser.add_argument('--email', help='Provider email')
    parser.add_argument('--password', help='Provider password')
    parser.add_argument('--country', help='Provider country', default='US')
    parser.add_argument('--language', help='Provider language', default='en')

    argv = parser.parse_args()
    email = argv.email
    password = argv.password

    connect(mongodb_uri=argv.mongo_uri)
    new_user = ProviderAdminUser.make_provider(email=email.lower(), password=password, country=argv.country,
                                               language=argv.language)
    new_user.status = ProviderAdminUser.Status.ACTIVE
    new_user.save()
    print('Successfully created provider email: {0}, password: {1}'.format(email, password))
