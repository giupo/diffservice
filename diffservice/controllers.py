# -*- coding:utf-8 -*-

import json

import tornado.web
import tornado.escape

from applogging import getLogger
from model import DiffRequest, DiffResult, session_scope
from backend import Queue
from config import config

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
    def context(cls):
        _context = config.get('General', 'request_url', '/requests')
        if _context[0] != '/':
            _context = '/' + _context
        return _context

    @classmethod
    def routes(cls):
        return [
            (cls.context()+'/(\\d+)', cls),
            (cls.context(), cls)
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
        log.info(self.request.body)
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
        params.update(tornado.escape.json_decode(self.request.body or '{}'))
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


class DiffResultsHandler(tornado.web.RequestHandler):
    """
    Handles the diffResults computed from the backend
    """

    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')
        self.set_header('Access-Control-Allow-Origin', '*')

    @classmethod
    def context(cls):
        _context = config.get('General', 'results_url', '/results')
        if _context[0] != '/':
            _context = '/' + _context
        return _context

    @classmethod
    def routes(cls):
        return [
            (cls.context() + '/(\\d+)', cls),
            (cls.context(), cls)
        ]

    def get(self, id=None):
        with session_scope() as s:
            if id is None:
                result = [x.to_dict() for x in s.query(DiffResult).all()]
            else:
                result = s.query(DiffResult).filter_by(id=id).first()
                if result is None:
                    raise tornado.web.HTTPError(404)
                result = result.to_dict()

        self.finish(json.dumps(result))

    def post(self):
        log.info(self.request.body)
        params = {k: self.get_argument(k) for k in self.request.arguments}
        params.update(tornado.escape.json_decode(self.request.body or '{}'))
        log.debug('Params received: %s', str(params))
        res = DiffResult(**params)
        with session_scope() as s:
            s.add(res)
            s.commit()
            self.set_status(201)
            self.finish(res.to_json())

    def put(self, id):
        params = {k: self.get_argument(k) for k in self.request.arguments}
        params.update(tornado.escape.json_decode(self.request.body or '{}'))
        log.debug('Params received: %s', str(params))
        with session_scope() as s:
            result = s.query(DiffResult).filter_by(id=id).first()
            if result is None:
                raise tornado.web.HTTPError(404)
            result.update(**params)
            s.commit()
            self.finish(result.to_json())

    def delete(self, id):
        with session_scope() as s:
            res = s.query(DiffResult).filter_by(id=id).first()
            if res is None:
                raise tornado.web.HTTPError(404)
            s.delete(res)
            s.commit()
            self.set_status(204)
            self.finish()
