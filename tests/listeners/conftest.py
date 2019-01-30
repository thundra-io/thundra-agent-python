import mock
import pytest

@pytest.fixture()
def mocked_span():
    return mock.Mock(name='mocked_span')

@pytest.fixture()
def mocked_listener():
    return mock.Mock(name='mocked_listener')

@pytest.fixture()
def mocked_span():
    return mock.Mock(name='mocked_span')

@pytest.fixture
def handler_with_xray_testing(thundra_with_xray):
    @thundra_with_xray
    def _handler(event, context):
        return {
            "Hello": "Hello Thundra"
        }

    return thundra_with_xray, _handler
