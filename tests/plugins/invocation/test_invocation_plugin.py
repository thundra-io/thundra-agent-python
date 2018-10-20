import os

from thundra import constants
from thundra.plugins.invocation.invocation_plugin import InvocationPlugin


def test_cold_starts(handler, mock_context, mock_event, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_APPLICATION_STAGE, 'dev')
    thundra, handler = handler

    invocation_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is InvocationPlugin:
            invocation_plugin = plugin

    handler(mock_event, mock_context)
    assert invocation_plugin.invocation_data['coldStart'] is True
    assert invocation_plugin.invocation_data['tags']['aws.lambda.invocation.cold_start'] is True

    handler(mock_event, mock_context)
    assert invocation_plugin.invocation_data['coldStart'] is False
    assert invocation_plugin.invocation_data['tags']['aws.lambda.invocation.cold_start'] is False


def test_if_error_is_added_to_report(handler_with_exception, mock_context, mock_event, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_APPLICATION_STAGE, 'dev')
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
    assert invocation_plugin.invocation_data['finishTimestamp'] is not None

    start_time = invocation_plugin.invocation_data['startTimestamp']
    end_time = invocation_plugin.invocation_data['finishTimestamp']

    duration = int(end_time - start_time)

    assert invocation_plugin.invocation_data['duration'] == duration
    assert invocation_plugin.invocation_data['erroneous'] is False
    assert invocation_plugin.invocation_data['errorType'] == ''
    assert invocation_plugin.invocation_data['errorMessage'] == ''

    assert invocation_plugin.invocation_data['functionRegion'] == 'region'


def test_tags_error(handler_with_exception, mock_context, mock_event, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_APPLICATION_STAGE, 'dev')
    thundra, handler = handler_with_exception

    invocation_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is InvocationPlugin:
            invocation_plugin = plugin

    try:
        handler(mock_event, mock_context)
    except Exception as e:
        pass

    assert invocation_plugin.invocation_data['tags']['error'] is True
    assert invocation_plugin.invocation_data['tags']['error.kind'] == 'Exception'
    assert invocation_plugin.invocation_data['tags']['error.message'] == 'hello'


def test_aws_related_tags(handler_with_profile, mock_context, mock_event, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_APPLICATION_STAGE, 'dev')
    thundra, handler = handler_with_profile

    invocation_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is InvocationPlugin:
            invocation_plugin = plugin

    try:
        response = handler(mock_event, mock_context)
    except Exception as e:
        pass

    assert invocation_plugin.invocation_data['tags']['aws.lambda.arn'] == 'invoked_function_arn'
    assert invocation_plugin.invocation_data['tags']['aws.lambda.memory.limit'] == '128'
    assert invocation_plugin.invocation_data['tags']['aws.lambda.log_group_name'] == 'log_group_name'
    assert invocation_plugin.invocation_data['tags']['aws.lambda.log_stream_name'] == 'log_stream_name[]id'
    assert invocation_plugin.invocation_data['tags']['aws.lambda.invocation.request_id'] == 'aws_request_id'


def test_when_app_stage_exists(handler_with_profile, mock_context, mock_event):

    thundra, handler = handler_with_profile

    invocation_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is InvocationPlugin:
            invocation_plugin = plugin

    handler(mock_event, mock_context)

    assert invocation_plugin.invocation_data['applicationStage'] == 'dev'


def test_when_app_stage_not_exists(handler, mock_context, mock_event):
    thundra, handler = handler

    invocation_plugin = None
    for plugin in thundra.plugins:
        if type(plugin) is InvocationPlugin:
            invocation_plugin = plugin

    handler(mock_event, mock_context)

    assert invocation_plugin.invocation_data['applicationStage'] is ''
