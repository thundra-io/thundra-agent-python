import mock
import pytest

class MockSubsegment(object):
    def __init__(self):
        self.annotations = {}
        self.metadata = {}
    
    def clear_annotations(self):
        self.annotations.clear()

    def put_annotation(self, key, value):
        self.annotations[key] = value
    
    def put_metadata(self, key, value):
        self.metadata[key] = value

@pytest.fixture()
def mocked_subsegment():
    return MockSubsegment()

@pytest.fixture()
def mocked_span():
    return mock.Mock(name='mocked_span')

@pytest.fixture()
def mocked_listener():
    return mock.Mock(name='mocked_listener')
