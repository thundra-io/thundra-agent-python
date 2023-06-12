import time
import mock
from catchpoint.opentracing.tracer import CatchpointTracer


def test_set_operation_name():
    tracer = CatchpointTracer.get_instance()
    with tracer.start_active_span(operation_name='operation name', finish_on_close=True) as scope:
        span = scope.span
        assert span.operation_name == 'operation name'

        span.set_operation_name('second operation name')
        assert span.operation_name == 'second operation name'


def test_tag():
    tracer = CatchpointTracer.get_instance()
    with tracer.start_active_span(operation_name='operation name', finish_on_close=True) as scope:
        span = scope.span
        assert bool(span.tags) == False

        span.set_tag('tag', 'test')
        tag = span.get_tag('tag')
        assert tag == 'test'


@mock.patch('catchpoint.opentracing.recorder.CatchpointRecorder')
def test_finish(mock_recorder):
    tracer = CatchpointTracer.get_instance()
    with tracer.start_active_span(operation_name='operation name', finish_on_close=True) as scope:
        span = scope.span
        assert span.finish_time == 0

        end_time = time.time()
        span.finish(f_time=end_time)

        duration = end_time - span.start_time
        assert span.get_duration() == duration

        mock_recorder.record.assert_called_once


def test_log_kv():
    tracer = CatchpointTracer.get_instance()
    with tracer.start_active_span(operation_name='operation name', finish_on_close=True) as scope:
        span = scope.span
        assert len(span.logs) == 0

        t = time.time()
        span.log_kv({
            'log1': 'log',
            'log2': 2,
        }, t)
        span.finish()

        assert len(span.logs) == 1
        log = span.logs[0]
        assert log['timestamp'] == t

        assert log['log1'] == 'log'
        assert log['log2'] == 2


def test_baggage_item():
    tracer = CatchpointTracer.get_instance()
    with tracer.start_active_span(operation_name='operation name', finish_on_close=True) as scope:
        span = scope.span
        assert bool(span.context.baggage) == False

        span.set_baggage_item('baggage', 'item')
        assert span.get_baggage_item('baggage') == 'item'
        span.finish()
