#!/usr/bin/env python3
import argparse
import os
import sys
from mongoengine import connect

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.home.user_loging_manager import User

PROJECT_NAME = 'test_life'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=PROJECT_NAME, usage='%(prog)s [options]')
    parser.add_argument('--mongo_uri', help='MongoDB credentials', default='mongodb://localhost:27017/iptv')
    parser.add_argument('--email', help='User email')
    parser.add_argument('--password', help='User password')

    argv = parser.parse_args()

    mongo = connect(argv.mongo_uri)
    if mongo:
        hash_pass = User.generate_password_hash(argv.password)
        new_user = User(email=argv.email, password=hash_pass)
        new_user.status = User.Status.ACTIVE
        new_user.save()
