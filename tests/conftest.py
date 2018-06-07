import pytest

from thundra.thundra_agent import Thundra


class MockContext:
    memory_limit_in_mb = '128'

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
def thundra_with_apikey():
    return Thundra('api key', disable_metric=True)


@pytest.fixture
def handler_with_apikey(thundra_with_apikey):
    @thundra_with_apikey.call
    def _handler(event, context):
        pass

    return thundra_with_apikey, _handler


@pytest.fixture
def thundra():
    return Thundra()


@pytest.fixture
def handler(thundra):
    @thundra.call
    def _handler(event, context):
        pass
    return thundra, _handler


@pytest.fixture
def handler_with_exception(thundra_with_apikey):
    @thundra_with_apikey.call
    def _handler(event, context):
        raise Exception('hello')
    return thundra_with_apikey, _handler
