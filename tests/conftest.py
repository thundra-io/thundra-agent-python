import pytest
import mock
import os

from thundra.thundra_agent import Thundra


class MockContext:
    memory_limit_in_mb = '128'

    def __init__(self, f_name='test_func'):
        self.function_name = f_name


@pytest.fixture
def mock_context():
    return MockContext()


@pytest.fixture
def mock_event():
    event = {
        'message': 'Hello'
    }
    return event


@pytest.fixture()
def mock_report():
    return {
        'apiKey': 'api key',
        'type': 'type',
        'dataFormatVersion': '1.1.1',
        'data': 'data'
    }


@pytest.fixture
def thundra_with_apikey():
    return Thundra('api key')


@pytest.fixture
def handler_with_apikey(thundra_with_apikey):
    @thundra_with_apikey.call
    def _handler(event, context):
        pass

    return thundra_with_apikey, _handler


@pytest.fixture
def thundra():
    return Thundra()


@pytest.fixture
def handler(thundra):
    @thundra.call
    def _handler(event, context):
        pass
    return thundra, _handler


@pytest.fixture
def handler_with_exception(thundra_with_apikey):
    @thundra_with_apikey.call
    def _handler(event, context):
        raise Exception('hello')
    return thundra_with_apikey, _handler


@pytest.fixture
def env_var():
    e_v = {
        'AWS_LAMBDA_LOG_STREAM_NAME': '[]test',
        'AWS_LAMBDA_FUNCTION_VERSION': 'version',
        'AWS_REGION': 'region'
    }
    return e_v


@pytest.fixture
def environment_variables(env_var):
    e_v = mock.patch.dict(os.environ, env_var)
    return e_v


@pytest.fixture
def environment_variables_with_profile(env_var):
    env_var['thundra_applicationProfile'] = 'profile'
    e_v = mock.patch.dict(os.environ, env_var)
    return e_v


@pytest.fixture
def environment_variables_with_apikey(env_var):
    env_var['thundra_apiKey'] = 'api key'
    e_v = mock.patch.dict(os.environ, env_var)
    return e_v


@pytest.fixture
def environment_variables_with_disable_trace_plugin(env_var):
    env_var['thundra_trace_disable'] = 'true'
    e_v = mock.patch.dict(os.environ, env_var)
    return e_v


@pytest.fixture
def environment_variables_with_enable_trace_plugin(env_var):
    env_var['thundra_trace_disable'] = 'false'
    e_v = mock.patch.dict(os.environ, env_var)
    return e_v


@pytest.fixture
def environment_variables_with_enable_async_monitoring(env_var):
    env_var['thundra_lambda_publish_cloudwatch_enable'] = 'true'
    e_v = mock.patch.dict(os.environ, env_var)
    return e_v


@pytest.fixture
def environment_variables_with_disable_async_monitoring(env_var):
    env_var['thundra_lambda_publish_cloudwatch_enable'] = 'false'
    e_v = mock.patch.dict(os.environ, env_var)
    return e_v
