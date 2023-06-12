import os
import pytest
import mock

from catchpoint import constants
from catchpoint.catchpoint_agent import Catchpoint
from catchpoint.reporter import Reporter
from catchpoint.plugins.trace.traceable import Traceable
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.config import config_names


@pytest.fixture
@mock.patch('catchpoint.reporter.requests')
def reporter(mock_requests):
    return Reporter('api key', mock_requests.Session())


@pytest.fixture
def catchpoint_with_profile(reporter, monkeypatch):
    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'region')
    ConfigProvider.set(config_names.CATCHPOINT_APPLICATION_ID, '[]test')
    ConfigProvider.set(config_names.CATCHPOINT_APPLICATION_VERSION, 'version')
    ConfigProvider.set(config_names.CATCHPOINT_APPLICATION_STAGE, 'dev')

    catchpoint = Catchpoint('api key', disable_metric=True)
    catchpoint.reporter = reporter
    return catchpoint


@pytest.fixture
def handler_with_profile(catchpoint_with_profile):
    @catchpoint_with_profile.call
    def _handler(event, context):
        return {
            'message': 'Hello'
        }
    return catchpoint_with_profile, _handler


@pytest.fixture
def catchpoint_with_request_response_skip(monkeypatch):
    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'region')
    ConfigProvider.set(config_names.CATCHPOINT_APPLICATION_ID, '[]test')
    ConfigProvider.set(config_names.CATCHPOINT_APPLICATION_VERSION, 'version')
    ConfigProvider.set(config_names.CATCHPOINT_APPLICATION_STAGE, 'dev')
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_REQUEST_SKIP, 'true')
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_RESPONSE_SKIP, 'true')
    catchpoint = Catchpoint('api key', disable_metric=True)
    return catchpoint


@pytest.fixture
def handler_with_request_response_skip(catchpoint_with_request_response_skip):
    @catchpoint_with_request_response_skip.call
    def _handler(event, context):
        pass
    return catchpoint_with_request_response_skip, _handler


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
