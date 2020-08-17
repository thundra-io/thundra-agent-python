import mock
import pytest

from thundra.context.execution_context_manager import ExecutionContextManager
from thundra.opentracing.tracer import ThundraTracer


@pytest.fixture(autouse=True)
def start_root_span():
    tracer = ThundraTracer.get_instance()
    execution_context = ExecutionContextManager.get()
    tracer.start_active_span(operation_name="test",
                             finish_on_close=False,
                             trace_id="test-trace-id",
                             transaction_id="test-transaction-id",
                             execution_context=execution_context)


def mock_tracer_get_call(self):
    return True


@pytest.fixture(scope="module", autouse=True)
def mock_get_active_span():
    with mock.patch('thundra.opentracing.tracer.ThundraTracer.get_active_span', mock_tracer_get_call):
        yield
