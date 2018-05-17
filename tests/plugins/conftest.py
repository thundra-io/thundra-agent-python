import os
import pytest
from mock import mock

from thundra import constants
from thundra.thundra_agent import Thundra

@pytest.fixture
def environment_variables_with_profile(env_var):
    env_var[constants.THUNDRA_APPLICATION_PROFILE] = 'profile'
    e_v = mock.patch.dict(os.environ, env_var)
    return e_v


@pytest.fixture
def thundra_with_profile(environment_variables_with_profile):
    e_v = environment_variables_with_profile
    e_v.start()
    thundra = Thundra('api key', disable_metric=True)
    e_v.stop()
    return thundra


@pytest.fixture
def handler_with_profile(thundra_with_profile):
    @thundra_with_profile.call
    def _handler(event, context):
        pass
    return thundra_with_profile, _handler


@pytest.fixture
def environment_variables_with_request_response_skip(env_var):
    env_var[constants.THUNDRA_LAMBDA_TRACE_REQUEST_SKIP] = 'true'
    env_var[constants.THUNDRA_LAMBDA_TRACE_RESPONSE_SKIP] = 'true'
    e_v = mock.patch.dict(os.environ, env_var)
    return e_v


@pytest.fixture
def thundra_with_request_response_skip(environment_variables_with_request_response_skip):
    e_v = environment_variables_with_request_response_skip
    e_v.start()
    thundra = Thundra('api key', disable_metric=True)
    e_v.stop()
    return thundra


@pytest.fixture
def handler_with_request_response_skip(thundra_with_request_response_skip):
    @thundra_with_request_response_skip.call
    def _handler(event, context):
        pass
    return thundra_with_request_response_skip, _handler


