import mock
import pytest

from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.context.execution_context_manager import ExecutionContextManager
from catchpoint.plugins.trace.trace_plugin import TracePlugin
from catchpoint.catchpoint_agent import Catchpoint


def test_if_api_key_is_retrieved_from_env_var():
    ConfigProvider.set(config_names.CATCHPOINT_APIKEY, 'api key')
    catchpoint = Catchpoint()
    assert catchpoint.api_key == 'api key'


def test_if_disable_trace_is_set_to_true():
    catchpoint = Catchpoint('api key', disable_trace=True)

    for plugin in catchpoint.plugins:
        assert not type(plugin) is TracePlugin


def test_if_disable_trace_is_set_to_false():
    catchpoint = Catchpoint('api key', disable_trace=False)

    trace_exist = False
    for plugin in catchpoint.plugins:
        if isinstance(plugin, TracePlugin):
            trace_exist = True

    assert trace_exist is True


def test_if_disable_trace_is_not_set():
    catchpoint = Catchpoint('api key')

    trace_exist = False
    for plugin in catchpoint.plugins:
        if isinstance(plugin, TracePlugin):
            trace_exist = True

    assert trace_exist is True


def test_disable_trace_plugin_from_environment_variable():
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_DISABLE, 'true')
    catchpoint = Catchpoint('api key')

    trace_exist = False
    for plugin in catchpoint.plugins:
        if isinstance(plugin, TracePlugin):
            trace_exist = True

    assert trace_exist is False


def test_enable_trace_plugin_from_environment_variable():
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_DISABLE, 'false')
    catchpoint = Catchpoint('api key')

    trace_exist = False
    for plugin in catchpoint.plugins:
        if isinstance(plugin, TracePlugin):
            trace_exist = True

    assert trace_exist is True


def test_if_disable_trace_plugin_from_environment_variable_is_prior():
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_DISABLE, 'true')
    catchpoint = Catchpoint('api key', disable_trace=False)

    trace_exist = False
    for plugin in catchpoint.plugins:
        if isinstance(plugin, TracePlugin):
            trace_exist = True

    assert trace_exist is False


def test_if_enable_trace_plugin_from_environment_variable_is_prior():
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_DISABLE, 'false')
    catchpoint = Catchpoint('api key', disable_trace=True)

    trace_exist = False
    for plugin in catchpoint.plugins:
        if isinstance(plugin, TracePlugin):
            trace_exist = True

    assert trace_exist is True


@mock.patch('catchpoint.reporter.Reporter')
def test_if_catchpoint_is_disabled(mock_reporter, handler, mock_event, mock_context):
    ConfigProvider.set(config_names.CATCHPOINT_TRACE_DISABLE, 'true')
    _, handler = handler

    handler(mock_event, mock_context)

    assert not mock_reporter.add_report.called
    assert not mock_reporter.send_reports.called


def test_if_exception_is_handled(handler_with_exception, mock_context, mock_event):
    catchpoint, handler = handler_with_exception
    with pytest.raises(Exception):
        handler(mock_event, mock_context)

    assert ExecutionContextManager.get().error


@mock.patch('catchpoint.catchpoint_agent.Catchpoint.check_and_handle_warmup_request')
def test_if_catchpoint_crashes_user_handler_before(mocked_func, handler, mock_event, mock_context):
    mocked_func.side_effect = RuntimeError('Boom!')
    catchpoint, handler = handler
    try:
        handler(mock_event, mock_context)
    except Exception:
        pytest.fail("User's handler shouldn't fail when Catchpoint raise an exception")


@mock.patch('catchpoint.reporter.Reporter.send_reports')
def test_if_catchpoint_crashes_user_handler_after(mocked_func, handler, mock_event, mock_context):
    mocked_func.side_effect = RuntimeError('Boom!')
    catchpoint, handler = handler
    try:
        handler(mock_event, mock_context)
    except Exception:
        pytest.fail("User's handler shouldn't fail when Catchpoint raise an exception")
