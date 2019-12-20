import os
from thundra import utils, constants
import pytest


def test_get_default_timeout_margin(monkeypatch):
    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'us-west-2')
    timeout_margin = utils.get_default_timeout_margin()
    assert timeout_margin == 200

    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'us-east-2')

    timeout_margin = utils.get_default_timeout_margin()
    assert timeout_margin == 600

    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'eu-west-1')

    timeout_margin = utils.get_default_timeout_margin()
    assert timeout_margin == 1000

    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'eu-west-1')
    monkeypatch.setitem(os.environ, constants.AWS_LAMBDA_FUNCTION_MEMORY_SIZE, '1536')

    timeout_margin = utils.get_default_timeout_margin()
    assert timeout_margin == 1000

    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'eu-west-1')
    monkeypatch.setitem(os.environ, constants.AWS_LAMBDA_FUNCTION_MEMORY_SIZE, '128')

    timeout_margin = utils.get_default_timeout_margin()
    assert timeout_margin == 3000


def test_get_nearest_collector(monkeypatch):
    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'us-west-2')
    collector = utils.get_nearest_collector()
    assert collector == "api.thundra.io"

    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'us-east-2')
    collector = utils.get_nearest_collector()
    assert collector == "api-us-east-1.thundra.io"

    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'eu-west-1')
    collector = utils.get_nearest_collector()
    assert collector == "api-eu-west-1.thundra.io"

    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'eu-west-2')
    collector = utils.get_nearest_collector()
    assert collector == "api-eu-west-2.thundra.io"

    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'ap-')
    collector = utils.get_nearest_collector()
    assert collector == "api-ap-northeast-1.thundra.io"
