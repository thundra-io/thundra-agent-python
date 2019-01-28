import time
import mock
from thundra.listeners import LatencyInjectorSpanListener
from thundra.opentracing.tracer import ThundraTracer

@mock.patch('time.sleep')
def test_delay_amount(mocked_time):
    try:
        tracer = ThundraTracer.get_instance()
        with tracer.start_active_span(operation_name='foo', finish_on_close=True) as scope:
            span = scope.span
            delay = 370
            sl = LatencyInjectorSpanListener(delay=delay)

            sl.on_span_started(span)
            
            called_delay = (mocked_time.call_args[0][0]) * 1000

            assert delay == called_delay
            assert sl.delay == delay
            assert sl.distribution == 'uniform'
            assert sl.variation == 0
    except Exception:
        raise
    finally:
        tracer.clear()

@mock.patch('time.sleep')
def test_delay_variaton(mocked_time):
    try:
        tracer = ThundraTracer.get_instance()
        with tracer.start_active_span(operation_name='foo', finish_on_close=True) as scope:
            span = scope.span
            delay = 100
            variation = 50
            sl = LatencyInjectorSpanListener(delay=delay, variation=variation)

            sl.on_span_started(span)
            
            called_delay = (mocked_time.call_args[0][0]) * 1000

            assert called_delay <= delay+variation and called_delay >= delay-variation
            assert sl.delay == delay
            assert sl.variation == variation
            assert sl.distribution == 'uniform'
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

    sl = LatencyInjectorSpanListener.from_config(config)

    assert sl.delay == 370
    assert sl.sigma == 73
    assert sl.variation == 37
    assert sl.distribution == 'normal'
