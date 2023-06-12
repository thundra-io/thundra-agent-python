import time
import mock
import pytest
from catchpoint.opentracing.tracer import CatchpointTracer


@pytest.fixture
def span():
    tracer = CatchpointTracer.get_instance()
    scope = tracer.start_active_span(operation_name='operation name')
    return scope.span


@mock.patch('catchpoint.opentracing.recorder.CatchpointRecorder')
@mock.patch('opentracing.scope_managers.ThreadLocalScopeManager')
def test_start_active_span(mock_recorder, mock_scope_manager, span):
    tracer = CatchpointTracer.get_instance()
    start_time = time.time()
    with tracer.start_active_span(operation_name='test', child_of=span, start_time=start_time) as active_scope:
        active_span = active_scope.span

        assert active_span.operation_name == 'test'
        assert active_span.start_time == start_time
        assert active_span.context.parent_span_id == span.context.span_id
        assert active_span.context.trace_id == span.context.trace_id

        mock_scope_manager.activate.assert_called_once
        mock_recorder.record.assert_called_once


@mock.patch('catchpoint.opentracing.recorder.CatchpointRecorder')
def test_start_span(mock_recorder, span):
    tracer = CatchpointTracer.get_instance()
    start_time = time.time()
    with tracer.start_span(operation_name='test', child_of=span, start_time=start_time) as active_span:
        assert active_span.operation_name == 'test'
        assert active_span.start_time == start_time
        assert active_span.context.parent_span_id == span.context.span_id
        assert active_span.context.trace_id == span.context.trace_id

        mock_recorder.record.assert_called_once



