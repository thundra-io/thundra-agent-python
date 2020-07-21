import os

from thundra.plugins.invocation.invocation_plugin import InvocationPlugin
from thundra.config.config_provider import ConfigProvider
from thundra.config import config_names


def test_coldstarts(handler, mock_context, mock_event):
    ConfigProvider.set(config_names.THUNDRA_APPLICATION_STAGE, 'dev')

    thundra, handler = handler

    invocation_plugin = None
    for plugin in thundra.plugins:
        if isinstance(plugin, InvocationPlugin):
            invocation_plugin = plugin

    handler(mock_event, mock_context)
    assert invocation_plugin.invocation_data['coldStart'] is True
    assert invocation_plugin.invocation_data['tags']['aws.lambda.invocation.coldstart'] is True

    handler(mock_event, mock_context)
    assert invocation_plugin.invocation_data['coldStart'] is False
    assert invocation_plugin.invocation_data['tags']['aws.lambda.invocation.coldstart'] is False


def test_if_error_is_added_to_report(handler_with_exception, mock_context, mock_event):
    ConfigProvider.set(config_names.THUNDRA_APPLICATION_STAGE, 'dev')
    thundra, handler = handler_with_exception

    invocation_plugin = None
    for plugin in thundra.plugins:
        if isinstance(plugin, InvocationPlugin):
            invocation_plugin = plugin

    try:
        handler(mock_event, mock_context)
    except Exception:
        pass

    assert invocation_plugin.invocation_data['erroneous'] is True
    assert invocation_plugin.invocation_data['errorType'] == 'Exception'
    assert invocation_plugin.invocation_data['errorMessage'] == 'hello'


def test_report(handler_with_profile, mock_context, mock_event):
    thundra, handler = handler_with_profile

    invocation_plugin = None
    for plugin in thundra.plugins:
        if isinstance(plugin, InvocationPlugin):
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


def test_aws_related_tags(handler_with_profile, mock_context, mock_event, monkeypatch):
    ConfigProvider.set(config_names.THUNDRA_APPLICATION_STAGE, 'dev')
    monkeypatch.setitem(os.environ, "_X_AMZN_TRACE_ID", "Root=1-5759e988-bd862e3fe1be46a994272793;Parent=53995c3f42cd8ad8;Sampled=1")
    thundra, handler = handler_with_profile

    invocation_plugin = None
    for plugin in thundra.plugins:
        if isinstance(plugin, InvocationPlugin):
            invocation_plugin = plugin

    try:
        handler(mock_event, mock_context)
    except Exception:
        pass

    assert invocation_plugin.invocation_data['tags']['aws.lambda.arn'] == 'arn:aws:lambda:us-west-2:123456789123:function:test'
    assert invocation_plugin.invocation_data['tags']['aws.account_no'] == '123456789123'
    assert invocation_plugin.invocation_data['tags']['aws.lambda.memory_limit'] == 128
    assert invocation_plugin.invocation_data['tags']['aws.lambda.log_group_name'] == 'log_group_name'
    assert invocation_plugin.invocation_data['tags']['aws.lambda.log_stream_name'] == 'log_stream_name[]id'
    assert invocation_plugin.invocation_data['tags']['aws.lambda.invocation.request_id'] == 'aws_request_id'
    assert invocation_plugin.invocation_data['tags']['aws.xray.trace.id'] == '1-5759e988-bd862e3fe1be46a994272793'
    assert invocation_plugin.invocation_data['tags']['aws.xray.segment.id'] == '53995c3f42cd8ad8'


def test_when_app_stage_exists(handler_with_profile, mock_context, mock_event):
    thundra, handler = handler_with_profile

    invocation_plugin = None
    for plugin in thundra.plugins:
        if isinstance(plugin, InvocationPlugin):
            invocation_plugin = plugin

    handler(mock_event, mock_context)

    assert invocation_plugin.invocation_data['applicationStage'] == 'dev'


def test_when_app_stage_not_exists(handler, mock_context, mock_event):
    thundra, handler = handler

    invocation_plugin = None
    for plugin in thundra.plugins:
        if isinstance(plugin, InvocationPlugin):
            invocation_plugin = plugin

    handler(mock_event, mock_context)

    assert invocation_plugin.invocation_data['applicationStage'] is ''


def test_invocation_support_error_set(handler_with_user_error, mock_context, mock_event):
    ConfigProvider.set(config_names.THUNDRA_APPLICATION_STAGE, 'dev')
    thundra, handler = handler_with_user_error

    invocation_plugin = None
    for plugin in thundra.plugins:
        if isinstance(plugin, InvocationPlugin):
            invocation_plugin = plugin

    handler(mock_event, mock_context)

    assert invocation_plugin.invocation_data['erroneous'] is True
    assert invocation_plugin.invocation_data['errorType'] == 'Exception'
    assert invocation_plugin.invocation_data['errorMessage'] == 'test'