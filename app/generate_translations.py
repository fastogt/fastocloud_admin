#!/usr/bin/env python3

from constants import AVAILABLE_LOCALES

import subprocess

# pybabel extract -F babel.cfg -o messages.pot .
# pybabel init -i messages.pot -d translations -l ru

if __name__ == '__main__':
    subprocess.call(['pybabel', 'extract', '-F', 'babel.cfg', '-k', 'lazy_gettext', '-o', 'messages.pot', '.'])
    for locale in AVAILABLE_LOCALES:
        subprocess.call(['pybabel', 'init', '-i', 'messages.pot', '-d', 'translations', '-l', locale])
