import json

from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.encoder import to_json
from catchpoint.listeners import *
from catchpoint.listeners.catchpoint_span_filterer import StandardSpanFilterer
from catchpoint.plugins.trace import trace_support


def test_create_empty_span_listener(empty_span_listener):
    sl_env_var = to_json(empty_span_listener)
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_SPAN_LISTENERCONFIG, sl_env_var)

    trace_support._parse_span_listeners()

    sl = trace_support.get_span_listeners()[0]

    assert type(sl) is FilteringSpanListener
    assert type(sl.listener) is ErrorInjectorSpanListener
    assert type(sl.filterer) is StandardSpanFilterer


def test_create_span_listener_with_only_listener(span_listener_with_one_listener):
    sl_env_var = to_json(span_listener_with_one_listener)
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_SPAN_LISTENERCONFIG, sl_env_var)

    trace_support._parse_span_listeners()

    sl = trace_support.get_span_listeners()[0]

    assert type(sl) is FilteringSpanListener
    assert type(sl.listener) is ErrorInjectorSpanListener
    assert sl.listener.error_type is NameError
    assert sl.listener.error_message == 'foo'
    assert type(sl.filterer) is StandardSpanFilterer


def test_create_span_listener_with_only_filterer(span_listener_with_one_filterer):
    sl_env_var = to_json(span_listener_with_one_filterer)
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_SPAN_LISTENERCONFIG, sl_env_var)

    trace_support._parse_span_listeners()

    sl = trace_support.get_span_listeners()[0]
    f = sl.filterer.span_filters[0]

    assert type(sl) is FilteringSpanListener
    assert sl.listener is None
    assert f.class_name == 'AWS-SQS'
    assert f.domain_name == 'Messaging'
    assert f.tags == {'foo': 'bar'}


def test_create_span_listener_with_filterer_and_listener(span_listener_with_filterer_and_listener):
    sl_env_var = to_json(span_listener_with_filterer_and_listener)
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_SPAN_LISTENERCONFIG, sl_env_var)

    trace_support._parse_span_listeners()

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


def test_create_span_listener_with_multiple_filter_and_listener(span_listener_with_multiple_filterers_and_listeners):
    sl_env_var = to_json(span_listener_with_multiple_filterers_and_listeners)
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_SPAN_LISTENERCONFIG, sl_env_var)

    trace_support._parse_span_listeners()

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


def test_with_non_existing_listener_type():
    sl_env_var = '{"type": "NonExistingSpanListener", "config": {"config": {}}}'
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_SPAN_LISTENERCONFIG, sl_env_var)

    trace_support._parse_span_listeners()

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
        ('CatchpointSpanListener', None),
        ('NonExistingListener', None),
    ]

    for case in map(prepare_case, cases):
        sl_class = trace_support._get_sl_class(case['class_name'])
        assert sl_class == case['class_type']
