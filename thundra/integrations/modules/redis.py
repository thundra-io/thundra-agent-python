"""
botocore patcher module.
"""

from __future__ import absolute_import
import wrapt
from thundra.integrations.modules.generic_wrapper import wrapper
from ..listeners.redis import RedisEventListener
import redis
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
    return wrapper(RedisEventListener, wrapped, instance, args, kwargs)


def patch():
    """
    Patch module.
    :return: None
    """

    disable_redis_integration_by_env = utils.get_configuration(constants.THUNDRA_DISABLE_REDIS_INTEGRATION)
    if not utils.should_disable(disable_redis_integration_by_env):
        methods = [method_name for method_name in dir(redis.client.Redis)
         if callable(getattr(redis.client.Redis, method_name)) and not method_name.__contains__('_')]

        for method in methods:
            wrapt.wrap_function_wrapper(
                'redis.client',
                'Redis.' + method,
                _wrapper
            )
