

import logging
import tornado.log
logging.root.handlers = []

log = logging.getLogger()

log.debug("log init")
handler = logging.StreamHandler()
formatter = tornado.log.LogFormatter()
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.DEBUG)
log.debug("log init complete")


def getLogger(key):
    return logging.getLogger(key)

