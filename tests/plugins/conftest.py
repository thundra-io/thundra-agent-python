import os
import pytest

from thundra import constants
from thundra.thundra_agent import Thundra


@pytest.fixture
def thundra_with_profile(monkeypatch):
    monkeypatch.setitem(os.environ, constants.AWS_LAMBDA_LOG_STREAM_NAME, '[]test')
    monkeypatch.setitem(os.environ, constants.AWS_LAMBDA_FUNCTION_VERSION, 'version')
    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'region')
    monkeypatch.setitem(os.environ, constants.THUNDRA_APPLICATION_PROFILE, 'profile')
    thundra = Thundra('api key', disable_metric=True)
    return thundra


@pytest.fixture
def handler_with_profile(thundra_with_profile):
    @thundra_with_profile.call
    def _handler(event, context):
        pass
    return thundra_with_profile, _handler


@pytest.fixture
def thundra_with_request_response_skip(monkeypatch):
    monkeypatch.setitem(os.environ, constants.AWS_LAMBDA_LOG_STREAM_NAME, '[]test')
    monkeypatch.setitem(os.environ, constants.AWS_LAMBDA_FUNCTION_VERSION, 'version')
    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'region')
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_TRACE_REQUEST_SKIP, 'true')
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_TRACE_RESPONSE_SKIP, 'true')
    thundra = Thundra('api key', disable_metric=True)
    return thundra


@pytest.fixture
def handler_with_request_response_skip(thundra_with_request_response_skip):
    @thundra_with_request_response_skip.call
    def _handler(event, context):
        pass
    return thundra_with_request_response_skip, _handler
