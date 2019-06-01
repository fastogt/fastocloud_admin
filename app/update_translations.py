#!/usr/bin/env python3


import subprocess

# pybabel update -i messages.pot -d translations

if __name__ == '__main__':
    subprocess.call(['pybabel', 'extract', '-F', 'babel.cfg', '-k', 'lazy_gettext', '-o', 'messages.pot', '.'])
    subprocess.call(['pybabel', 'update', '-i', 'messages.pot', '-d', 'translations'])
