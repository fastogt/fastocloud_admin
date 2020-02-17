#!/usr/bin/env python3
import argparse
import os
import sys
from pymodm import connect
from bson.objectid import ObjectId

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pyfastocloud_models.stream.entry import TestLifeStream
from pyfastocloud_models.service.entry import ServiceSettings
from pyfastocloud_models.utils.m3u_parser import M3uParser

PROJECT_NAME = 'test_life'


def _get_server_by_id(sid: str):
    try:
        server = ServiceSettings.objects.get({'_id': ObjectId(sid)})
    except ServiceSettings.DoesNotExist:
        return None
    else:
        return server


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=PROJECT_NAME, usage='%(prog)s [options]')
    parser.add_argument('uri', help='Uri to m3u8 list')
    parser.add_argument('mongo_uri', help='MongoDB credentials')

    argv = parser.parse_args()

    mongo = connect(argv.mongo_uri)
    if mongo:
        service_settings = ServiceSettings.objects.get({})
        m3u_parser = M3uParser()
        m3u_parser.read_m3u(argv.uri)
        m3u_parser.parse()
        for file in m3u_parser.files:
            stream = TestLifeStream.make_stream(service_settings)
            stream.input[0].uri = file['link']
            stream.name = '{0}({1})'.format(file['tvg-group'], file['title'])
            service_settings.streams.append(stream)

        service_settings.save()
