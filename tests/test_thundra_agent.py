import pytest

from thundra.thundra_agent import Thundra


def test_if_exception_raised_when_api_key_is_not_set():
    with pytest.raises(Exception) as exc:
        thundra = Thundra()
        assert thundra.api_key is None


def test_if_api_key_is_retrieved_from_env_var(environment_variables_with_apikey):
    e_v = environment_variables_with_apikey
    e_v.start()
    thundra = Thundra()
    assert thundra.api_key == 'api key'
    e_v.stop()


def test_if_disable_trace_is_set_to_true():
    thundra = Thundra('api key', disable_trace=True)
    assert len(thundra.plugins) == 0


def test_if_disable_trace_is_set_to_false():
    thundra = Thundra('api key', disable_trace=False)
    assert len(thundra.plugins) > 0


def test_if_disable_trace_is_not_set():
    thundra = Thundra('api key')
    assert len(thundra.plugins) > 0


def test_disable_trace_plugin_from_environment_variable(environment_variables_with_disable_trace_plugin):
    e_v = environment_variables_with_disable_trace_plugin
    e_v.start()
    thundra = Thundra('api key')
    assert len(thundra.plugins) == 0
    e_v.stop()


def test_enable_trace_plugin_from_environment_variable(environment_variables_with_enable_trace_plugin):
    e_v = environment_variables_with_enable_trace_plugin
    e_v.start()
    thundra = Thundra('api key')
    assert len(thundra.plugins) > 0
    e_v.stop()


def test_if_disable_trace_plugin_from_environment_variable_is_prior(environment_variables_with_disable_trace_plugin):
    e_v = environment_variables_with_disable_trace_plugin
    e_v.start()
    thundra = Thundra('api key', disable_trace=False)
    assert len(thundra.plugins) == 0
    e_v.stop()


def test_if_enable_trace_plugin_from_environment_variable_is_prior(environment_variables_with_enable_trace_plugin):
    e_v = environment_variables_with_enable_trace_plugin
    e_v.start()
    thundra = Thundra('api key', disable_trace=True)
    assert len(thundra.plugins) > 0
    e_v.stop()


def test_if_exception_is_handled(handler_with_exception, mock_context, mock_event, environment_variables):
    e_v = environment_variables
    e_v.start()
    thundra, handler = handler_with_exception
    try:
        handler(mock_event, mock_context)
    except Exception as e:
        pass
    assert 'error' in thundra.data
    e_v.stop()





