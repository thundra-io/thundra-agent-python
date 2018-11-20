"""
botocore patcher module.
"""

from __future__ import absolute_import
import wrapt
from thundra.integrations.modules.generic_wrapper import wrapper
from ..listeners.botocore import AWSEventListeners


def _wrapper(wrapped, instance, args, kwargs):
    """
    General wrapper for botocore instrumentation.
    :param wrapped: wrapt's wrapped
    :param instance: wrapt's instance
    :param args: wrapt's args
    :param kwargs: wrapt's kwargs
    :return: None
    """
    return wrapper(AWSEventListeners, wrapped, instance, args, kwargs)


def patch():
    """
    Patch module.
    :return: None
    """
    wrapt.wrap_function_wrapper(
        'botocore.client',
        'BaseClient._make_api_call',
        _wrapper
    )
