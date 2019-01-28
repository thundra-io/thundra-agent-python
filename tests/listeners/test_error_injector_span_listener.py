from thundra.listeners import ErrorInjectorSpanListener
from thundra.opentracing.tracer import ThundraTracer

def test_frequency():
    try:
        tracer = ThundraTracer.get_instance()
        with tracer.start_active_span(operation_name='foo', finish_on_close=True) as scope:
            span = scope.span
            
            esl = ErrorInjectorSpanListener(
                inject_count_freq=3
            )

            for i in range(10):
                esl.on_span_finished(span)

            assert esl._counter == 0

            err_count = 0
            for i in range(33):
                try:
                    esl.on_span_started(span)
                except Exception:
                    err_count += 1
                    pass

            assert esl._counter == 33
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
            esl = ErrorInjectorSpanListener(
                error_type=error_type,
                error_message=error_message,
                inject_on_finish=False
            )

            error_on_started = None
            try:
                esl.on_span_started(span)
            except Exception as e:
                error_on_started = e
            
            assert error_on_started is not None
            assert type(error_on_started) is error_type
            assert str(error_on_started) == error_message


            error_on_finished = None
            try:
                esl.on_span_finished(span)
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
        'errorMessage': '"You have a very funny name!"',
        'injectOnFinish': 'true',
        'injectCountFreq': '7',
        'foo': 'bar',
    }

    esl = ErrorInjectorSpanListener.from_config(config)

    assert esl.error_type is NameError
    assert esl.error_message == "You have a very funny name!"
    assert esl.inject_on_finish
    assert esl.inject_count_freq == 7
