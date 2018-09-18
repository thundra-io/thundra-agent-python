from thundra import constants
from thundra.plugins.trace.trace_plugin import TracePlugin
import os


def test_cold_starts(handler_with_apikey, mock_context, mock_event, monkeypatch):
    monkeypatch.setattr(TracePlugin, 'IS_COLD_START', True)
    monkeypatch.setitem(os.environ, constants.THUNDRA_APPLICATION_PROFILE, 'profile')
    thundra, handler = handler_with_apikey

    trace_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is TracePlugin:
            trace_plugin = plugin

    handler(mock_event, mock_context)
    assert trace_plugin.trace_data['properties']['coldStart'] is 'true'

    handler(mock_event, mock_context)
    assert trace_plugin.trace_data['properties']['coldStart'] is 'false'


def test_when_app_profile_exists(handler_with_profile, mock_context, mock_event):
    thundra, handler = handler_with_profile

    trace_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is TracePlugin:
            trace_plugin = plugin

    handler(mock_event, mock_context)

    assert trace_plugin.trace_data['applicationProfile'] == 'profile'


def test_when_app_profile_not_exists(handler_with_apikey, mock_context, mock_event):
    thundra, handler = handler_with_apikey

    trace_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is TracePlugin:
            trace_plugin = plugin

    handler(mock_event, mock_context)

    assert trace_plugin.trace_data['applicationProfile'] is ''


def test_if_error_is_added_to_report(handler_with_exception, mock_context, mock_event, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_APPLICATION_PROFILE, 'profile')
    thundra, handler = handler_with_exception

    trace_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is TracePlugin:
            trace_plugin = plugin

    try:
        handler(mock_event, mock_context)
    except Exception as e:
        pass

    assert trace_plugin.trace_data['thrownError'] == 'Exception'
    assert 'Exception' in trace_plugin.trace_data['errors']

    assert trace_plugin.trace_data['auditInfo']['thrownError']['errorType'] == 'Exception'


def test_report(handler_with_profile, mock_context, mock_event):
    thundra, handler = handler_with_profile

    trace_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is TracePlugin:
            trace_plugin = plugin

    handler(mock_event, mock_context)

    assert trace_plugin.trace_data['startTimestamp'] is not None
    assert trace_plugin.trace_data['endTimestamp'] is not None

    start_time = trace_plugin.trace_data['startTimestamp']
    end_time = trace_plugin.trace_data['endTimestamp']

    duration = end_time - start_time

    assert trace_plugin.trace_data['duration'] == duration
    assert trace_plugin.trace_data['auditInfo']['openTimestamp'] == start_time
    assert trace_plugin.trace_data['auditInfo']['closeTimestamp'] == end_time

    assert trace_plugin.trace_data['applicationName'] == 'test_func'
    assert trace_plugin.trace_data['applicationId'] == 'id'
    assert trace_plugin.trace_data['applicationVersion'] == 'function_version'
    assert trace_plugin.trace_data['applicationType'] == 'python'

    assert trace_plugin.trace_data['contextName'] == 'test_func'
    assert trace_plugin.trace_data['auditInfo']['contextName'] == 'test_func'

    assert trace_plugin.trace_data['properties']['functionRegion'] == 'region'
    assert trace_plugin.trace_data['properties']['functionMemoryLimitInMB'] == '128'
    assert trace_plugin.trace_data['properties']['timeout'] == 'false'


def test_if_request_response_is_skipped(handler_with_request_response_skip, mock_context, mock_event):
    thundra, handler = handler_with_request_response_skip

    trace_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is TracePlugin:
            trace_plugin = plugin

    handler(mock_event, mock_context)

    assert trace_plugin.trace_data['properties']['request'] is None
    assert trace_plugin.trace_data['properties']['response'] is None
