#  app.py  - kla app main
#
#
__author__ = 'johnw'

import os, sys
import logging

from flask import Flask

import settings

log = logging.getLogger('app')

# instantiate Flask app
kla = Flask(__name__)

@kla.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run()



def main(argv):
    "kla main, start kla webapp"

    kla.run(host='0.0.0.0', port=9000, debug=True)


# ----------  command-line processor -------

CMDS = {
    "start": main,
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
