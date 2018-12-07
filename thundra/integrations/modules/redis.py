from __future__ import absolute_import
import wrapt
from thundra import utils
from thundra import constants
from thundra.integrations.redis import RedisIntegration

redis_integration = RedisIntegration()
def _wrapper(wrapped, instance, args, kwargs):
    response = redis_integration.create_span(
        wrapped,
        instance,
        args,
        kwargs
    )
    return response


def patch():
    disable_redis_integration_by_env = utils.get_configuration(constants.THUNDRA_DISABLE_REDIS_INTEGRATION)
    if not utils.should_disable(disable_redis_integration_by_env):
        for method in map(str.lower, constants.RedisCommandTypes.keys()):
            try:
                wrapt.wrap_function_wrapper(
                    'redis.client',
                    'Redis.' + method,
                    _wrapper
                )
            except:
                pass
