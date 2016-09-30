# -*- coding:utf-8 -*-

import os
import requests
import threading

from applogging import getLogger
from config import config
from pysd.discovery import sd
from pandas import Series

log = getLogger(__name__)


class ServiceClient(object):
    """
    Base class for all Serivce clients
    """
    def __init__(self):
        self.trust_proxy = bool(config.get('General', 'trust_proxy'))
        self.ssl_verify = bool(config.get('General', 'ssl_verify'))
        if self.trust_proxy:
            self.proxies = {
                'http': os.environ['http_proxy'],
                'https': os.environ['https_proxy']
            }
        else:
            self.proxies = {
                'http': None,
                'https': None
            }

    def get(self, url):
        res = requests.get(url, verify=self.ssl_verify, proxies=self.proxies)
        res.raise_for_status()
        return res.json()


class DiffRequestsClient(ServiceClient):
    """
    Client for DiffService
    """

    def __init__(self):
        super(DiffRequestsClient, self).__init__()
        self.context = config.get('General', 'request_url')

    def running(self, id):
        self.update(id, {
            'status': 'RUNNING'
        })

    def done(self, id):
        self.update(id, {
            'status': 'DONE'
        })

    def error(self, id):
        self.update(id, {
            'status': 'ERROR'
        })

    def update(self, id, data):
        url = '/'.join([self.base_url, str(id)])
        log.debug('URL to update %s with data: %s', url, data)
        res = requests.put(url, json=data,
                           verify=self.ssl_verify,
                           proxies=self.proxies)
        res.raise_for_status()
        return res.json()

    @property
    def base_url(self):
        service_name = config.get('General', 'servicename')
        url = sd.getService(service_name)
        if not url:
            raise Exception("URL for service %s is None" % service_name)
        url = ''.join([url, self.context])
        return url

    def __getitem__(self, key):
        thread_name = threading.current_thread().name
        log.debug('[%s] looking for DiffRequest %d', thread_name, key)
        url = '/'.join([self.base_url, str(key)])
        res = requests.get(url, verify=self.ssl_verify, proxies=self.proxies)
        res.raise_for_status()
        return res.json()


class MetaService(ServiceClient):
    """
    Client for Metadata Service
    """

    def __init__(self, tag):
        super(MetaService, self).__init__()
        self.tag = tag

    @property
    def base_url(self):
        service_name = config.get('General', 'meta_service_name')
        url = sd.getService(service_name)
        if not url:
            raise Exception("URL for service %s is None" % service_name)
        return url

    def lookup(self, key, value):
        url = '/'.join([self.base_url, self.tag, 'search', key, value])
        return self.get(url)


class DataService(ServiceClient):
    """
    Data service client
    """

    def __init__(self, tag):
        super(DataService, self).__init__()
        self.tag = tag

    @property
    def base_url(selfelf):
        service_name = config.get('General', 'data_service_name')
        url = sd.getService(service_name)
        if not url:
            raise Exception("URL for service %s is None" % service_name)
        return url

    def __getitem__(self, key):
        url = '/'.join([self.base_url, self.tag, key])
        return self.get(url)


def dati_tavola(tag, tavola):
    """helper function to download dati from tag and grouped by tavola"""
    meta = MetaService(tag)
    listanomi = meta.lookup('TAVOLA_DI_OUTPUT', tavola)
    datas = DataService(tag)
    dati = {}
    for name in listanomi:
        dati[name] = datas[name]

    return dati
