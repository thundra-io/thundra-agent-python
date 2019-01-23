from thundra.listeners.error_injector_span_listener import ErrorInjectorSpanListener
from thundra.opentracing.tracer import ThundraTracer

def test_frequency():
    tracer = ThundraTracer.get_instance()
    with tracer.start_active_span(operation_name='foo', finish_on_close=True) as scope:
        span = scope.span
        
        sl = ErrorInjectorSpanListener(
            inject_on_finish=False,
            inject_count_freq=3
        )

        for i in range(10):
            sl.on_span_finished(span)

        assert sl._counter == 0

        err_count = 0
        for i in range(33):
            try:
                sl.on_span_started(span)
            except Exception:
                err_count += 1
                pass

        assert sl._counter == 33
        assert err_count == 11