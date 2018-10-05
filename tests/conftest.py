import pytest
import mock

from thundra.thundra_agent import Thundra
from thundra.reporter import Reporter


class MockContext:
    memory_limit_in_mb = '128'
    log_group_name = 'log_group_name'
    log_stream_name = 'log_stream_name[]id'
    aws_request_id = 'aws_request_id'
    invoked_function_arn = 'invoked_function_arn'
    function_version = 'function_version'

    def __init__(self, f_name='test_func'):
        self.function_name = f_name


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
