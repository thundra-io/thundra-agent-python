"""
botocore patcher module.
"""

from __future__ import absolute_import
import wrapt
from thundra import utils
from thundra import constants
from thundra.integrations.botocore import AWSIntegrationFactory


def _wrapper(wrapped, instance, args, kwargs):
    response = AWSIntegrationFactory.create_span(
        wrapped,
        instance,
        args,
        kwargs
    )

    return response


def patch():
    disable_aws_integration_by_env = utils.get_configuration(constants.THUNDRA_DISABLE_AWS_INTEGRATION)
    if not utils.should_disable(disable_aws_integration_by_env):
        wrapt.wrap_function_wrapper(
            'botocore.client',
            'BaseClient._make_api_call',
            _wrapper
        )
