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
