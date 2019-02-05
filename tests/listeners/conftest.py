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