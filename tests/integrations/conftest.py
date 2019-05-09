import pytest
import mock

from thundra.opentracing.tracer import ThundraTracer


def mock_tracer_get_call(self):
    return True


@pytest.fixture(scope="module", autouse=True)
def mock_get_active_span():
    with mock.patch('thundra.opentracing.tracer.ThundraTracer.get_active_span', mock_tracer_get_call):
        yield
