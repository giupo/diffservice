# -*- coding:utf-8 -*-

import signal
import time

import tornado.httpserver
import tornado.ioloop
import tornado.web

from applogging import getLogger
from pysd.discovery import Service
from config import config
from controllers import DiffRequestsHandler, AdminHandler
from controllers import DiffResultsHandler

log = getLogger(__name__)

routes = []
routes.extend(AdminHandler.routes())
routes.extend(DiffRequestsHandler.routes())
routes.extend(DiffResultsHandler.routes())

settings = {
}


def makeApp():
    global routes
    global settings
    application = tornado.web.Application(routes, **settings)
    return application


def on_shutdown():
    """shutdown handlers"""
    global service
    log.info("Shutting down")
    if service:
        service.unregister()

    tornado.ioloop.IOLoop.instance().stop()
    log.info("%s closed", config.get('General', 'servicename'))


def startWebServer():
    """starts the web server"""

    global service

    log.debug("Starting web server")
    server = tornado.httpserver.HTTPServer(makeApp())
    port = config.getint('General', 'port')
    while True:
        try:
            log.info('try %d', port)
            server.bind(port)
            log.info('%d is free, starting and registering', port)
        except:
            log.info('port already used, ...')
            port += 1
        else:
            break

    service = Service(config.get('General', 'servicename'),
                      config.get('General', 'protocol') + '://' +
                      config.get('General', 'addr') + ':' + str(port))

    service.register()
    time.sleep(1)
    log.info(str(service))

    ioloop = tornado.ioloop.IOLoop.instance()
    log.debug('Registering SIGINT handler')
    signal.signal(signal.SIGINT,
                  lambda sig, frame:
                  ioloop.add_callback_from_signal(on_shutdown))
    log.info('Routes: %s', str(routes))
    server.start(config.getint('General', 'nproc'))
    log.info('%s started', config.get('General', 'servicename'))
    ioloop.start()


def main():
    """main entry point of application"""
    startWebServer()


if __name__ == '__main__':
    """this is where everything starts"""
    main()
