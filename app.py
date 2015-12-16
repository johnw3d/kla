#  app.py  - kla app main
#
#
__author__ = 'johnw'

import os, sys
import logging

import settings
from webapp.handlers.main import run_dev_server

log = logging.getLogger('app')

def main(argv):
    "kla main, start kla dev webapp"

    run_dev_server()

# ----------  command-line processor -------

CMDS = {
    "start": main,
}

if __name__ == "__main__":
    # config logging
    logging.basicConfig(filename=os.path.join(settings.LOGS.LOG_ROOT, 'kla.log'), filemode='a',
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
