"""
botocore patcher module.
"""

from __future__ import absolute_import
import wrapt
from thundra import utils
from thundra import constants
from thundra.integrations.base_integration import BaseIntegration
import thundra.integrations.botocore
from thundra.integrations.modules.requests import _wrapper as request_wrapper

INTEGRATIONS = {
    class_obj.CLASS_TYPE: class_obj()
    for class_obj in BaseIntegration.__subclasses__()
}


def _wrapper(wrapped, instance, args, kwargs):
    integration_name = instance.__class__.__name__.lower()
    try:
        response = INTEGRATIONS[integration_name].create_span(
            wrapped,
            instance,
            args,
            kwargs
        )
        return response
    except:
        pass
    return wrapped(*args, **kwargs)


def patch():
    disable_aws_integration_by_env = utils.get_configuration(constants.THUNDRA_DISABLE_AWS_INTEGRATION)
    disable_http_integration_by_env = utils.get_configuration(constants.THUNDRA_DISABLE_HTTP_INTEGRATION)
    if not utils.should_disable(disable_aws_integration_by_env):
        wrapt.wrap_function_wrapper(
            'botocore.client',
            'BaseClient._make_api_call',
            _wrapper
        )
    if not utils.should_disable(disable_http_integration_by_env):
        wrapt.wrap_function_wrapper(
            'botocore.vendored.requests',
            'Session.send',
            request_wrapper
        )
