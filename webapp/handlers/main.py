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
    #
    #  test parseTree
    from parser.parse import Parser
    from parser.patterns.clientLog import patternDef
    import os
    #
    p = Parser(os.path.expanduser("~/Dropbox/Documents/Kontiki 2014/debugging/Lloyds/pDPTu3_AT2k1-20151125-204429/error2.log"), patternDef)
    p.parse()
    #
    def _renderParseTree(tree):
        if isinstance(tree, dict):
            nodelist = []
            for k in sorted(tree.keys()):
                v = tree[k]
                if isinstance(v, (dict, list)):
                    nodelist.append(dict(text=k, children=_renderParseTree(v)))
                else:
                    nodelist.append(


    return render_template("index.html")


#     'core' : {
#         'data' : [
#             { "text" : "Root node", "children" : [
#                 { "text" : "Child node 1" },
#                 { "text" : "Child node 2" },
#
#                 { "text" : "Child node 3" }
#
#             ]
#             },
#         ]
#     }
# });