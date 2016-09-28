# -*- coding:utf-8 -*-

import json

import tornado.web
import tornado.escape

from applogging import getLogger
from model import DiffRequest, session_scope
from backend import Queue

log = getLogger(__name__)


class AdminHandler(tornado.web.RequestHandler):
    """Admin handler"""

    @classmethod
    def routes(cls):
        return [
            (r'/admin', cls)
        ]

    def get(self):
        self.write('ciao mondo')
        self.finish()


class DiffRequestsHandler(tornado.web.RequestHandler):
    """
    Handles all the diff requests. on DiffRequest creation, sends a
    message to a queue to async process the request and store the results
    """

    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')
        self.set_header('Access-Control-Allow-Origin', '*')

    @classmethod
    def routes(cls):
        return [
            (r'/requests/(\d*)', cls),
            (r'/requests', cls)
        ]

    def get(self, id=None):
        with session_scope() as s:
            if id is None:
                result = [x.to_dict() for x in s.query(DiffRequest).all()]
            else:
                result = s.query(DiffRequest).filter_by(id=id).first()
                if result is None:
                    raise tornado.web.HTTPError(404)
                result = result.to_dict()

        self.finish(json.dumps(result))

    def post(self):
        params = {k: self.get_argument(k) for k in self.request.arguments}
        params.update(tornado.escape.json_decode(self.request.body or '{}'))
        log.debug('Params received: %s', str(params))
        request = DiffRequest(**params)
        with session_scope() as s:
            s.add(request)
            s.commit()
            Queue.post(request)
            self.set_status(201)
            self.finish(request.to_json())

    def put(self, id):
        params = {k: self.get_argument(k) for k in self.request.arguments}
        log.debug('Params received: %s', str(params))
        with session_scope() as s:
            request = s.query(DiffRequest).filter_by(id=id).first()
            if request is None:
                raise tornado.web.HTTPError(404)
            request.update(**params)
            s.commit()
            self.finish(request.to_json())

    def delete(self, id):
        with session_scope() as s:
            request = s.query(DiffRequest).filter_by(id=id).first()
            if request is None:
                raise tornado.web.HTTPError(404)
            s.delete(request)
            s.commit()
            self.set_status(204)
            self.finish()
