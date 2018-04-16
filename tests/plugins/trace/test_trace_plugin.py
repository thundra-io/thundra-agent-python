
import pytest
from thundra.plugins.trace.trace_plugin import TracePlugin
from thundra.thundra_agent import Thundra


def test_cold_starts(handler_with_apikey, mock_context, mock_event, environment_variables, monkeypatch):
    e_v = environment_variables
    e_v.start()
    monkeypatch.setattr(TracePlugin, 'IS_COLD_START', True)
    thundra, handler = handler_with_apikey

    trace_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is TracePlugin:
            trace_plugin = plugin

    handler(mock_event, mock_context)
    assert trace_plugin.trace_data['properties']['coldStart'] is 'true'

    handler(mock_event, mock_context)
    assert trace_plugin.trace_data['properties']['coldStart'] is 'false'
    e_v.stop()


@pytest.fixture
def thundra_with_profile(environment_variables_with_profile):
    e_v = environment_variables_with_profile
    e_v.start()
    thundra = Thundra('api key')
    e_v.stop()
    return thundra


@pytest.fixture
def handler_with_profile(thundra_with_profile):
    @thundra_with_profile.call
    def _handler(event, context):
        pass
    return thundra_with_profile, _handler


def test_when_app_profile_exists(handler_with_profile, mock_context, mock_event):

    thundra, handler = handler_with_profile

    trace_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is TracePlugin:
            trace_plugin = plugin

    handler(mock_event, mock_context)

    assert trace_plugin.trace_data['applicationProfile'] == 'profile'


def test_when_app_profile_not_exists(handler_with_apikey, mock_context, mock_event, environment_variables):
    e_v = environment_variables
    e_v.start()
    thundra, handler = handler_with_apikey

    trace_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is TracePlugin:
            trace_plugin = plugin

    handler(mock_event, mock_context)

    assert trace_plugin.trace_data['applicationProfile'] == ''

    e_v.stop()


def test_if_error_is_added_to_report(handler_with_exception, mock_context, mock_event, environment_variables):
    e_v = environment_variables
    e_v.start()
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
    assert 'hello' in trace_plugin.trace_data['auditInfo']['thrownError']['args']

    e_v.stop()


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
    duration_in_ms = int(duration * 1000)

    assert trace_plugin.trace_data['duration'] == duration_in_ms
    assert trace_plugin.trace_data['auditInfo']['openTimestamp'] == start_time
    assert trace_plugin.trace_data['auditInfo']['closeTimestamp'] == end_time

    assert trace_plugin.trace_data['applicationName'] == 'test_func'
    assert trace_plugin.trace_data['applicationId'] == 'test'
    assert trace_plugin.trace_data['applicationVersion'] == 'version'
    assert trace_plugin.trace_data['applicationType'] == 'python'

    assert trace_plugin.trace_data['contextName'] == 'test_func'
    assert trace_plugin.trace_data['auditInfo']['contextName'] == 'test_func'

    assert trace_plugin.trace_data['properties']['functionRegion'] == 'region'
    assert trace_plugin.trace_data['properties']['functionMemoryLimitInMB'] == '128'
