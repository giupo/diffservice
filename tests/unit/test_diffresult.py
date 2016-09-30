# -*- coding:utf-8 -*-

"""
test_diffresult
----------------------------------

Tests for `DiffResultsHandler` class.
"""
import json
import pytest

from diffservice import app as app_module
from diffservice.applogging import getLogger
from diffservice.controllers import DiffResultsHandler
log = getLogger(__name__)


@pytest.fixture
def app():
    return app_module.makeApp()


@pytest.mark.gen_test
def test_diffrequest_get_empty(http_client, base_url):
    response = yield http_client.fetch(
        base_url + DiffResultsHandler.context(),
        method='GET')
    log.info(response.body)
    resobj = json.loads(response.body)
    assert response.code == 200
    assert isinstance(resobj, list)
    assert len(resobj) == 0


@pytest.mark.gen_test
def test_diffresult_crud(http_client, base_url):
    context = DiffResultsHandler.context()
    post_args = {
        'request_id': 1,
        'result': {
            'B': 2
        }
    }

    response = yield http_client.fetch(
        base_url + context,
        method='POST',
        body=json.dumps(post_args),
        follow_redirects=False)

    resobj = json.loads(response.body)
    assert response.code == 201

    response = yield http_client.fetch(
        base_url + context + '/' + str(resobj['id']),
        method='GET')

    obj1 = json.loads(response.body)
    assert obj1 == resobj

    # ====

    put_args = {
        'request_id': 2,
        'result': {
            'A': 1
        }
    }

    response2 = yield http_client.fetch(
        base_url + context + '/1',
        method='PUT',
        body=json.dumps(put_args),
        follow_redirects=False)

    obj2 = json.loads(response2.body)

    assert response2.code == 200

    assert json.loads(obj2['result_json']) == put_args['result']
    assert obj2['request_id'] == put_args['request_id']
    assert obj2['id'] == 1
    # ====

    delete_response = yield http_client.fetch(
        base_url + context + '/1',
        method='DELETE')

    assert delete_response.code == 204
    assert delete_response.body == ''


@pytest.mark.gen_test
def test_diffresult_get_is_still_empty0(http_client, base_url):
    response = yield http_client.fetch(
        base_url + DiffResultsHandler.context(),
        method='GET')

    resobj = json.loads(response.body)
    assert response.code == 200
    assert isinstance(resobj, list)
    assert len(resobj) == 0


@pytest.mark.gen_test
def test_diffresult_no_side_effects1(http_client, base_url):
    post_args = {
        'request_id': 2,
        'result': {
            'A': 1
        }
    }

    response = yield http_client.fetch(
        base_url + DiffResultsHandler.context(),
        method='POST',
        body=json.dumps(post_args),
        follow_redirects=False)

    resobj = json.loads(response.body)
    assert response.code == 201
    assert resobj['id'] == 1
