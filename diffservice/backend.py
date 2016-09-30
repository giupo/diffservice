# -*- coding:utf-8 -*-


import signal
import json
import threading

import redis
import redis.exceptions

from config import config
from applogging import getLogger
from model import SQLAlchemyDictView
from clients import DiffRequestsClient, dati_tavola

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

        r.rpush(config.get('Redis', 'worker_queue'), json.dumps(data))
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
        signal.signal(signal.SIGINT,
                      lambda sig, frame:
                      self.on_shutdown)

    def submit(self, msg):
        """enqueues a request to the pool"""
        log.debug("Submitting: %s", msg)
        self._pool.submit(self.execute,  msg)

    def on_shutdown(self):
        """shutdown callback"""
        self.alive = False

    def execute(self, msg):
        """
        Executes a job repsesented by data container
        this should be executed via `submit`, and not called
        directly: it will hang the current thread
        """
        thread_name = threading.current_thread().name
        log.info('[%s] Processing data: %s', thread_name, msg)
        queue_name, data = msg
        log.debug("[%s] Queue name: %s", thread_name, queue_name)
        log.debug("[%s] Data: %s", thread_name, data)
        data = json.loads(data)
        id = data['id']
        log.debug('[%s] Processing DiffRequest:%d', thread_name, id)

        try:
            diffclient = DiffRequestsClient()
            req = diffclient[id]
            if req['status'] != 'PENDING':
                log.debug(
                    '[%s] DiffRequest:%d is not PENDING, but %s, discarding...',  # noqa
                    thread_name, id, req['status'])
                return

            diffclient.running(id)
            # get all data from tavola
            # get all series from tavola for A
            datiA = dati_tavola(data['A'], data['tavola'])
            datiB = dati_tavola(data['A'], data['tavola'])
            common = []

            for name in common:
                serieA = datiA[name]
                serieB = datiB[name]
                # handle case where freq is different

                diff = serieA - serieB
                deltap = 100 * diff/serieB

            # get all series from tavola for B
            # for each series common in A & B
            #    diff = A - B
            #    deltap(diff)
            # store data in result
            # push message of result done.

            diffclient.done(id)
        except Exception as e:
            log.exception("[%s] %s", thread_name, e)
            diffclient.error(id)

    def run(self):
        self.alive = True
        log.info("Server loop started")
        while self.alive:
            try:
                log.debug("waiting for data from Redis")
                data = self._redis.blpop(
                    config.get('Redis', 'worker_queue'))
                log.debug("Received %s from Redis", str(data))
                # handle kill operations
                if data == {}:
                    self.alive = False
                    continue

                self.submit(data)
            except (KeyboardInterrupt, SystemExit,
                    redis.exceptions.ConnectionError) as e:
                if 'Interrupted system call' in str(e):
                    log.warn(e)
                    log.info("lost connection to Redis")
                else:
                    log.error(e)
                # well, we are here beacause no Redis or on purpose,
                # let's shutdown everything
                self.alive = False

            except Exception as e:
                log.exception(e)

        log.info("Server loop ended")


def main():
    s = DiffServer()
    s.run()


if __name__ == '__main__':
    main()
