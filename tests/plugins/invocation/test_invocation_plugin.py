import os

from thundra import constants
from thundra.plugins.invocation.invocation_plugin import InvocationPlugin


def test_cold_starts(handler_with_apikey, mock_context, mock_event, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_APPLICATION_PROFILE, 'profile')
    monkeypatch.setattr(InvocationPlugin, 'IS_COLD_START', True)
    thundra, handler = handler_with_apikey

    invocation_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is InvocationPlugin:
            invocation_plugin = plugin

    handler(mock_event, mock_context)
    assert invocation_plugin.invocation_data['coldStart'] is True

    handler(mock_event, mock_context)
    assert invocation_plugin.invocation_data['coldStart'] is False


def test_if_error_is_added_to_report(handler_with_exception, mock_context, mock_event, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_APPLICATION_PROFILE, 'profile')
    thundra, handler = handler_with_exception

    invocation_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is InvocationPlugin:
            invocation_plugin = plugin

    try:
        handler(mock_event, mock_context)
    except Exception as e:
        pass

    assert invocation_plugin.invocation_data['erroneous'] is True
    assert invocation_plugin.invocation_data['errorType'] == 'Exception'
    assert invocation_plugin.invocation_data['errorMessage'] == 'hello'


def test_report(handler_with_profile, mock_context, mock_event):

    thundra, handler = handler_with_profile

    invocation_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is InvocationPlugin:
            invocation_plugin = plugin

    handler(mock_event, mock_context)

    assert invocation_plugin.invocation_data['startTimestamp'] is not None
    assert invocation_plugin.invocation_data['endTimestamp'] is not None

    start_time = invocation_plugin.invocation_data['startTimestamp']
    end_time = invocation_plugin.invocation_data['endTimestamp']

    duration = end_time - start_time
    duration_in_ms = int(duration * 1000)

    assert invocation_plugin.invocation_data['duration'] == duration_in_ms
    assert invocation_plugin.invocation_data['erroneous'] is False
    assert invocation_plugin.invocation_data['errorType'] == ''
    assert invocation_plugin.invocation_data['errorMessage'] == ''

    assert invocation_plugin.invocation_data['region'] == 'region'
    assert invocation_plugin.invocation_data['memorySize'] == 128


def test_when_app_profile_exists(handler_with_profile, mock_context, mock_event):

    thundra, handler = handler_with_profile

    invocation_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is InvocationPlugin:
            invocation_plugin = plugin

    handler(mock_event, mock_context)

    assert invocation_plugin.invocation_data['applicationProfile'] == 'profile'


def test_when_app_profile_not_exists(handler_with_apikey, mock_context, mock_event):
    thundra, handler = handler_with_apikey

    invocation_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is InvocationPlugin:
            invocation_plugin = plugin

    handler(mock_event, mock_context)

    assert invocation_plugin.invocation_data['applicationProfile'] is ''
