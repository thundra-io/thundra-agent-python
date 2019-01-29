import os
from thundra import constants
from thundra.plugins.trace import trace_support
from thundra.listeners import FilteringSpanListener, ErrorInjectorSpanListener, LatencyInjectorSpanListener

def test_create_empty_span_listener(monkeypatch):
    sl_env_var = 'FilteringSpanListener[]'
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_SPAN_LISTENER, sl_env_var)

    trace_support.parse_span_listeners()

    sl = trace_support.get_span_listeners()[0]

    assert type(sl) is FilteringSpanListener
    assert sl.listener is None
    assert sl.filterer is None

def test_create_span_listener_with_only_listener(monkeypatch):
    sl_env_var = 'FilteringSpanListener[listener=ErrorInjectorSpanListener,config.errorType=NameError,config.errorMessage="foo"]'
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_SPAN_LISTENER, sl_env_var)

    trace_support.parse_span_listeners()

    sl = trace_support.get_span_listeners()[0]

    assert type(sl) is FilteringSpanListener
    assert type(sl.listener) is ErrorInjectorSpanListener
    assert sl.listener.error_type is NameError
    assert sl.listener.error_message == 'foo'
    assert sl.filterer is None

def test_create_span_listener_with_only_filterer(monkeypatch):
    sl_env_var = 'FilteringSpanListener[filter.className=AWS-SQS,filter.domainName=Messaging,filter.tag.foo=bar]'
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
    sl_env_var = ('FilteringSpanListener[listener=ErrorInjectorSpanListener,config.errorType=NameError,'
                    'config.errorMessage="foo",config.injectOnFinish=true,config.injectCountFreq=3,'
                    'filter.className=AWS-SQS,filter.domainName=Messaging,filter.tag.foo=bar]')
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
    sl_env_var = ('FilteringSpanListener[listener=LatencyInjectorSpanListener,config.delay=370,'
                    'config.distribution=normal,config.sigma=73,config.variation=37,'
                    'filter1.className=AWS-SQS,filter1.domainName=Messaging,filter1.tag.foo=bar,'
                    'filter2.className=HTTP,filter2.operationName=http_request,filter2.tag.http.host=foobar.com]')
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
    sl_env_var = 'NonExistingSpanListener[]'
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_SPAN_LISTENER, sl_env_var)

    trace_support.parse_span_listeners()


    assert len(trace_support.get_span_listeners()) == 0