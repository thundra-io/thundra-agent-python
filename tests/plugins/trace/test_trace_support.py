import os
from thundra import constants
from thundra.plugins.trace import trace_support
from thundra.listeners import *

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

def test_get_class_and_config_parts():
    def prepare_case(case):
        return {
            'val': case[0],
            'listener': case[1],
            'config': case[2],
        }

    cases = [
        ('', None, None),
        ('dummy_listener[]','dummy_listener',''),
        ('dummy_listener[a=a,b=b,c=c]','dummy_listener','a=a,b=b,c=c'),
        ('dummy_listener[a=a, b=b, c=c]','dummy_listener','a=a, b=b, c=c'),
        ('dummy_listener[a=b.c,b=c.d,c=d.e.f]','dummy_listener','a=b.c,b=c.d,c=d.e.f'),
        ('dummy_listener_2[a=1,b=2,c=3]','dummy_listener_2','a=1,b=2,c=3'),
        ('dummy_listener[?!./+-,;:]','dummy_listener','?!./+-,;:'),
        ('dummy_listener[?!./+-,;:]','dummy_listener','?!./+-,;:'),
        ('foo[bar]', 'foo', 'bar'),
        ('37[73]', '37', '73'),
        ('[foo]', None, None),
        ('//73%37![==,==,==]', None, None),
    ]

    for case in map(prepare_case, cases):
        listener, config = trace_support._get_class_and_config_parts(case['val'])
        assert listener == case['listener']
        assert config == case['config']

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


def test_parse_config():
    cases = [
        {
            'config_str': '',
            'config': {}
        },
        {
            'config_str': 'foobar',
            'config': {}
        },
        {
            'config_str': 'a=1,b=',
            'config': {
                'a': '1',
                'b': '',
            }
        },
        {
            'config_str': 'a=1,b=2,c=3',
            'config': {
                'a': '1',
                'b': '2',
                'c': '3',
            }
        },
        {
            'config_str': 'listener=SampleListener, config.param1=val1, config.param2=val2',
            'config': {
                'listener': 'SampleListener',
                'config.param1': 'val1',
                'config.param2': 'val2',
            }
        },
        {
            'config_str': 'listener=boto3.exceptions.Boto3Error,foo_bar=foo-bar',
            'config': {
                'listener': 'boto3.exceptions.Boto3Error',
                'foo_bar': 'foo-bar',
            }
        },
        {
            'config_str': 'listener=boto3.exceptions.Boto3Error,foo_bar=foo-bar',
            'config': {
                'listener': 'boto3.exceptions.Boto3Error',
                'foo_bar': 'foo-bar',
            }
        },
    ]

    for case in cases:
        config = trace_support._parse_config(case['config_str'])
        assert config == case['config']
