"""
botocore patcher module.
"""

from __future__ import absolute_import
import wrapt
from thundra.integrations.modules.generic_wrapper import wrapper
from thundra.integrations.botocore import AWSIntegrationFactory
from thundra import utils
from thundra import constants


def _wrapper(wrapped, instance, args, kwargs):
    """
    General wrapper for botocore instrumentation.
    :param wrapped: wrapt's wrapped
    :param instance: wrapt's instance
    :param args: wrapt's args
    :param kwargs: wrapt's kwargs
    :return: None
    """
    return wrapper(AWSIntegrationFactory, wrapped, instance, args, kwargs)


def patch():
    """
    Patch module.
    :return: None
    """
    disable_aws_integration_by_env = utils.get_configuration(constants.THUNDRA_DISABLE_AWS_INTEGRATION)
    if not utils.should_disable(disable_aws_integration_by_env):
        wrapt.wrap_function_wrapper(
            'botocore.client',
            'BaseClient._make_api_call',
            _wrapper
        )
