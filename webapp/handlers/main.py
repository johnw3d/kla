#  handlers/main.py  - kla app main webapp request handlers
#
#
__author__ = 'johnw'

import logging

from flask import (Flask, request, session, g, redirect, url_for,
     abort, render_template)

import settings

log = logging.getLogger('handlers.main')

# instantiate Flask (global) app
kla = Flask('app', **settings.FLASK.app)

def run_dev_server():
    "launch Flask dev server"
    kla.run(**settings.FLASK.run)

# -------- main request handlers --------

@kla.route('/')
def index():
    return "Hello, world."