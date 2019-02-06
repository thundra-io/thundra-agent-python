import mock
import pytest

class MockSubsegment(object):
    def __init__(self):
        self.annotations = {}
    
    def clear_annotations(self):
        self.annotations.clear()

    def put_annotation(self, key, value):
        self.annotations[key] = value

@pytest.fixture()
def mocked_subsegment():
    return MockSubsegment()

@pytest.fixture()
def mocked_span():
    m = mock.Mock(name='mocked_span')
    m.context = mock.Mock(name='mocked_span_context')

    m.context.trace_id = 'mocked_trace_id'
    m.context.transaction_id = 'mocked_transaction_id'
    m.context.span_id = 'mocked_span_id'
    m.context.parent_span_id = 'mocked_parent_span_id'

    def get_duration():
        return 37
    m.get_duration = get_duration
    m.class_name = 'mocked_class_name'
    m.domain_name = 'mocked_domain_name'
    m.operation_name = 'mocked_operation_name'
    m.start_time = 37
    m.finish_time = 73
    
    return m

@pytest.fixture()
def mocked_listener():
    return mock.Mock(name='mocked_listener')
