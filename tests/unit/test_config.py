#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_config
----------------------------------

Tests for `diffservice.config` module.
"""
import io
from diffservice.config import config


def test_default_url():
    assert config.get('DB','url') == "sqlite://"

def test_deafault_redis_host():
    assert config.get('Redis', 'host') == 'localhost'

def test_default_redis_port():
    expected_port = 6379
    assert config.getint('Redis', 'port') == expected_port
    assert config.get('Redis', 'port') == str(expected_port)

def test_url_precedence():
    assert config.get('DB','url') == "sqlite://"
    sample_config = """
[DB]
url = postgres://host/port
"""
    config.readfp(io.BytesIO(sample_config))
    assert config.get('DB','url') != "sqlite://"
    assert config.get('DB','url') == 'postgres://host/port'

def test_side_effects():
    assert config.get('DB','url') != "sqlite://"
    assert config.get('DB','url') == 'postgres://host/port'

def test_redis_precedence():
    assert config.get('Redis','host') == "localhost"
    assert config.get('Redis','port') == "6379"
    sample_config = """
[Redis]
host = newRedisHost
port = 1234
"""
    config.readfp(io.BytesIO(sample_config))
    assert config.get('Redis', 'host') == "newRedisHost"
    assert config.get('Redis', 'port') == "1234"
    assert config.getint('Redis', 'port') == 1234

def test_redis_side_effects():
    assert config.get('Redis', 'host') == "newRedisHost"
    assert config.get('Redis', 'port') == "1234"
    assert config.getint('Redis', 'port') == 1234
