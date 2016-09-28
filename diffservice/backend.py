# -*- coding:utf-8 -*-

import redis

from config import config
from applogging import getLogger
from model import SQLAlchemyDictView

log = getLogger(__name__)


class Queue(object):
    """Represent a queue for async jobs on the backend"""
    @classmethod
    def post(cls, data):
        log.debug('posting to backend')
        r = redis.StrictRedis(
            host=config.get('Redis', 'host'),
            port=config.getint('Redis', 'port'), db=0)

        if isinstance(data, SQLAlchemyDictView):
            data = data.to_dict()

        r.rpush(config.get('Redis', 'worker_queue'), data)
        log.debug('post to backend complete')
