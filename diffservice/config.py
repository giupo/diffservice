"""
This modules handles configuration for the diff service

Configuration can be specified at command line, each key
or specifing the path for the config file.

A config file is an INI file. It can reside in:
 - $HOME/.diffservice/config.ini
 - any other location specified at command line
 - /dev/null (if config options are specified at command line, each one)

Config options are :
- url of the database("schema://host:port/dbname")
- host:port for Redis

"""

try:
    from ConfigParser import ConfigParser
except:
    from configparser import ConfigParser
# -*- coding:utf-8 -*-

import os
from tornado.options import define, options, parse_command_line

from applogging import getLogger
log = getLogger(__name__)

DEFAULT_REDIS_HOST = "localhost"
DEFAULT_REDIS_PORT = 6379
DEFAULT_DB_URL = "sqlite://"
DEFAULT_NPROC = 1
DEFAULT_CONFIG_FILE_PATH = os.path.join(os.path.expanduser("~"),
                                        ".diffservice", "config.ini")

define("redisHost", default=DEFAULT_REDIS_HOST, help="Redis host")
define("redisPort", default=DEFAULT_REDIS_PORT, type=int, help="Redis port")
define("DBURL", default=DEFAULT_DB_URL, help="DB connection url")
define("nproc", default=DEFAULT_NPROC, type=int, help="Numero processi")
define("config", default=DEFAULT_CONFIG_FILE_PATH, help="Path to config file")

parse_command_line()

config = ConfigParser()
config.add_section('DB')
config.add_section('Redis')
config.add_section('General')

config.set('DB', 'url', options.DBURL)
config.set('Redis', 'host', options.redisHost)
config.set('Redis', 'port', str(options.redisPort))
config.set('General', 'nproc', str(options.nproc))

if os.path.isfile(options.config):
    config.read(options.config)

log.info("Starting with the following config properties:")
for section in config.sections():
    for key, val in config.items(section):
        log.info('[%s] %s=%s' % (section, key, val))
