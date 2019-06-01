#!/usr/bin/env python3

# https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04

# this file mostly for debug, in prod we using gunicorn (gunicorn3 --bind 0.0.0.0:8080 server:app)

from app import app
import argparse

PROJECT_NAME = 'iptv_admin'
HOST = '0.0.0.0'
PORT = 8080

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=PROJECT_NAME, usage='%(prog)s [options]')
    parser.add_argument('--port', help='port (default: {0})'.format(PORT), default=PORT)
    parser.add_argument('--host', help='host (default: {0})'.format(HOST), default=HOST)
    argv = parser.parse_args()

    app.run(host=argv.host, port=argv.port, debug=True, use_reloader=True)  # debug=True, use_reloader=False
