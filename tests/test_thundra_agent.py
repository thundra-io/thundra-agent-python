import os

import mock
import pytest
from thundra import constants
from thundra.plugins.trace.trace_plugin import TracePlugin
from thundra.thundra_agent import Thundra


def test_if_api_key_is_retrieved_from_env_var(monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_APIKEY, 'api key')
    thundra = Thundra()
    assert thundra.api_key == 'api key'


def test_if_disable_trace_is_set_to_true():
    thundra = Thundra('api key', disable_trace=True)

    for plugin in thundra.plugins:
        assert not type(plugin) is TracePlugin


def test_if_disable_trace_is_set_to_false():
    thundra = Thundra('api key', disable_trace=False)

    trace_exist = False
    for plugin in thundra.plugins:
        if isinstance(plugin, TracePlugin):
            trace_exist = True

    assert trace_exist is True


def test_if_disable_trace_is_not_set():
    thundra = Thundra('api key')

    trace_exist = False
    for plugin in thundra.plugins:
        if isinstance(plugin, TracePlugin):
            trace_exist = True

    assert trace_exist is True


def test_disable_trace_plugin_from_environment_variable(monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_DISABLE_TRACE, 'true')
    thundra = Thundra('api key')

    trace_exist = False
    for plugin in thundra.plugins:
        if isinstance(plugin, TracePlugin):
            trace_exist = True

    assert trace_exist is False


def test_enable_trace_plugin_from_environment_variable(monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_DISABLE_TRACE, 'false')
    thundra = Thundra('api key')

    trace_exist = False
    for plugin in thundra.plugins:
        if isinstance(plugin, TracePlugin):
            trace_exist = True

    assert trace_exist is True


def test_if_disable_trace_plugin_from_environment_variable_is_prior(monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_DISABLE_TRACE, 'true')
    thundra = Thundra('api key', disable_trace=False)

    trace_exist = False
    for plugin in thundra.plugins:
        if isinstance(plugin, TracePlugin):
            trace_exist = True

    assert trace_exist is False


def test_if_enable_trace_plugin_from_environment_variable_is_prior(monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_DISABLE_TRACE, 'false')
    thundra = Thundra('api key', disable_trace=True)

    trace_exist = False
    for plugin in thundra.plugins:
        if isinstance(plugin, TracePlugin):
            trace_exist = True

    assert trace_exist is True


@mock.patch('thundra.reporter.Reporter')
def test_if_thundra_is_disabled(mock_reporter, monkeypatch, handler, mock_event, mock_context):
    monkeypatch.setitem(os.environ, constants.THUNDRA_DISABLE, 'true')

    thundra, handler = handler

    handler(mock_event, mock_context)

    assert not mock_reporter.add_report.called
    assert not mock_reporter.send_report.called


def test_if_exception_is_handled(handler_with_exception, mock_context, mock_event):
    thundra, handler = handler_with_exception
    with pytest.raises(Exception) as exinfo:
        handler(mock_event, mock_context)

    assert 'error' in thundra.plugin_context


@mock.patch('thundra.thundra_agent.Thundra.check_and_handle_warmup_request')
def test_if_thundra_crashes_user_handler_before(mocked_func, handler, mock_event, mock_context):
    mocked_func.side_effect = RuntimeError('Boom!')
    thundra, handler = handler
    try:
        handler(mock_event, mock_context)
    except Exception:
        pytest.fail("User's handler shouldn't fail when Thundra raise an exception")

    assert len(thundra.reporter.reports) == 0


@mock.patch('thundra.reporter.Reporter.send_report')
def test_if_thundra_crashes_user_handler_after(mocked_func, handler, mock_event, mock_context):
    mocked_func.side_effect = RuntimeError('Boom!')
    thundra, handler = handler
    try:
        handler(mock_event, mock_context)
    except Exception:
        pytest.fail("User's handler shouldn't fail when Thundra raise an exception")

    assert len(thundra.reporter.reports) == 0
