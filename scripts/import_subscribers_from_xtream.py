#!/usr/bin/env python3
import argparse
import os
import sys
from pymodm import connect
import mysql.connector

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.service.service import ServiceSettings

PROJECT_NAME = 'import_subscribers_from_xtream'

from scripts.migrate.xtream.subscribers import import_subscribers_to_server

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=PROJECT_NAME, usage='%(prog)s [options]')
    parser.add_argument('--mongo_uri', help='MongoDB credentials', default='mongodb://localhost:27017/iptv')
    parser.add_argument('--mysql_host', help='MySQL host', default='localhost')
    parser.add_argument('--mysql_user', help='MySQL username', default='root')
    parser.add_argument('--mysql_password', help='MySQL password', default='')
    parser.add_argument('--mysql_port', help='MySQL port', default=3306)
    parser.add_argument('--server_id', help='Server ID', default='')

    argv = parser.parse_args()
    mysql_host = argv.mysql_host
    mysql_user = argv.mysql_user
    mysql_password = argv.mysql_password
    mysql_port = argv.mysql_port
    server_id = argv.server_id

    mongo = connect(uri=argv.mongo_uri)
    if not mongo:
        sys.exit(1)

    ser = ServiceSettings.objects(id=server_id).first()
    if not ser:
        sys.exit(1)

    d = mysql.connector.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        passwd=mysql_password,
        database='xtream_iptvpro'
    )

    import_subscribers_to_server(d, ser)
    d.close()
