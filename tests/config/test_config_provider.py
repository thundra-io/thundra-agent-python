import os

import pytest

from thundra.config.config_provider import ConfigProvider


@pytest.fixture()
def config_options():
    return {
        'config': {
            'my': {
                'key': 'my-value'
            },
            'lambda': {
                'my': {
                    'key2': 'my-value2'
                }
            },
            'thundra': {
                'agent': {
                    'my': {
                        'key3': 'my-value3'
                    },
                    'lambda': {
                        'my': {
                            'key4': 'my-value4'
                        }
                    }
                }
            }
        }
    }


@pytest.fixture()
def options_with_different_type():
    return {
        'config': {
            'thundra': {
                'agent': {
                    'application': {
                        'className': 'TEST'
                    },
                    'debug': {
                        'enable': True
                    },
                    'lambda': {
                        'debugger.broker.port': 444
                    }
                }
            }
        }
    }


def test_config_from_environment_variable(monkeypatch):
    monkeypatch.setitem(os.environ, 'THUNDRA_AGENT_TEST_KEY', 'test_value')
    monkeypatch.setitem(os.environ, 'THUNDRA_AGENT_LAMBDA_TEST_KEY2', 'test_value2')

    ConfigProvider.__init__()
    monkeypatch.delitem(os.environ, 'THUNDRA_AGENT_TEST_KEY')
    monkeypatch.delitem(os.environ, 'THUNDRA_AGENT_LAMBDA_TEST_KEY2')

    assert ConfigProvider.get('thundra.agent.test.key') == 'test_value'
    assert ConfigProvider.get('thundra.agent.lambda.test.key2') == 'test_value2'

    assert ConfigProvider.get('THUNDRA_AGENT_TEST_KEY') is None
    assert ConfigProvider.get('THUNDRA_AGENT_LAMBDA_TEST_KEY2') is None


def test_config_from_options(config_options):
    ConfigProvider.__init__(options=config_options)

    assert ConfigProvider.get('thundra.agent.my.key') == 'my-value'
    assert ConfigProvider.get('thundra.agent.lambda.my.key2') == 'my-value2'
    assert ConfigProvider.get('thundra.agent.my.key3') == 'my-value3'
    assert ConfigProvider.get('thundra.agent.lambda.my.key4') == 'my-value4'

    assert ConfigProvider.get('thundra.agent.my.key2') == 'my-value2'
    assert ConfigProvider.get('thundra.agent.my.key4') == 'my-value4'

    assert ConfigProvider.get('thundra.agent.my.key5') is None


def test_config_environment_variable_override_options(monkeypatch, config_options):
    monkeypatch.setitem(os.environ, 'THUNDRA_AGENT_MY_KEY', 'my_value_from_env')
    monkeypatch.setitem(os.environ, 'THUNDRA_AGENT_LAMBDA_MY_KEY2', 'my_value_from_env2')

    ConfigProvider.__init__(options=config_options)

    assert ConfigProvider.get('thundra.agent.my.key') == 'my_value_from_env'
    assert ConfigProvider.get('thundra.agent.lambda.my.key2') == 'my_value_from_env2'
    assert ConfigProvider.get('thundra.agent.my.key2') == 'my_value_from_env2'


def test_config_variable_correct_type(monkeypatch, options_with_different_type):
    monkeypatch.setitem(os.environ, 'thundra_agent_lambda_debugger_port', '3000')
    monkeypatch.setitem(os.environ, 'thundra_agent_trace_integrations_aws_dynamodb_traceInjection_enable', 'true')

    ConfigProvider.__init__(options=options_with_different_type)

    assert ConfigProvider.get('thundra.agent.lambda.debugger.port') == 3000
    assert ConfigProvider.get('thundra.agent.trace.integrations.aws.dynamodb.traceinjection.enable') is True

    assert ConfigProvider.get('thundra.agent.lambda.debugger.broker.port') == 444
    assert ConfigProvider.get('thundra.agent.application.classname') == 'TEST'
    assert ConfigProvider.get('thundra.agent.debug.enable') is True


def test_config_correct_default_value():
    ConfigProvider.__init__()

    assert ConfigProvider.get('thundra.agent.debug.enable') is False
    assert ConfigProvider.get('thundra.agent.debug.enable', True) is True
    assert ConfigProvider.get('thundra.agent.lambda.debugger.logs.enable') is False
