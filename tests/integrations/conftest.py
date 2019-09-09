import pytest
import mock

from thundra.opentracing.tracer import ThundraTracer
from thundra.application_support import parse_application_info

def mock_tracer_get_call(self):
    return True


@pytest.fixture(scope="module", autouse=True)
def mock_get_active_span():
    with mock.patch('thundra.opentracing.tracer.ThundraTracer.get_active_span', mock_tracer_get_call):
        yield

class MockContext:
    def __init__(self, f_name='test_func'):
        self.function_name = f_name

@pytest.fixture(scope="module", autouse=True)
def mock_parse_application_info():
    parse_application_info(MockContext())


