from thundra.listeners import ErrorInjectorSpanListener
from thundra.opentracing.tracer import ThundraTracer

def test_frequency():
    try:
        tracer = ThundraTracer.get_instance()
        with tracer.start_active_span(operation_name='foo', finish_on_close=True) as scope:
            span = scope.span
            
            sl = ErrorInjectorSpanListener(
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
    except Exception:
        raise
    finally:
        tracer.clear()

def test_err_type_and_message():
    try:
        tracer = ThundraTracer.get_instance()
        with tracer.start_active_span(operation_name='foo', finish_on_close=True) as scope:
            span = scope.span
            
            error_type = NameError
            error_message = "Your name is not good for this mission!"
            sl = ErrorInjectorSpanListener(
                error_type=error_type,
                error_message=error_message,
                inject_on_finish=False
            )

            error_on_started = None
            try:
                sl.on_span_started(span)
            except Exception as e:
                error_on_started = e
            
            assert error_on_started is not None
            assert type(error_on_started) is error_type
            assert str(error_on_started) == error_message


            error_on_finished = None
            try:
                sl.on_span_finished(span)
            except Exception as e:
                error_on_finished = e
            
            assert error_on_finished is None
    except Exception:
        raise
    finally:
        tracer.clear()

def test_create_from_config():
    config = {
        'errorType': 'NameError',
        'errorMessage': '"Your name is not good for this mission!"',
        'injectOnFinish': 'true',
        'injectCountFreq': '7',
        'foo': 'bar',
    }

    sl = ErrorInjectorSpanListener.from_config(config)

    assert sl.error_type is NameError
    assert sl.error_message == "Your name is not good for this mission!"
    assert sl.inject_on_finish
    assert sl.inject_count_freq == 7
