import wrapt
from thundra import constants
from thundra.integrations.redis import RedisIntegration
from thundra.config import utils as config_utils

redis_integration = RedisIntegration()


def _wrapper(wrapped, instance, args, kwargs):
    return redis_integration.run_and_trace(
        wrapped,
        instance,
        args,
        kwargs
    )


def patch():
    if not config_utils.get_bool_property(constants.THUNDRA_DISABLE_REDIS_INTEGRATION):
        for method in map(str.lower, constants.RedisCommandTypes.keys()):
            try:
                wrapt.wrap_function_wrapper(
                    'redis.client',
                    'Redis.' + method,
                    _wrapper
                )
            except:
                pass
