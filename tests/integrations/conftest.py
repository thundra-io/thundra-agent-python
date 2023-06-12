import mock
import pytest

from catchpoint.context.execution_context_manager import ExecutionContextManager
from catchpoint.opentracing.tracer import CatchpointTracer


@pytest.fixture(autouse=True)
def start_root_span():
    tracer = CatchpointTracer.get_instance()
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
    with mock.patch('catchpoint.opentracing.tracer.CatchpointTracer.get_active_span', mock_tracer_get_call):
        yield
