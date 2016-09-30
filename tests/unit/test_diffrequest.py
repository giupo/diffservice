# -*- coding:utf-8 -*-

"""
test_diffrequest
----------------------------------

Tests for `DiffRequestHandler` class.
"""

import json
import pytest

from diffservice import app as app_module
from diffservice.applogging import getLogger
from diffservice.controllers import DiffRequestsHandler
log = getLogger(__name__)


@pytest.fixture
def app():
    return app_module.makeApp()


@pytest.mark.gen_test
def test_diffrequest_get_empty(http_client, base_url):
    response = yield http_client.fetch(
        base_url + DiffRequestsHandler.context(),
        method='GET')
    log.info(response.body)
    resobj = json.loads(response.body)
    assert response.code == 200
    assert isinstance(resobj, list)
    assert len(resobj) == 0


@pytest.mark.gen_test
def test_diffrequest_crud(http_client, base_url):
    context = DiffRequestsHandler.context()
    post_args = {
        'tavola': 'tavola',
        'A': 'A',
        'B': 'B',
        'soglia': 1.,
        'who': 'me'
    }

    response = yield http_client.fetch(
        base_url + context,
        method='POST',
        body=json.dumps(post_args),
        follow_redirects=False)

    resobj = json.loads(response.body)
    keys_to_test = ['tavola', 'soglia', 'A', 'B', 'who']
    assert response.code == 201
    for key in keys_to_test:
        assert resobj[key] == post_args[key]

    response = yield http_client.fetch(
        base_url + context + "/" + str(resobj['id']),
        method='GET')

    obj1 = json.loads(response.body)
    assert obj1 == resobj

    # ====

    put_args = {
        'tavola': 'tavola1',
        'A': 'A1',
        'B': 'B1',
        'soglia': 0.,
        'who': 'you'
    }

    response2 = yield http_client.fetch(
        base_url + context + '/1',
        method='PUT',
        body=json.dumps(put_args),
        follow_redirects=False)

    obj2 = json.loads(response2.body)

    assert response2.code == 200

    keys_to_test = ['tavola', 'soglia', 'A', 'B', 'who']
    for key in keys_to_test:
        assert obj2[key] == put_args[key]
        assert obj1[key] != obj2[key]

    # ====

    delete_response = yield http_client.fetch(
        base_url + context + '/1',
        method='DELETE')

    assert delete_response.code == 204
    assert delete_response.body == ''


@pytest.mark.gen_test
def test_diffrequest_get_is_still_empty(http_client, base_url):
    response = yield http_client.fetch(
        base_url + DiffRequestsHandler.context(),
        method='GET')

    resobj = json.loads(response.body)
    assert response.code == 200
    assert isinstance(resobj, list)
    assert len(resobj) == 0


@pytest.mark.gen_test
def test_diffrequest_no_side_effects(http_client, base_url):
    post_args = {
        'tavola': 'tavola',
        'A': 'A',
        'B': 'B',
        'soglia': 1.,
        'who': 'me'
    }

    response = yield http_client.fetch(
        base_url + DiffRequestsHandler.context(),
        method='POST',
        body=json.dumps(post_args),
        follow_redirects=False)

    resobj = json.loads(response.body)
    assert response.code == 201
    assert resobj['id'] == 1
