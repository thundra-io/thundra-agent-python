import os
from thundra import constants
from thundra.plugins.trace import trace_support
from thundra.listeners import *
from thundra.listeners.thundra_span_filterer import StandardSpanFilterer

def test_create_empty_span_listener(monkeypatch):
    sl_env_var = '{"type":"FilteringSpanListener", "config": {"listener": {"type": "ErrorInjectorSpanListener"}}}'
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_SPAN_LISTENER, sl_env_var)

    trace_support.parse_span_listeners()

    sl = trace_support.get_span_listeners()[0]

    assert type(sl) is FilteringSpanListener
    assert type(sl.listener) is ErrorInjectorSpanListener
    assert type(sl.filterer) is StandardSpanFilterer

def test_create_span_listener_with_only_listener(monkeypatch):
    sl_env_var = '{"type": "FilteringSpanListener", "config": { "listener": {"type": "ErrorInjectorSpanListener", "config": {"errorType":"NameError","errorMessage":"foo"}}}}'
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_SPAN_LISTENER, sl_env_var)

    trace_support.parse_span_listeners()

    sl = trace_support.get_span_listeners()[0]

    assert type(sl) is FilteringSpanListener
    assert type(sl.listener) is ErrorInjectorSpanListener
    assert sl.listener.error_type is NameError
    assert sl.listener.error_message == 'foo'
    assert type(sl.filterer) is StandardSpanFilterer

def test_create_span_listener_with_only_filterer(monkeypatch):
    sl_env_var = '{"type": "FilteringSpanListener", "config": { "filters": [ { "className":"AWS-SQS","domainName":"Messaging","tags":{"foo": "bar"}}]}}'
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_SPAN_LISTENER, sl_env_var)

    trace_support.parse_span_listeners()

    sl = trace_support.get_span_listeners()[0]
    f = sl.filterer.span_filters[0]

    assert type(sl) is FilteringSpanListener
    assert sl.listener is None
    assert f.class_name == 'AWS-SQS'
    assert f.domain_name == 'Messaging'
    assert f.tags == {'foo': 'bar'}

def test_create_span_listener_with_filterer_and_listener(monkeypatch):
    sl_env_var = ('{"type": "FilteringSpanListener", "config": {"listener": {"type": "ErrorInjectorSpanListener", "config": {"errorType": "NameError",'
                    '"errorMessage":"foo", "injectOnFinish": true, "injectCountFreq":3}},'
                    '"filters": [{"className":"AWS-SQS", "domainName":"Messaging", "tags": {"foo":"bar"}}]}}')
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_SPAN_LISTENER, sl_env_var)

    trace_support.parse_span_listeners()

    sl = trace_support.get_span_listeners()[0]
    f = sl.filterer.span_filters[0]

    assert type(sl) is FilteringSpanListener
    assert type(sl.listener) is ErrorInjectorSpanListener
    assert sl.listener.error_type is NameError
    assert sl.listener.error_message == 'foo'
    assert sl.listener.inject_on_finish
    assert sl.listener.inject_count_freq
    
    assert f.class_name == 'AWS-SQS'
    assert f.domain_name == 'Messaging'
    assert f.tags == {'foo': 'bar'}

def test_create_span_listener_with_multiple_filter_and_listener(monkeypatch):
    sl_env_var = ('{"type": "FilteringSpanListener", "config": {"listener": {"type": "LatencyInjectorSpanListener","config": {"delay":370,'
                    '"distribution":"normal", "sigma": 73, "variation":37}},'
                    '"filters": [{"className":"AWS-SQS", "domainName": "Messaging", "tags": {"foo":"bar"}},'
                    '{"className":"HTTP", "operationName": "http_request", "tags": {"http.host": "foobar.com"}}]}}')
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_SPAN_LISTENER, sl_env_var)

    trace_support.parse_span_listeners()

    sl = trace_support.get_span_listeners()[0]
    f1 = sl.filterer.span_filters[0]
    f2 = sl.filterer.span_filters[1]

    assert type(sl) is FilteringSpanListener
    assert type(sl.listener) is LatencyInjectorSpanListener
    assert sl.listener.delay == 370
    assert sl.listener.distribution == 'normal'
    assert sl.listener.sigma == 73
    assert sl.listener.variation == 37
    
    assert f1.class_name == 'AWS-SQS'
    assert f1.domain_name == 'Messaging'
    assert f1.tags == {'foo': 'bar'}

    assert f2.class_name == 'HTTP'
    assert f2.operation_name == 'http_request'
    assert f2.tags == {'http.host': 'foobar.com'}

def test_with_non_existing_listener_type(monkeypatch):
    sl_env_var = '{"type": "NonExistingSpanListener", "config": {"config": {}}}'
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_SPAN_LISTENER, sl_env_var)

    trace_support.parse_span_listeners()


    assert len(trace_support.get_span_listeners()) == 0


def test_get_sl_class():
    def prepare_case(case):
        return {
            'class_name': case[0],
            'class_type': case[1],
        }
    
    cases = [
        ('ErrorInjectorSpanListener', ErrorInjectorSpanListener),
        ('LatencyInjectorSpanListener', LatencyInjectorSpanListener),
        ('FilteringSpanListener', FilteringSpanListener),
        ('AWSXRayListener', AWSXRayListener),
        ('ThundraSpanListener', None),
        ('NonExistingListener', None),
    ] 

    for case in map(prepare_case, cases):
        sl_class = trace_support._get_sl_class(case['class_name'])
        assert sl_class == case['class_type']

def test_xray_sl_added(monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_TRACE_ENABLE_XRAY, 'true')

    trace_support.parse_span_listeners()
    span_listeners = trace_support.get_span_listeners()
    xray_listener = span_listeners[0]

    assert len(span_listeners) == 1
    assert type(xray_listener) == AWSXRayListener

def test_xray_sl_not_added(monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_TRACE_ENABLE_XRAY, 'false')

    trace_support.parse_span_listeners()
    span_listeners = trace_support.get_span_listeners()

    assert len(span_listeners) == 0
    
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_TRACE_ENABLE_XRAY, 'foo')

    trace_support.parse_span_listeners()
    span_listeners = trace_support.get_span_listeners()

    assert len(span_listeners) == 0
    
    monkeypatch.delitem(os.environ, constants.THUNDRA_LAMBDA_TRACE_ENABLE_XRAY)

    trace_support.parse_span_listeners()
    span_listeners = trace_support.get_span_listeners()

    assert len(span_listeners) == 0
