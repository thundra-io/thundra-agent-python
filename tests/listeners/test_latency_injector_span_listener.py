import mock
from catchpoint.listeners import LatencyInjectorSpanListener
from catchpoint.opentracing.tracer import CatchpointTracer

@mock.patch('time.sleep')
def test_delay_amount(mocked_time):
    try:
        tracer = CatchpointTracer.get_instance()
        with tracer.start_active_span(operation_name='foo', finish_on_close=True) as scope:
            span = scope.span
            delay = 370
            lsl = LatencyInjectorSpanListener(delay=delay)

            lsl.on_span_started(span)
            
            called_delay = (mocked_time.call_args[0][0]) * 1000

            assert delay == called_delay
            assert lsl.delay == delay
            assert lsl.distribution == 'uniform'
            assert lsl.variation == 0
    except Exception:
        raise
    finally:
        tracer.clear()

@mock.patch('time.sleep')
def test_delay_variaton(mocked_time):
    try:
        tracer = CatchpointTracer.get_instance()
        with tracer.start_active_span(operation_name='foo', finish_on_close=True) as scope:
            span = scope.span
            delay = 100
            variation = 50
            lsl = LatencyInjectorSpanListener(delay=delay, variation=variation)

            lsl.on_span_started(span)
            
            called_delay = (mocked_time.call_args[0][0]) * 1000

            assert called_delay <= delay+variation and called_delay >= delay-variation
            assert lsl.delay == delay
            assert lsl.variation == variation
            assert lsl.distribution == 'uniform'
    except Exception:
        raise
    finally:
        tracer.clear()

def test_create_from_config():
    config = {
        'delay': '370',
        'sigma': '73',
        'distribution': 'normal',
        'variation': '37',
    }

    lsl = LatencyInjectorSpanListener.from_config(config)

    assert lsl.delay == 370
    assert lsl.sigma == 73
    assert lsl.variation == 37
    assert lsl.distribution == 'normal'

def test_create_from_config_with_type_errors():
    config = {
        'delay': 'foo',
        'sigma': 'bar',
        'distribution': 12,
        'variation': 'foobar',
    }

    lsl = LatencyInjectorSpanListener.from_config(config)

    assert lsl.delay == 0
    assert lsl.sigma == 0
    assert lsl.variation == 0
    assert lsl.distribution == 'uniform'
