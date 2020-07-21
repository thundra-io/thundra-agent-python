import os
import pytest
import mock

from thundra import constants
from thundra.thundra_agent import Thundra
from thundra.reporter import Reporter
from thundra.plugins.trace.traceable import Traceable
from thundra.config.config_provider import ConfigProvider
from thundra.config import config_names


@pytest.fixture
@mock.patch('thundra.reporter.requests')
def reporter(mock_requests):
    return Reporter('api key', mock_requests.Session())


@pytest.fixture
def thundra_with_profile(reporter, monkeypatch):
    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'region')
    ConfigProvider.set(config_names.THUNDRA_APPLICATION_ID, '[]test')
    ConfigProvider.set(config_names.THUNDRA_APPLICATION_VERSION, 'version')
    ConfigProvider.set(config_names.THUNDRA_APPLICATION_STAGE, 'dev')

    thundra = Thundra('api key', disable_metric=True)
    thundra.reporter = reporter
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
    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'region')
    ConfigProvider.set(config_names.THUNDRA_APPLICATION_ID, '[]test')
    ConfigProvider.set(config_names.THUNDRA_APPLICATION_VERSION, 'version')
    ConfigProvider.set(config_names.THUNDRA_APPLICATION_STAGE, 'dev')
    ConfigProvider.set(config_names.THUNDRA_LAMBDA_TRACE_REQUEST_SKIP, 'true')
    ConfigProvider.set(config_names.THUNDRA_LAMBDA_TRACE_RESPONSE_SKIP, 'true')
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
