import os
from thundra.plugins.trace.lambda_trace_plugin import LambdaTracePlugin
from thundra import constants


def test_when_app_stage_exists(handler_with_profile, mock_context, mock_event):
    thundra, handler = handler_with_profile

    trace_plugin = None
    for plugin in thundra.plugins:
        if isinstance(plugin, LambdaTracePlugin):
            trace_plugin = plugin

    handler(mock_event, mock_context)

    assert trace_plugin.trace_data['applicationStage'] == 'dev'


def test_when_app_stage_not_exists(handler, mock_context, mock_event):
    thundra, handler = handler

    trace_plugin = None
    for plugin in thundra.plugins:
        if isinstance(plugin, LambdaTracePlugin):
            trace_plugin = plugin

    handler(mock_event, mock_context)

    assert trace_plugin.trace_data['applicationStage'] is ''


def test_report(handler_with_profile, mock_context, mock_event):
    thundra, handler = handler_with_profile

    trace_plugin = None
    for plugin in thundra.plugins:
        if isinstance(plugin, LambdaTracePlugin):
            trace_plugin = plugin

    handler(mock_event, mock_context)

    assert trace_plugin.trace_data['startTimestamp'] is not None
    assert trace_plugin.trace_data['finishTimestamp'] is not None

    start_time = trace_plugin.trace_data['startTimestamp']
    end_time = trace_plugin.trace_data['finishTimestamp']

    duration = end_time - start_time

    assert trace_plugin.trace_data['duration'] == duration

    assert trace_plugin.trace_data['applicationName'] == 'test_func'
    assert trace_plugin.trace_data['applicationId'] == 'aws:lambda:us-west-2:123456789123:test'
    assert trace_plugin.trace_data['applicationInstanceId'] == 'id'
    assert trace_plugin.trace_data['applicationVersion'] == 'function_version'
    assert trace_plugin.trace_data['applicationRuntime'] == 'python'


def test_invocation_support_error_set_to_root_span(handler_with_user_error, mock_context, mock_event, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_APPLICATION_STAGE, 'dev')
    thundra, handler = handler_with_user_error

    trace_plugin = None
    for plugin in thundra.plugins:
        if isinstance(plugin, LambdaTracePlugin):
            trace_plugin = plugin

    handler(mock_event, mock_context)

    assert trace_plugin.root_span.get_tag('error') is True
    assert trace_plugin.root_span.get_tag('error.kind') == 'Exception'
    assert trace_plugin.root_span.get_tag('error.message') == 'test'
