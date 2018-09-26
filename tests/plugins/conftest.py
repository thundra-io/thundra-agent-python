import os
import pytest

from thundra import constants
from thundra.plugins.trace.traceable import Traceable
from thundra.thundra_agent import Thundra


@pytest.fixture
def thundra_with_profile(monkeypatch):
    monkeypatch.setitem(os.environ, constants.AWS_LAMBDA_APPLICATION_ID, '[]test')
    monkeypatch.setitem(os.environ, constants.AWS_LAMBDA_FUNCTION_VERSION, 'version')
    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'region')
    monkeypatch.setitem(os.environ, constants.THUNDRA_APPLICATION_STAGE, 'dev')
    thundra = Thundra('api key', disable_metric=True)
    return thundra


@pytest.fixture
def handler_with_profile(thundra_with_profile):
    @thundra_with_profile.call
    def _handler(event, context):
        return {
            'message': 'Hello'
        }
    return thundra_with_profile, _handler


@pytest.fixture
def thundra_with_request_response_skip(monkeypatch):
    monkeypatch.setitem(os.environ, constants.AWS_LAMBDA_APPLICATION_ID, '[]test')
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


@pytest.fixture
def traceable_trace_args():
    return Traceable(trace_args=True)


@pytest.fixture
def traceable_trace_return_val():
    return Traceable(trace_return_value=True)

@pytest.fixture
def traceable():
    return Traceable()


@pytest.fixture
def trace_args(traceable_trace_args):
    @traceable_trace_args.call
    def func_args(arg1, arg2):
        pass
    return traceable_trace_args, func_args


@pytest.fixture
def trace_return_val(traceable_trace_return_val):
    @traceable_trace_return_val.call
    def func_return_val():
        return {
            'message': 'Hi test!'
        }
    return traceable_trace_return_val, func_return_val


@pytest.fixture
def trace_error(traceable):
    @traceable.call
    def func_with_error():
        raise Exception('test')
    return traceable, func_with_error


@pytest.fixture
def trace(traceable):
    @traceable.call
    def func(arg):
        return {
            'response': 'test'
        }
    return traceable, func
