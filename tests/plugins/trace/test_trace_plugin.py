from thundra import constants
from thundra.plugins.trace.trace_plugin import TracePlugin
import os



def test_when_app_stage_exists(handler_with_profile, mock_context, mock_event):
    thundra, handler = handler_with_profile

    trace_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is TracePlugin:
            trace_plugin = plugin

    handler(mock_event, mock_context)

    assert trace_plugin.trace_data['applicationStage'] == 'dev'


def test_when_app_stage_not_exists(handler_with_apikey, mock_context, mock_event):
    thundra, handler = handler_with_apikey

    trace_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is TracePlugin:
            trace_plugin = plugin

    handler(mock_event, mock_context)

    assert trace_plugin.trace_data['applicationStage'] is ''


def test_if_error_is_added_to_report(handler_with_exception, mock_context, mock_event, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_APPLICATION_STAGE, 'dev')
    thundra, handler = handler_with_exception

    trace_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is TracePlugin:
            trace_plugin = plugin

    try:
        handler(mock_event, mock_context)
    except Exception as e:
        pass

    assert trace_plugin.trace_data['tags']['error'] == True

    assert trace_plugin.trace_data['tags']['error.kind'] == 'Exception'
    assert 'hello' in trace_plugin.trace_data['tags']['error.message']


def test_report(handler_with_profile, mock_context, mock_event):
    thundra, handler = handler_with_profile

    trace_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is TracePlugin:
            trace_plugin = plugin

    handler(mock_event, mock_context)

    assert trace_plugin.trace_data['startTimestamp'] is not None
    assert trace_plugin.trace_data['finishTimestamp'] is not None

    start_time = trace_plugin.trace_data['startTimestamp']
    end_time = trace_plugin.trace_data['finishTimestamp']

    duration = end_time - start_time

    assert trace_plugin.trace_data['duration'] == duration

    assert trace_plugin.trace_data['applicationName'] == 'test_func'
    assert trace_plugin.trace_data['applicationId'] == 'id'
    assert trace_plugin.trace_data['applicationVersion'] == 'function_version'
    assert trace_plugin.trace_data['applicationRuntime'] == 'python'

    assert trace_plugin.trace_data['tags']['aws.lambda.memory.limit'] == '128'

