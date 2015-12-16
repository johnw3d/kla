#  app.py  - threadery app main
#
# Copyright (c) John Wainwright 2014 - All rights reserved.
#
__author__ = 'johnw'

import os, sys
import logging
import tornado.ioloop
import tornado.web

import settings
from handlers.home import (HomeHandler, ItemTagHandler, )
from handlers.threads import (ThreadListHandler, ThreadSelectorHandler, )
from handlers.feeds import (AddFeedHandler, )
from handlers.folds import (AddFoldHandler, )

from threadstore.client import ThreadStoreClient

handlers = [
    (r"/", HomeHandler),
    # folds
    (r"/addfold/", AddFoldHandler),
    (r"/addfold/directory/", AddFoldHandler),
    # feeds
    (r"/addfeed/", AddFeedHandler),
    (r"/addfeed/directory/", AddFeedHandler),
    # threads
    (r"/threadlist/(.*)", ThreadListHandler),
    (r"/threadselector/item/(.*)", ThreadSelectorHandler),
    (r"/itemtag/(.*)", ItemTagHandler),
]

log = logging.getLogger('app')

def main(argv):
    "threader main, start threadery webapp"
    # open threadstore client
    ThreadStoreClient.open(**settings.THREADSTORE)
    # start threadery webapp
    msg = 'Starting Threadery on port %d...' % settings.APP.port
    log.info(msg)
    print(msg)
    application = tornado.web.Application(handlers, **settings.TORNADO)
    application.listen(settings.APP.port)
    tornado.ioloop.IOLoop.instance().start()

def init_reader_threadstore(argv):
    "init reader threadstore collections"
    tsc = ThreadStoreClient.open(**settings.THREADSTORE)
    tsc.init_reader_threadstore()
    tsc.close()

def build_test_db(argv):
    "init reader threadstore collections & build test feeds"
    tsc = ThreadStoreClient.open(**settings.THREADSTORE)
    tsc.init_reader_threadstore()
    tsc.build_test_db()
    tsc.close()

# ----------  command-line processor -------

CMDS = {
    "start": main,
    "testdb": build_test_db,
    "cleandb": init_reader_threadstore,
}

if __name__ == "__main__":
    # config logging
    logging.basicConfig(filename=os.path.join(settings.LOGS.LOG_ROOT, 'app.log'), filemode='a',
                    level=settings.LOGS.LOG_LEVEL, format=settings.LOGS.LOG_FORMAT)
    # dispatch cmd
    if len(sys.argv) > 1:
        cmd = CMDS.get(sys.argv[1])
        if cmd:
            cmd(sys.argv)
        else:
            print(("Unknown command: ", sys.argv[1]))
    else:
        main(sys.argv)
