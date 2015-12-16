#  settings.py - kla app settings
#
__author__ = 'johnw'

import os, logging

# utility dict class that maps attr access to dict items
class settings(dict):
    def __getattr__(self, name):
        return self[name]

APP = settings(
    port = 9001,
)

FLASK = settings(
    app = settings(
        static_path = '/static',
        static_folder = 'webapp/static',
        template_folder = 'webapp/templates'),
    run = settings(
        host = '0.0.0.0',
        port = 9000,
        debug = True
    )
)

ELASTIC_SEARCH = settings(
    host = 'tc1-elk.esjc.kontiki.com',
    port = 9200,
)

LOGS = settings(
    LOG_ROOT = os.environ.get('THREADERY_LOG_ROOT', '/var/log/kla'),
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler'
            },
            'null': {
                'level': 'DEBUG',
                'class':'django.utils.log.NullHandler',
            },

        },
        'loggers': {
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },
        }
    },
    LOG_LEVEL = logging.DEBUG,
    LOG_FORMAT = '%(asctime)s %(process)d %(filename)s(%(lineno)d): %(levelname)s %(message)s',
)
