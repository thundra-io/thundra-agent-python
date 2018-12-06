import pytest
import mock
from thundra.thundra_agent import Thundra
from thundra.reporter import Reporter
from thundra import constants
from aws_xray_sdk.core import xray_recorder
from tests.listeners.test_listeners_thundra_class import ThundraForListeners
import os


class MockContext:
    memory_limit_in_mb = '128'
    log_group_name = 'log_group_name'
    log_stream_name = 'log_stream_name[]id'
    aws_request_id = 'aws_request_id'
    invoked_function_arn = 'invoked_function_arn'
    function_version = 'function_version'

    def __init__(self, f_name='test_func'):
        self.function_name = f_name
        self.memory_limit_in_mb = '128'
        self.log_group_name = 'log_group_name'
        self.log_stream_name = 'log_stream_name[]id'
        self.aws_request_id = 'aws_request_id'
        self.invoked_function_arn = 'invoked_function_arn'
        self.function_version = 'function_version'


@pytest.fixture
def mock_context():
    return MockContext()


@pytest.fixture
def mock_event():
    event = {
        'message': 'Hello'
    }
    return event


@pytest.fixture()
def mock_report():
    return {
        'apiKey': 'api key',
        'type': 'type',
        'dataFormatVersion': '1.1.1',
        'data': 'data'
    }


@pytest.fixture
@mock.patch('thundra.reporter.requests')
def reporter(mock_requests):
    return Reporter('api key', mock_requests.Session())


@pytest.fixture
def thundra(reporter):
    thundra = Thundra(disable_metric=True)
    thundra.reporter = reporter
    return thundra


@pytest.fixture
def handler(thundra):
    @thundra.call
    def _handler(event, context):
        pass
    return thundra, _handler


@pytest.fixture
def handler_with_exception(thundra):
    @thundra.call
    def _handler(event, context):
        raise Exception('hello')
    return thundra, _handler

@pytest.fixture
def thundra_with_xray(monkeypatch, reporter):
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_TRACE_ENABLE_XRAY, 'true')
    monkeypatch.setitem(os.environ, constants.THUNDRA_APPLICATION_STAGE, 'dev')
    thundra = ThundraForListeners(disable_metric=True)
    thundra.reporter = reporter
    xray_recorder.configure(sampling=False)
    xray_recorder.begin_segment('test')
    return thundra

@pytest.fixture
def handler_with_xray(thundra_with_xray, monkeypatch):
    @thundra_with_xray.call
    def _handler(event, context):
        pass
    return thundra_with_xray, _handler

@pytest.fixture
def handler_with_xray_testing(thundra_with_xray):
    @thundra_with_xray
    def _handler(event, context):
        return {
            "Hello": "Hello Thundra"
        }
    return thundra_with_xray, _handler