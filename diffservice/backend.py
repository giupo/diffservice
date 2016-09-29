# -*- coding:utf-8 -*-

import redis

from config import config
from applogging import getLogger
from model import SQLAlchemyDictView
from pysd.discovery import sd

try:
    import concurrent.futures as futures  # python 3.x
except ImportError:
    import futures  # python 2.x

from multiprocessing import cpu_count


log = getLogger(__name__)


def redisConnection():
    """Redis Connection Factory"""
    return redis.StrictRedis(
        host=config.get('Redis', 'host'),
        port=config.getint('Redis', 'port'), db=0)


class Queue(object):
    """Represent a queue for async jobs on the backend"""
    @classmethod
    def post(cls, data):
        log.debug('posting to backend')
        r = redisConnection()
        if isinstance(data, SQLAlchemyDictView):
            data = data.to_dict()

        r.rpush(config.get('Redis', 'worker_queue'), data)
        log.debug('post to backend complete')


class DiffServer(object):
    """
    Backend server for evaluating differences between
    series.

    This polls data from a queue (Redis) and executes
    diffs in a dedicated thread (per request)
    """

    def __init__(self):
        self._pool = futures.ThreadPoolExecutor(max_workers=cpu_count())
        self._redis = redisConnection()
        self.alive = False

    def submit(self, data):
        """enqueues a request to the pool"""
        self._pool.submit(self.execute, self, data)

    def execute(self, data):
        """
        Executes a job repsesented by data container
        this should be executed via `submit`, and not called
        directly: it will hang the current thread
        """
        dataurl = sd.getService('DataService')


    def run(self):
        self.alive = True
        log.info("Server loop started")
        while self.alive:
            try:
                log.debug("waiting for data from Redis")
                data = self._redis.rpop()
                log.debug("Received %s from Redis", str(data))
                # handle kill operations
                if False:
                    self.alive = False
                    continue

                self.submit(data)
            except Exception as e:
                log.exception(e)
        log.info("Server loop ended")


def main():
    s = DiffServer()
    s.run()


if __name__ == '__main__':
    main()
